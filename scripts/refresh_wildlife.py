"""
NatureWatch — Wildlife Data Refresh Script
Runs on the 1st and 15th of every month via GitHub Actions.

Uses master_list.py as the source of truth for which animals to include.
Batches animals into groups of 10, one API call per batch.
Merges all results into wildlife_data.json.
"""

import json
import os
import sys
from datetime import datetime
from math import ceil
import anthropic
from master_list import MASTER_LIST, ALL_ANIMALS

# ── CONFIG ───────────────────────────────────────────────────────────────────
OUTPUT_PATH   = os.path.join(os.path.dirname(__file__), "../data/wildlife_data.json")
MODEL         = "claude-sonnet-4-6"
MAX_TOKENS    = 8000
BATCH_SIZE    = 10   # animals per API call

# Known park → valid state codes (for validation)
PARK_STATES = {
    "Yellowstone NP": ["WY","MT","ID"],
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
    "Death Valley NP": ["CA","NV"],
    "Joshua Tree NP": ["CA"],
    "Pinnacles NP": ["CA"],
    "Great Smoky Mountains NP": ["TN","NC"],
    "Shenandoah NP": ["VA"],
    "Badlands NP": ["SD"],
    "Wind Cave NP": ["SD"],
    "Isle Royale NP": ["MI"],
    "Kenai Fjords NP": ["AK"],
    "Denali NP": ["AK"],
    "Wrangell-St. Elias NP": ["AK"],
    "Hawaii Volcanoes NP": ["HI"],
    "Haleakala NP": ["HI"],
    "Congaree NP": ["SC"],
    "Cuyahoga Valley NP": ["OH"],
}

PROMPT_TEMPLATE = """You are generating wildlife viewing data for NatureWatch, a US nature guide app.

Generate viewing data for EXACTLY these {count} specific animals:
{animal_list}

Return ONLY valid JSON — no markdown, no backticks, no explanation before or after.

Use this exact structure:
{{
  "animals": [
    {{
      "id": "kebab-case-unique-id",
      "name": "Exact animal name as given above",
      "emoji": "single most relevant emoji",
      "category": "{category}",
      "parks": ["Most relevant viewing location NP/NWR/SP"],
      "states": ["XX"],
      "best_months": ["January"],
      "best_time": "Dawn & Dusk|Early Morning|Morning|Midday|Dusk|Anytime",
      "temps": {{ "MonthName": "XX–XX°F" }},
      "weather": {{ "MonthName": "☀️ or ⛅ or 🌤 or 🌧 or ❄️ or 🌨 or 🌦 or 🍂" }},
      "behavior_notes": "1-2 sentences on behavior during best viewing months",
      "viewing_tips": "1-2 sentences of practical advice for actually seeing this animal",
      "nps_source": "https://www.nps.gov/real-path-to-species-page",
      "confidence": "High|Medium|Low"
    }}
  ]
}}

CRITICAL RULES:
- Include ALL {count} animals listed — do not skip any
- states[] must be accurate US state codes where this animal actually lives wild
  Acadia NP = ME, Yellowstone = WY/MT/ID, Everglades = FL, Grand Canyon = AZ
- parks[] and states[] must match — every park must be in a listed state
- temps and weather keys must exactly match best_months
- confidence: High=easily spotted, Medium=requires effort, Low=rare/elusive/endangered
- For extinct or zoo-only animals, set confidence=Low and note in viewing_tips
- Return ONLY the JSON, nothing else"""


# ── HELPERS ──────────────────────────────────────────────────────────────────

def get_next_refresh():
    today = datetime.now()
    if today.day < 15:
        return today.replace(day=15).strftime("%Y-%m-%d")
    if today.month == 12:
        return today.replace(year=today.year+1, month=1, day=1).strftime("%Y-%m-%d")
    return today.replace(month=today.month+1, day=1).strftime("%Y-%m-%d")


def clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


def validate_animal(animal: dict) -> list:
    errors = []
    required = ["id","name","emoji","category","parks","states",
                "best_months","best_time","temps","weather",
                "behavior_notes","viewing_tips","nps_source","confidence"]
    for f in required:
        if f not in animal:
            errors.append(f"Missing: {f}")
    for m in animal.get("best_months", []):
        if m not in animal.get("temps", {}):
            errors.append(f"Missing temp: {m}")
        if m not in animal.get("weather", {}):
            errors.append(f"Missing weather: {m}")
    for park in animal.get("parks", []):
        if park in PARK_STATES:
            valid = PARK_STATES[park]
            if not any(s in animal.get("states", []) for s in valid):
                errors.append(f"Park/state mismatch: {park} needs {valid}")
    return errors


def fetch_batch(client, animals: list, category: str, batch_num: int, total_batches: int) -> list:
    names = [a["name"] for a in animals]
    animal_list = "\n".join(f"- {n}" for n in names)

    print(f"  Batch {batch_num}/{total_batches}: {', '.join(names[:3])}{'...' if len(names)>3 else ''}")

    prompt = PROMPT_TEMPLATE.format(
        count=len(animals),
        animal_list=animal_list,
        category=category
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        print(f"    ERROR: API call failed: {e}", file=sys.stderr)
        return []

    raw = response.content[0].text
    cleaned = clean_json(raw)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"    ERROR: JSON parse failed: {e}", file=sys.stderr)
        print(f"    First 200 chars: {raw[:200]}", file=sys.stderr)
        return []

    result = data.get("animals", [])
    print(f"    Got {len(result)}/{len(animals)} animals")

    # Validate
    for animal in result:
        errs = validate_animal(animal)
        if errs:
            print(f"    WARN {animal.get('name','?')}: {'; '.join(errs)}")

    return result


# ── MAIN ─────────────────────────────────────────────────────────────────────

def run_refresh():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    all_animals = []
    all_ids = set()

    total = len(ALL_ANIMALS)
    print(f"[{datetime.now().isoformat()}] Starting refresh")
    print(f"Master list: {total} animals across {len(MASTER_LIST)} categories")

    for category, animals_in_cat in MASTER_LIST.items():
        cat_animals = [{"name": n, "category": category} for n in animals_in_cat]
        batches = [cat_animals[i:i+BATCH_SIZE] for i in range(0, len(cat_animals), BATCH_SIZE)]
        total_batches = len(batches)

        print(f"\n── {category} ({len(cat_animals)} animals, {total_batches} batches) ──")

        for i, batch in enumerate(batches, 1):
            results = fetch_batch(client, batch, category, i, total_batches)

            for animal in results:
                aid = animal.get("id")
                if aid and aid not in all_ids:
                    all_ids.add(aid)
                    all_animals.append(animal)
                elif aid in all_ids:
                    # Try to make ID unique
                    animal["id"] = f"{aid}-{category.lower().replace(' ','-')}"
                    all_ids.add(animal["id"])
                    all_animals.append(animal)

        print(f"  Running total: {len(all_animals)} animals")

    if not all_animals:
        print("ERROR: No animals fetched — aborting", file=sys.stderr)
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
    print(f"   Generated: {output['generated_at']} | Next: {output['next_refresh']}")

    from collections import Counter
    counts = Counter(a.get("category","?") for a in all_animals)
    for cat, n in sorted(counts.items()):
        expected = len(MASTER_LIST.get(cat, []))
        status = "✅" if n == expected else f"⚠️  (expected {expected})"
        print(f"   {cat}: {n} {status}")


if __name__ == "__main__":
    run_refresh()