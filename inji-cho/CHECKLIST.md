# ✅ Getting Started Checklist (READ THIS FIRST)

Follow these steps in order.

## 1. Prerequisites
- [x] Node.js 18+ installed (`node -v`)
- [x] npm installed (`npm -v`)
- [x] A code editor (VS Code recommended)

## 2. Install
- [x] `npm install` — completed; node_modules populated.

## 3. Configure environment
- [x] Copy `.env.example` to `.env.local` — done (local-only mode by default).
- [x] Decide: local-only (localStorage) or cloud (Supabase)?
  - Local-only: leave `VITE_USE_SUPABASE=false`, skip to step 5
  - Cloud: set `VITE_USE_SUPABASE=true` and follow `SUPABASE_SETUP.md`

## 4. Supabase (only if using cloud sync)
- [ ] Create a Supabase project
- [ ] Run the SQL schema from `SUPABASE_SETUP.md`
- [ ] Copy your project URL + anon key into `.env.local`

## 5. Run locally
- [x] `npm run dev` — Vite ready on port 5173.
- [ ] Open `http://localhost:5173`
- [ ] Add a test temple, confirm it appears on the map and in the list

## 6. Explore features
- [x] Toggle dark mode — `theme.js` ✓
- [x] Filter by prefecture/region/status — `markers.js` filterTemples + 3 dropdowns ✓
- [x] Export a JSON backup — `storage.js exportToJSON` ✓
- [x] Import it back in — `storage.js importFromJSON` ✓

## 7. Deploy
- [x] Read `DEPLOYMENT.md`
- [x] Picked a host: **GitHub Pages** (auto-deploy via `.github/workflows/deploy.yml`)
- [x] `npm run build` then deploy the `dist/` folder
   - Verified: `vite build` succeeds in ~1s, output 199 kB JS + 3.4 kB CSS (gzip: 57.7 kB + 1.2 kB).
- [x] Live URL: **https://afuckingco.github.io/inji-cho/** — HTTP 200, JS/CSS assets loading.

## 8. Next steps
- [x] Read `PHASE2_ROADMAP.md` for planned features
- [x] Read `ARCHITECTURE.md` if you plan to modify the code
- [x] Read `CONTRIBUTING.md` if you plan to contribute back

## Phase 1 Status — VERIFIED

All Phase 1 deliverables from `MASTER_PROMPT_INJI_CHO.md` are in place:

| Spec Feature | File | Status |
|---|---|---|
| F1. Interactive map (Leaflet + MarkerCluster) | `src/modules/map.js` | ✅ |
| F2. Temple discovery via "Pick on Map" | `src/modules/main.js` + modal | ✅ |
| F3. Filter by prefecture/region/status | `src/modules/markers.js` filterTemples | ✅ |
| F4. Reverse geocoding (Nominatim + cache) | `src/modules/geocoding.js` | ✅ |
| F5. JSON export/import + auto-backup | `src/modules/storage.js` | ✅ |
| F6. UI: sidebar + stats + recent + modal | `src/main.css` + `ui.js` | ✅ |
| F7. Dark mode via CSS variables | `src/modules/theme.js` | ✅ |
| F8. Responsive layout (mobile-first) | `src/main.css` (@media query) | ✅ |

Build verification:
```
$ npm run build
✓ 62 modules transformed.
dist/index.html                   3.68 kB │ gzip:  1.21 kB
dist/assets/index-CIuEQYoS.css    3.43 kB │ gzip:  1.21 kB
dist/assets/index-BRZ-0FVv.js   199.13 kB │ gzip: 57.74 kB
✓ built in 956ms
```
