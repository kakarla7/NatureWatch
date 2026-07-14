"""
NatureWatch — Wildlife Data Refresh Script
Runs on the 1st and 15th of every month via GitHub Actions.
Makes 5 Claude API calls (one per category) and merges into wildlife_data.json.
"""

import json
import os
import sys
from datetime import datetime
import anthropic

# ── CONFIG ──────────────────────────────────────────────────────────────────
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/wildlife_data.json")
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000

CATEGORIES = [
    {
        "key": "mammals",
        "label": "Mammal",
        "count": 25,
        "examples": "bears, wolves, bison, elk, moose, mountain lions, wolverines, pronghorn, bighorn sheep, manatees, whales, dolphins, sea otters, beavers, foxes"
    },
    {
        "key": "birds",
        "label": "Bird",
        "count": 20,
        "examples": "bald eagles, California condors, trumpeter swans, whooping cranes, great blue herons, puffins, sandhill cranes, snowy owls, roseate spoonbills, roadrunners"
    },
    {
        "key": "marine",
        "label": "Marine",
        "count": 15,
        "examples": "harbor seals, sea lions, humpback whales, gray whales, orcas, manatees, sea turtles, whale sharks, manta rays, dolphins, walruses"
    },
    {
        "key": "reptiles",
        "label": "Reptile",
        "count": 10,
        "examples": "American alligators, American crocodiles, Gila monsters, Komodo-like monitors, sea turtles, gopher tortoises, rattlesnakes, green iguanas in Florida"
    },
    {
        "key": "insects",
        "label": "Insect",
        "count": 10,
        "examples": "monarch butterflies, fireflies, giant swallowtails, American bumble bees, luna moths, periodical cicadas, dragonflies, walking sticks"
    },
]

PROMPT_TEMPLATE = """Generate a US wildlife viewing guide dataset for NatureWatch — category: {label}.
Return ONLY valid JSON — no markdown, no backticks, no explanation.

Include exactly {count} diverse {label} species viewable in the wild in the US.
Focus on animals people actually travel to see. Examples to draw from: {examples}
Do NOT repeat animals from other categories. All must be found wild in the US.

Return this exact JSON structure:
{{
  "animals": [
    {{
      "id": "kebab-case-unique-id",
      "name": "Common Name",
      "emoji": "single relevant emoji",
      "category": "{label}",
      "parks": ["Park Name NP", "Park Name NWR"],
      "states": ["XX", "XX"],
      "best_months": ["January", "February"],
      "best_time": "Dawn & Dusk|Early Morning|Morning|Midday|Dusk|Anytime",
      "temps": {{
        "MonthName": "XX–XX°F"
      }},
      "weather": {{
        "MonthName": "emoji (use ☀️⛅🌤🌧❄️🌨🌦🍂)"
      }},
      "behavior_notes": "1-2 sentences on behavior during best months",
      "viewing_tips": "1-2 sentences of practical viewing advice",
      "nps_source": "https://www.nps.gov/real-path",
      "confidence": "High|Medium|Low"
    }}
  ]
}}

Rules:
- temps and weather keys must exactly match best_months values
- nps_source must be a plausible real nps.gov URL
- confidence: High = easily spotted, Medium = requires effort, Low = rare/elusive
- Cover a wide geographic spread — Northeast, Southeast, Midwest, Southwest, Northwest, Alaska, Hawaii
- CRITICAL: states[] must be the actual US state codes where this animal is found in the wild
  Examples: Acadia NP is in ME not OH. Yellowstone is in WY MT ID. Everglades is in FL only.
  Double-check every state code — wrong states break the map filter feature.
- parks[] and states[] must be consistent — every park must be in one of the listed states
- Return ONLY the JSON object, nothing else"""


# ── HELPERS ─────────────────────────────────────────────────────────────────

def get_next_refresh():
    today = datetime.now()
    if today.day < 15:
        next_date = today.replace(day=15)
    else:
        if today.month == 12:
            next_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_date = today.replace(month=today.month + 1, day=1)
    return next_date.strftime("%Y-%m-%d")


def clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


# Known park → state mappings for validation
PARK_STATES = {
    "Yellowstone NP": ["WY", "MT", "ID"],
    "Grand Teton NP": ["WY"],
    "Glacier NP": ["MT"],
    "Everglades NP": ["FL"],
    "Biscayne NP": ["FL"],
    "Big Cypress NP": ["FL"],
    "Acadia NP": ["ME"],
    "Grand Canyon NP": ["AZ"],
    "Zion NP": ["UT"],
    "Bryce Canyon NP": ["UT"],
    "Rocky Mountain NP": ["CO"],
    "Olympic NP": ["WA"],
    "North Cascades NP": ["WA"],
    "Mount Rainier NP": ["WA"],
    "Crater Lake NP": ["OR"],
    "Redwood NP": ["CA"],
    "Yosemite NP": ["CA"],
    "Sequoia NP": ["CA"],
    "Channel Islands NP": ["CA"],
    "Death Valley NP": ["CA", "NV"],
    "Joshua Tree NP": ["CA"],
    "Pinnacles NP": ["CA"],
    "Great Smoky Mountains NP": ["TN", "NC"],
    "Shenandoah NP": ["VA"],
    "Badlands NP": ["SD"],
    "Wind Cave NP": ["SD"],
    "Isle Royale NP": ["MI"],
    "Kenai Fjords NP": ["AK"],
    "Denali NP": ["AK"],
    "Wrangell-St. Elias NP": ["AK"],
    "Hawaii Volcanoes NP": ["HI"],
    "Haleakalā NP": ["HI"],
    "Congaree NP": ["SC"],
    "Cuyahoga Valley NP": ["OH"],
}

def validate_animal(animal: dict) -> list:
    errors = []
    required = ["id", "name", "emoji", "category", "parks", "states",
                "best_months", "best_time", "temps", "weather",
                "behavior_notes", "viewing_tips", "nps_source", "confidence"]
    for field in required:
        if field not in animal:
            errors.append(f"Missing: {field}")
    if "best_months" in animal and "temps" in animal:
        for m in animal["best_months"]:
            if m not in animal["temps"]:
                errors.append(f"Missing temp for {m}")
    if "best_months" in animal and "weather" in animal:
        for m in animal["best_months"]:
            if m not in animal["weather"]:
                errors.append(f"Missing weather for {m}")
    # Validate park/state consistency
    if "parks" in animal and "states" in animal:
        for park in animal["parks"]:
            if park in PARK_STATES:
                valid_states = PARK_STATES[park]
                if not any(s in animal["states"] for s in valid_states):
                    errors.append(f"Park/state mismatch: {park} should be in {valid_states} but states={animal['states']}")
    return errors


def fetch_category(client, category: dict) -> list:
    label   = category["label"]
    count   = category["count"]
    examples = category["examples"]

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching {count} {label}s...")

    prompt = PROMPT_TEMPLATE.format(
        label=label,
        count=count,
        examples=examples
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        print(f"  ERROR: API call failed for {label}: {e}", file=sys.stderr)
        return []

    raw = response.content[0].text
    print(f"  Received {len(raw)} characters")

    cleaned = clean_json(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"  ERROR: JSON parse failed for {label}: {e}", file=sys.stderr)
        print(f"  First 300 chars: {raw[:300]}", file=sys.stderr)
        return []

    animals = data.get("animals", [])
    print(f"  Parsed {len(animals)} {label}s")

    # Validate
    error_count = 0
    for animal in animals:
        errs = validate_animal(animal)
        if errs:
            error_count += 1
            print(f"  WARN {animal.get('name','?')}: {', '.join(errs)}")

    if error_count:
        print(f"  {error_count} animals had validation warnings (still included)")

    return animals


# ── MAIN ────────────────────────────────────────────────────────────────────

def run_refresh():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    all_animals = []
    all_ids = set()

    for category in CATEGORIES:
        animals = fetch_category(client, category)

        # Deduplicate across categories by id
        unique = []
        for a in animals:
            if a.get("id") and a["id"] not in all_ids:
                all_ids.add(a["id"])
                unique.append(a)
            elif a.get("id") in all_ids:
                print(f"  Skipping duplicate id: {a['id']}")

        all_animals.extend(unique)
        print(f"  Running total: {len(all_animals)} animals")

    if not all_animals:
        print("ERROR: No animals fetched — aborting to preserve existing data", file=sys.stderr)
        sys.exit(1)

    today = datetime.now()
    output = {
        "generated_at": today.strftime("%Y-%m-%d"),
        "next_refresh": get_next_refresh(),
        "total": len(all_animals),
        "animals": all_animals
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done — {len(all_animals)} animals written to {OUTPUT_PATH}")
    print(f"   Generated: {output['generated_at']}")
    print(f"   Next refresh: {output['next_refresh']}")

    # Print category breakdown
    from collections import Counter
    counts = Counter(a.get("category","?") for a in all_animals)
    for cat, n in sorted(counts.items()):
        print(f"   {cat}: {n}")


if __name__ == "__main__":
    run_refresh()