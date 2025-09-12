# Red Deer Toyota Poster Site

This is a single-page React app that displays used inventory scraped from reddeertoyota.com and lets you generate a printable A4 poster PDF per vehicle.

## Quick start

1) Install frontend deps
```sh
npm install
```

2) Install Python deps
```sh
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

3) Generate inventory
```sh
python3 src/script/toyota_scrapper.py
```

4) Start the app
```sh
npm start
```

Open the URL shown in your terminal. Click “Download PDF” on a vehicle to get a windshield-ready poster.

## Deploying to Vercel with daily updates

1) Import this GitHub repo into Vercel (framework: Create React App)
2) Create a Deploy Hook in your Vercel project (Settings → Deploy Hooks) and copy its URL
3) In your GitHub repo settings, add a secret named `VERCEL_DEPLOY_HOOK_URL` with that URL
4) The workflow at `.github/workflows/daily-scrape.yml` runs daily around 7:00 AM Mountain Time and commits `public/data/inventory.csv` if it changed; it then triggers the Vercel deploy hook

DST handling: the workflow schedules both 13:00 and 14:00 UTC to cover 7:00 AM in MDT/MST.

## Files of interest

- Scraper: `src/script/toyota_scrapper.py` (writes `public/data/inventory.csv`)
- CSV: `public/data/inventory.csv`
- UI: `src/components/VehicleList.js`, `src/components/VehiclePoster.js`
- Styles: `src/App.css`
- CI: `.github/workflows/daily-scrape.yml`

## Build

```sh
npm run build
```

The static site is created in `build/`. Ensure `public/data/inventory.csv` is up to date before building.
