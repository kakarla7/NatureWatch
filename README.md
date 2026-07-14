# 🌿 NatureWatch

**US Nature & Sky Guide** — Discover where and when to spot wildlife, sky events, and natural phenomena across America's national parks.

Live: [naturewatch on GitHub Pages](https://kakarla7.github.io/NatureWatch)

---

## Phases

| Phase | Category | Status | Data |
|---|---|---|---|
| 1 | 🐾 Wildlife | ✅ Live | LLM call, bi-monthly refresh |
| 2 | 🌌 Sky Events | 🔜 Coming | NOAA + NASA APIs |
| 3 | 🌸 Seasonal | 🔜 Coming | iNaturalist + live APIs |
| 4 | 🌊 Water & Earth | 🔜 Coming | USGS + NOAA APIs |

---

## How it works

### Wildlife data (Phase 1)
- `data/wildlife_data.json` — static file served with the site
- Refreshed on the **1st and 15th of every month** via GitHub Actions
- Refresh = one Claude API call that regenerates the full JSON
- HTML loads the JSON on page load — no backend needed

### Scheduled refresh
GitHub Actions (`.github/workflows/refresh.yml`) runs `scripts/refresh_wildlife.py` on schedule, commits the new `wildlife_data.json`, and GitHub Pages auto-deploys.

### Animal request form
Users can request animals not yet in the database via Google Form. Requests are reviewed before each bi-monthly refresh.

---

## Setup

### 1. Fork / clone this repo
```bash
git clone https://github.com/kakarla7/NatureWatch.git
cd NatureWatch
```

### 2. Add your Anthropic API key
Go to **Settings → Secrets → Actions** in your GitHub repo and add:
```
ANTHROPIC_API_KEY = sk-ant-...
```

### 3. Enable GitHub Pages
Go to **Settings → Pages** → Source: `Deploy from branch` → Branch: `main` → Folder: `/ (root)`

### 4. Wire up the Google Form
Replace `GOOGLE_FORM_URL` in `index.html` (two places) with your actual Google Form URL.

### 5. Test the refresh script locally
```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/refresh_wildlife.py
```

### 6. Trigger a manual refresh
Go to **Actions → Refresh Wildlife Data → Run workflow**

---

## File structure

```
NatureWatch/
├── index.html                        # Main app (single file)
├── data/
│   └── wildlife_data.json            # Generated wildlife data
├── scripts/
│   └── refresh_wildlife.py           # LLM refresh script
├── .github/
│   └── workflows/
│       └── refresh.yml               # GitHub Actions scheduler
└── README.md
```

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | HTML + CSS + Vanilla JS |
| Hosting | GitHub Pages (free) |
| Data | Static JSON |
| AI | Anthropic Claude API (`claude-sonnet-4-6`) |
| Scheduler | GitHub Actions |
| Requests | Google Forms → Google Sheets |

---

## Future: TripCraft integration
NatureWatch will eventually expose its data as an API consumed by [TripCraft](https://tripcraft.streamlit.app) — wildlife and nature events will be woven into AI-generated trip itineraries.
