# Local Development Setup (30-45 min)

## 1. Clone / unzip the project
```bash
cd inji-cho
```

## 2. Install dependencies
```bash
npm install
```
This installs Vite, Leaflet, Leaflet.markercluster, and the Supabase JS client.

## 3. Environment variables
```bash
cp .env.example .env.local
```
Edit `.env.local`:
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_USE_SUPABASE=false
```
Leave `VITE_USE_SUPABASE=false` if you just want to run the app against localStorage (no account, no backend needed).

## 4. Start the dev server
```bash
npm run dev
```
Vite will start at `http://localhost:5173` with hot module reload.

## 5. Verify core flows
1. Click "+ Add Temple", fill in a name and coordinates, save.
2. Confirm the torii marker appears on the map.
3. Click the marker popup, try Edit and Delete.
4. Use the filter dropdowns (prefecture/region/status).
5. Export JSON, then re-import it to confirm round-tripping works.
6. Toggle dark mode with the 🌓 button.

## 6. Common issues

**Map tiles don't load**
- Check your network/firewall isn't blocking `tile.openstreetmap.org`.

**Markers don't cluster**
- Confirm `leaflet.markercluster` installed correctly (`node_modules/leaflet.markercluster`).

**Geocoding requests fail**
- Nominatim rate-limits to 1 request/second; the app already throttles this, but heavy testing may still 429. Wait a few seconds and retry.

**Changes to .env.local not picked up**
- Restart the Vite dev server after editing environment variables.

## 7. Build for production
```bash
npm run build
npm run preview   # sanity-check the production build locally
```
Output goes to `dist/`. See `DEPLOYMENT.md` for hosting instructions.
