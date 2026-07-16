# Architecture & Code Structure

```
inji-cho/
├── index.html                  Entry HTML, form/modal markup
├── package.json
├── vite.config.js
├── .env.example
├── src/
│   ├── main.css                 Global styles, CSS variables, dark mode
│   ├── modules/
│   │   ├── main.js               App bootstrap, event wiring, state
│   │   ├── db.js                 Supabase CRUD client + localStorage fallback
│   │   ├── map.js                Leaflet map init, marker rendering, clustering
│   │   ├── ui.js                 DOM helpers: forms, modals, notifications, stats
│   │   ├── geocoding.js           Nominatim reverse geocoding + address search
│   │   ├── storage.js             localStorage persistence, JSON export/import
│   │   ├── theme.js               Dark mode toggle & system preference sync
│   │   ├── markers.js             Marker icon generation, filtering, popups
│   │   └── validators.js          Input validation & sanitization
│   └── utils/
│       ├── constants.js           App-wide constants, feature flags, colors
│       └── helpers.js             debounce, haversine distance, sorting, etc.
```

## Data flow

1. `main.js` boots the app: initializes theme, map, dropdowns, and event listeners.
2. `db.js` fetches temples — from Supabase if configured, otherwise from `storage.js` (localStorage).
3. State lives in a plain object inside `main.js` (`state.temples`, `state.filters`).
4. On any mutation (create/update/delete), `main.js` calls `db.js`, updates local `state`, then calls `refresh()`.
5. `refresh()` filters temples via `markers.js#filterTemples`, then re-renders the map (`map.js#renderMarkers`), the sidebar list, and the stats panel (`ui.js#updateStatsDisplay`).

## Why no framework?

The app is intentionally framework-free (vanilla ES modules) to keep the single-file-to-multi-file migration simple and to make it trivially deployable as static files (GitHub Pages, etc.) without a build step being strictly required — though Vite is used for dev ergonomics (HMR, env vars, bundling npm deps like Leaflet).

## Feature flags

`src/utils/constants.js` exports `FEATURE_FLAGS`:
- `USE_SUPABASE` — toggles cloud vs local persistence (read from `.env`)
- `ENABLE_PHOTO_UPLOAD` — Phase 2, currently off
- `ENABLE_STATS_DASHBOARD` — on
- `ENABLE_DARK_MODE` — on
- `ENABLE_CLUSTERING` — on

## Extending the app

- **New field on a temple**: update `validators.js` (validation + sanitization), the form in `index.html`, and the Supabase schema in `SUPABASE_SETUP.md`.
- **New filter**: add UI in `index.html`, wire an event in `main.js`, extend `filterTemples` in `markers.js`.
- **New marker style**: edit `createToriiIcon` in `markers.js`.
