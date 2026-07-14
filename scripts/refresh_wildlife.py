"""
NatureWatch — Wildlife Data Refresh Script
Runs on the 1st and 15th of every month via GitHub Actions.
Calls Claude API to regenerate wildlife_data.json with fresh data.
"""

import json
import os
import sys
from datetime import datetime, timedelta
import anthropic

# ── CONFIG ──────────────────────────────────────────────────────────────────
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/wildlife_data.json")
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000

PROMPT = """Generate a comprehensive US wildlife viewing guide dataset for NatureWatch.
Return ONLY valid JSON — no markdown, no backticks, no explanation.

Include exactly 20 diverse animals across these categories: Mammal, Bird, Marine, Reptile, Insect.
Cover a wide geographic spread across US national parks and wildlife refuges.

Return this exact JSON structure:
{
  "animals": [
    {
      "id": "kebab-case-id",
      "name": "Common Name",
      "emoji": "single relevant emoji",
      "category": "Mammal|Bird|Marine|Reptile|Insect",
      "parks": ["Park Name NP", "Park Name NP"],
      "states": ["XX", "XX"],
      "best_months": ["January", "February"],
      "best_time": "Dawn & Dusk|Early Morning|Morning|Midday|Dusk|Anytime",
      "temps": {
        "MonthName": "XX–XX°F"
      },
      "weather": {
        "MonthName": "emoji (use ☀️⛅🌤🌧❄️🌨🌦🍂)"
      },
      "behavior_notes": "1-2 sentences on behavior during best months",
      "viewing_tips": "1-2 sentences of practical advice",
      "nps_source": "https://www.nps.gov/real-url",
      "confidence": "High|Medium|Low"
    }
  ]
}

Rules:
- temps and weather keys must match best_months exactly
- Include at least 3 marine animals, 3 birds, 1 insect, rest mammals
- Include at least one animal per region: Northeast, Southeast, Midwest, Southwest, Northwest, Alaska
- NPS source URLs must be real nps.gov URLs
- confidence: High = easily spotted, Medium = requires effort, Low = rare/elusive
- Do not include any animal not found wild in the US
- Return ONLY the JSON object, nothing else"""

# ── HELPERS ─────────────────────────────────────────────────────────────────

def get_next_refresh():
    today = datetime.now()
    if today.day < 15:
        next_date = today.replace(day=15)
    else:
        # First of next month
        if today.month == 12:
            next_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_date = today.replace(month=today.month + 1, day=1)
    return next_date.strftime("%Y-%m-%d")


def clean_json_response(text: str) -> str:
    """Strip any accidental markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


def validate_animal(animal: dict) -> list[str]:
    """Return list of validation errors for an animal entry."""
    errors = []
    required = ["id", "name", "emoji", "category", "parks", "states",
                 "best_months", "best_time", "temps", "weather",
                 "behavior_notes", "viewing_tips", "nps_source", "confidence"]
    for field in required:
        if field not in animal:
            errors.append(f"Missing field: {field}")

    if "best_months" in animal and "temps" in animal:
        for month in animal["best_months"]:
            if month not in animal["temps"]:
                errors.append(f"Missing temp for month: {month}")
    if "best_months" in animal and "weather" in animal:
        for month in animal["best_months"]:
            if month not in animal["weather"]:
                errors.append(f"Missing weather for month: {month}")

    valid_categories = ["Mammal", "Bird", "Marine", "Reptile", "Insect"]
    if animal.get("category") not in valid_categories:
        errors.append(f"Invalid category: {animal.get('category')}")

    valid_times = ["Dawn & Dusk", "Early Morning", "Morning", "Midday", "Dusk", "Anytime"]
    if animal.get("best_time") not in valid_times:
        errors.append(f"Invalid best_time: {animal.get('best_time')}")

    valid_confidence = ["High", "Medium", "Low"]
    if animal.get("confidence") not in valid_confidence:
        errors.append(f"Invalid confidence: {animal.get('confidence')}")

    return errors


# ── MAIN ────────────────────────────────────────────────────────────────────

def run_refresh():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"[{datetime.now().isoformat()}] Calling Claude API...")

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": PROMPT}]
        )
    except Exception as e:
        print(f"ERROR: Claude API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    raw = response.content[0].text
    print(f"Received {len(raw)} characters from Claude")

    # Parse JSON
    cleaned = clean_json_response(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse failed: {e}", file=sys.stderr)
        print("Raw response (first 500 chars):", raw[:500], file=sys.stderr)
        sys.exit(1)

    animals = data.get("animals", [])
    print(f"Parsed {len(animals)} animals")

    # Validate
    all_errors = []
    for i, animal in enumerate(animals):
        errors = validate_animal(animal)
        if errors:
            name = animal.get("name", f"animal[{i}]")
            for err in errors:
                all_errors.append(f"  {name}: {err}")

    if all_errors:
        print(f"WARNING: {len(all_errors)} validation issue(s):")
        for err in all_errors:
            print(err)
        # Don't fail — partial data is still useful

    # Build final output
    today = datetime.now()
    output = {
        "generated_at": today.strftime("%Y-%m-%d"),
        "next_refresh": get_next_refresh(),
        "total": len(animals),
        "animals": animals
    }

    # Write to file
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Written {len(animals)} animals to {OUTPUT_PATH}")
    print(f"   Generated: {output['generated_at']}")
    print(f"   Next refresh: {output['next_refresh']}")


if __name__ == "__main__":
    run_refresh()