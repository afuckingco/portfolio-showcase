# Production Deployment

## Build

```bash
npm run build
```
Output is a static site in `dist/`.

## Option A: Netlify

1. `npm install -g netlify-cli` (optional, or use the web UI)
2. Connect your Git repo in the Netlify dashboard, or drag-and-drop `dist/`.
3. Build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
4. Add environment variables in Site settings → Environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_USE_SUPABASE`

## Option B: Vercel

1. Import the repo at https://vercel.com/new
2. Framework preset: Vite
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add the same environment variables as above in Project Settings → Environment Variables.

## Option C: GitHub Pages

1. In `vite.config.js`, set `base: '/your-repo-name/'` if deploying to `username.github.io/your-repo-name`.
2. Build: `npm run build`
3. Deploy the `dist/` folder to the `gh-pages` branch, e.g. using the `gh-pages` npm package:
   ```bash
   npm install -D gh-pages
   npx gh-pages -d dist
   ```
4. In repo Settings → Pages, set source to the `gh-pages` branch.
5. Note: environment variables baked at build time — set them locally in `.env.local` before running `npm run build`, since GitHub Pages has no server-side env config.

## Post-deploy checklist

- [ ] Map tiles load correctly (check CSP/firewall if not)
- [ ] Adding/editing/deleting a temple works
- [ ] Dark mode toggle persists across reloads
- [ ] Export/Import JSON works
- [ ] If using Supabase, confirm rows appear in the Table Editor
