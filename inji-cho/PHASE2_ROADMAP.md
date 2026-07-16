# Phase 2 Roadmap (Planned Features)

These are documented but **not yet implemented** in Phase 1.

## 📷 Photo Uploads
- Attach one or more photos per temple.
- Client-side image compression before upload (target: <500KB per photo).
- Storage: Supabase Storage bucket `temple-photos`, referenced via the `photos` table (already scaffolded in `SUPABASE_SETUP.md`).
- Lightbox/gallery view in the temple popup.

## 📊 Statistics Dashboard (expanded)
- Visit breakdown by prefecture/region (bar chart).
- Visit timeline (visits over time).
- "Completion" progress toward user-defined goals (e.g. all Kyoto shrines).

## 🔀 Custom Sorting
- Sort temple list by: name, distance from user, date added, date visited.
- Persist sort preference in `SETTINGS_KEY` (localStorage).

## 🌓 Dark Mode Toggle (polish)
- Current Phase 1 ships dark mode via `theme.js`, driven by a single toggle button.
- Phase 2: add a three-way switch (Light / Dark / System) and smoother transition animations.

## Later ideas (unscheduled)
- Multi-stop itinerary planning with draggable reordering.
- Real-time weather via Open-Meteo API for planned visit dates.
- Cost estimation per itinerary (transport + entry fees).
- Visit history/journal with free-text entries per visit.
- Automated backup snapshots (rolling, beyond the 5 kept in `injicho_auto_backups`).
- Multi-user accounts with per-user RLS policies in Supabase.
