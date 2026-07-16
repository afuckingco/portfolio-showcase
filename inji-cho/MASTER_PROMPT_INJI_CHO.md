# 🏮 INJI-CHO: Complete Application Development Prompt

**Project Name**: Inji-cho (隠寺手帖) - Japanese Temple Field Journal  
**Version**: 0.1.0 (Phase 1)  
**Status**: Production-Ready Blueprint  

---

## 📋 PROJECT OVERVIEW

### Vision
A beautiful, minimal web application for documenting and mapping Japanese temples and shrines. Users can discover, record, and share their temple visits on an interactive map with traditional Japanese aesthetic.

### Target Users
- Temple enthusiasts
- Cultural researchers
- Travel photographers
- Japanese culture followers

### Technology Stack
- **Frontend**: Vanilla JavaScript (ES6 modules)
- **Map Engine**: Leaflet.js + MarkerCluster
- **Build Tool**: Vite
- **Backend/Database**: Supabase (PostgreSQL + PostGIS)
- **Geocoding**: Nominatim (OpenStreetMap)
- **Styling**: CSS3 (Grid, Flexbox, CSS Variables)
- **Hosting**: Netlify/Vercel/GitHub Pages

---

## 🎯 PHASE 1: CORE FEATURES (Complete)

### Feature 1: Interactive Map
**Requirement**: Display interactive map with temple locations

**Specifications**:
- Map library: Leaflet.js 1.9.4+
- Default center: Lat 35.6762, Lng 139.6503 (Tokyo)
- Default zoom: 8
- Tile provider: OpenStreetMap (free)
- Marker clustering: MarkerCluster plugin (auto-cluster at zoom < 17)
- Custom marker icon: SVG torii gate (32x40px)
- Marker popup: Temple name, prefecture, region, notes, visited status

**Database Schema**:
```sql
CREATE TABLE temples (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name TEXT NOT NULL,
  prefecture TEXT,
  region TEXT,
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  location_name TEXT,
  visited BOOLEAN DEFAULT false,
  notes TEXT,
  photo_urls TEXT[] DEFAULT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_temples_coordinates ON temples USING GIST(
  ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')', 4326)
);
```

**User Interaction**:
- Scroll wheel to zoom
- Click+drag to pan
- Double-click to zoom to point
- Click marker to open popup
- Click marker popup "Details" → Show temple info

---

### Feature 2: Temple Discovery & Creation

**Requirement**: Allow users to add temples to map

**Specification - Pick Mode**:
1. Click "📍 Pick Location" button
2. Button changes to "✓ Pick Mode Active" (highlighted)
3. User clicks map at temple location
4. Modal form appears with:
   - Name field (required, min 2 chars)
   - Prefecture dropdown (47 Japanese prefectures)
   - Region field (optional, text)
   - Latitude field (auto-filled, readonly)
   - Longitude field (auto-filled, readonly)
   - Location name field (auto-filled via Nominatim, readonly)
   - Notes textarea (optional, max 1000 chars)
   - Visited checkbox
   - Save/Cancel buttons

**Validation**:
- Name: 2-100 characters, required
- Latitude: -90 to 90
- Longitude: -180 to 180
- Notes: max 1000 characters
- Sanitize HTML to prevent XSS

**Database Operation**:
```javascript
INSERT INTO temples (name, prefecture, region, latitude, longitude, location_name, visited, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
```

---

### Feature 3: Filter & Search

**Requirement**: Filter temples by criteria

**Filter Types**:
1. **Prefecture Filter** - Dropdown/chips showing all prefectures with temple count
2. **Region Filter** - Chips showing regions in selected prefecture
3. **Visit Status** - Chips: "✓ Visited" / "◯ Not Visited"

**Implementation**:
- Filter chips appear in left sidebar
- Click chip to toggle active/inactive
- Active chips apply filter immediately
- Map updates to show only matching temples
- Multiple filters combine with AND logic

**Database Query**:
```javascript
SELECT * FROM temples 
WHERE (prefecture = ? OR prefecture IS NULL)
  AND (region = ? OR region IS NULL)
  AND (visited = ? OR visited IS NULL)
ORDER BY created_at DESC
```

---

### Feature 4: Reverse Geocoding

**Requirement**: Auto-fill location name from coordinates

**Specification**:
- Use Nominatim API (free, OpenStreetMap)
- Endpoint: `https://nominatim.openstreetmap.org/reverse`
- Parameters: `lat`, `lon`, `format=json`
- Cache results in localStorage (key: coordinates)
- Fallback: Use coordinates if API fails
- Rate limit: 1 second between requests (Nominatim TOS)
- Timeout: 5 seconds

**Response Parsing**:
```javascript
// API returns address object
// Extract: city/town/village + state + country
const location = address.city || address.town || address.village
                + ", " + address.state
// Result example: "Asakusa, Tokyo"
```

---

### Feature 5: JSON Export/Import

**Requirement**: Backup and restore temple data

**Export Specification**:
```json
{
  "version": "1.0",
  "exportDate": "2026-07-04T12:00:00Z",
  "count": 10,
  "temples": [
    {
      "id": 1,
      "name": "Senso-ji",
      "prefecture": "Tokyo",
      "region": "Asakusa",
      "latitude": 35.7148,
      "longitude": 139.7967,
      "location_name": "Asakusa, Tokyo",
      "visited": true,
      "notes": "Beautiful morning visit",
      "created_at": "2026-07-01T10:00:00Z",
      "updated_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

**Export Flow**:
1. Click "📥 Export" button
2. Download `temples-YYYY-MM-DD.json`

**Import Flow**:
1. Click "📤 Import" button
2. Select JSON file
3. Validate file format
4. Merge with existing temples (no duplicates by ID)
5. Show success notification: "✓ Imported 5 temples"

**Validation**:
- File must be valid JSON
- Must have "temples" array
- Each temple must have required fields
- Skip invalid entries, count how many skipped

---

### Feature 6: User Interface

**Layout**:
```
┌─────────────────────────────────────────┐
│ Header: 🏮 隠寺手帖 [Buttons: Pick/Export/Import/Dark/About] │
├──────────────┬──────────────────────────┤
│   Sidebar    │                          │
│   (300px)    │         MAP              │
│              │       (Leaflet)          │
│  Filters     │                          │
│  Statistics  │                          │
│  Recent      │                          │
└──────────────┴──────────────────────────┘
```

**Header Buttons**:
- 📍 Pick Location - Toggle pick mode
- 📥 Export - Download JSON
- 📤 Import - Upload JSON
- 🌙 Dark Mode - Toggle dark mode
- ℹ️ About - Show info modal

**Sidebar**:
- **Filters Section**: Prefecture/Region/Visit Status chips
- **Statistics Section**: Total/Visited/Remaining counts
- **Recent Section**: Last 5 temples added (clickable → pan to)

**Modal Forms**:
- Temple creation form (from pick mode)
- About modal (project info)
- Future: Temple detail view, photo gallery (Phase 2)

---

### Feature 7: Dark Mode

**Requirement**: Support dark theme

**Implementation**:
- CSS variables for all colors
- Toggle via JavaScript
- Save preference to localStorage
- Detect system preference (prefers-color-scheme)

**Colors - Light Mode**:
```css
--bg-primary: #f5f5dc;        /* Washi paper beige */
--bg-secondary: #faf8f3;      /* Off-white */
--text-primary: #2c2c2c;      /* Dark gray */
--accent-rust: #8B4513;       /* Saddle brown */
--accent-sage: #6b8e7f;       /* Sage green */
--border-color: #d4d4d4;      /* Light border */
```

**Colors - Dark Mode**:
```css
--bg-primary: #0a0a0a;        /* Pure black */
--bg-secondary: #1a1a1a;      /* Dark gray */
--text-primary: #e8e8e8;      /* Light gray */
--accent-rust: #c77a54;       /* Lighter rust */
--accent-sage: #7ab899;       /* Lighter sage */
--border-color: #333333;      /* Dark border */
```

**Transition**: Smooth 250ms transition between modes

---

### Feature 8: Responsive Design

**Requirement**: Work on all screen sizes

**Breakpoints**:
```css
/* Desktop: 1025px+ */
Grid: Sidebar (300px) + Map (1fr)

/* Tablet: 769-1024px */
Grid: Sidebar (250px) + Map (1fr)

/* Mobile: 0-768px */
Grid: Single column
Sidebar: Collapsible or full-width
Map: Full width below
```

**Mobile Optimizations**:
- Touch-friendly tap targets (48x48px)
- Simplified header (stack buttons)
- Hide unnecessary info on small screens
- Full-screen map on mobile

---

## 📦 PROJECT STRUCTURE

```
inji-cho/
├── src/
│   ├── index.html
│   ├── main.js (entry point, initialization)
│   ├── main.css (global styles + variables)
│   │
│   ├── modules/
│   │   ├── db.js (Supabase client, CRUD)
│   │   ├── map.js (Leaflet initialization, markers)
│   │   ├── ui.js (DOM events, notifications)
│   │   ├── geocoding.js (Nominatim API)
│   │   ├── storage.js (JSON import/export)
│   │   ├── theme.js (dark mode toggle)
│   │   └── markers.js (marker utilities)
│   │
│   ├── utils/
│   │   ├── constants.js (app constants, prefectures, colors)
│   │   ├── helpers.js (utility functions)
│   │   └── validators.js (input validation)
│   │
│   └── styles/ (optional)
│       ├── map.css
│       ├── washi.css
│       └── dark-mode.css
│
├── package.json
├── vite.config.js
├── .env.example
├── .gitignore
├── README.md
├── LICENSE (MIT)
├── CONTRIBUTING.md
├── docs/
│   ├── SUPABASE_SETUP.md
│   ├── ARCHITECTURE.md
│   ├── PHASE2_ROADMAP.md
│   └── DEPLOYMENT.md
└── dist/ (build output)
```

---

## 🔧 DEVELOPMENT SETUP

### Prerequisites
- Node.js 18+
- Git
- Supabase account (free)
- Code editor (VS Code recommended)

### Installation
```bash
# Clone or create project
mkdir inji-cho && cd inji-cho

# Initialize
npm init -y
npm install leaflet leaflet-markercluster @supabase/supabase-js
npm install -D vite

# Setup
cp .env.example .env.local
# Edit .env.local with Supabase credentials

# Development
npm run dev         # http://localhost:3000

# Production
npm run build       # Creates dist/
npm run preview     # Test build locally
```

### Configuration Files

**package.json** - Dependencies:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "leaflet": "^1.9.4",
    "leaflet-markercluster": "^1.5.1",
    "@supabase/supabase-js": "^2.38.0"
  }
}
```

**.env.example**:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_MAP_CENTER_LAT=35.6762
VITE_MAP_CENTER_LNG=139.6503
VITE_MAP_ZOOM=8
```

---

## 🔌 API & INTEGRATIONS

### Supabase
- **Type**: Backend as a Service (BaaS)
- **Plan**: Free tier sufficient
- **Operations**: 
  - `getTemples(filters)` - Query with filtering
  - `createTemple(data)` - Insert new temple
  - `updateTemple(id, data)` - Update temple
  - `deleteTemple(id)` - Delete temple
  - `bulkInsertTemples(array)` - Batch insert for import

**Authentication**: Public anon key (read/write with RLS)

### Nominatim (OpenStreetMap)
- **Type**: Free reverse geocoding
- **Endpoint**: `https://nominatim.openstreetmap.org/reverse`
- **Rate Limit**: 1 request/second (respect TOS)
- **Caching**: localStorage to minimize requests
- **Fallback**: Use coordinates if API down

### Leaflet.js & Tiles
- **Tiles**: OpenStreetMap (free, no key needed)
- **Plugins**: MarkerCluster for grouping markers
- **Custom Icons**: SVG torii gates

---

## 🎨 DESIGN SYSTEM

### Color Palette (Washi Aesthetic)
**Light Mode**:
- Primary background: #f5f5dc (washi beige)
- Text: #2c2c2c (dark)
- Accent 1: #8B4513 (rust/saddle brown)
- Accent 2: #6b8e7f (sage green)
- Accent 3: #daa520 (gold)

**Dark Mode**:
- Primary background: #0a0a0a (black)
- Text: #e8e8e8 (light gray)
- Accent 1: #c77a54 (lighter rust)
- Accent 2: #7ab899 (lighter sage)
- Accent 3: #daa520 (same gold)

### Typography
- Font family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- Font sizes: xs (0.75rem) → 2xl (2rem)
- Line height: 1.6
- Font weight: 400, 500, 600, 700

### Spacing
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)

### Border Radius
- sm: 4px
- md: 8px
- lg: 12px
- full: 50% (circles)

### Shadows
- sm: 0 1px 2px rgba(0,0,0,0.05)
- md: 0 4px 6px rgba(0,0,0,0.1)
- lg: 0 10px 15px rgba(0,0,0,0.15)

---

## 🚀 DEPLOYMENT

### Option 1: Netlify (Recommended)
1. Push to GitHub
2. Connect repo at netlify.com
3. Set build: `npm run build`, publish: `dist`
4. Add environment variables (Supabase URL + key)
5. Auto-deploy on every push

**Result**: `https://yoursite.netlify.app`

### Option 2: Vercel
1. Push to GitHub
2. Import project at vercel.com
3. Set environment variables
4. Auto-deploy on push

**Result**: `https://yoursite.vercel.app`

### Option 3: GitHub Pages
1. Add `deploy.sh` script
2. Build locally and push to `gh-pages` branch
3. Configure in Settings → Pages

**Result**: `https://yourusername.github.io/inji-cho/`

---

## 📊 DATA FLOW

```
User Interaction (UI)
    ↓
UI Module (events, validation)
    ↓
App State (temples array, filters)
    ↓
┌─────────────────────────────────┐
│ Database Module    │ Map Module  │ Storage Module
│ (Supabase)        │ (Leaflet)   │ (JSON)
└─────────────────────────────────┘
    ↓
External Services
(Supabase, Leaflet tiles, Nominatim)
```

---

## ✅ QUALITY STANDARDS

### Code Quality
- All functions documented with JSDoc
- No console.log in production
- Input validation on all forms
- Error handling with try-catch
- Consistent naming (camelCase functions, UPPER_CASE constants)

### Performance
- Lazy load map tiles
- Marker clustering for large datasets
- Debounce filter changes (300ms)
- Cache Nominatim results in localStorage
- Minify CSS/JS in build

### Security
- Sanitize HTML input (prevent XSS)
- Supabase RLS enabled (prevent unauthorized access)
- No sensitive data in localStorage
- HTTPS enforced on production
- Environment variables for API keys

### Accessibility
- Semantic HTML (header, main, aside, section)
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast ≥ 4.5:1
- Focus states on all inputs

### Responsiveness
- Mobile-first CSS
- Touch-friendly buttons (48x48px minimum)
- Works on: mobile (375px), tablet (768px), desktop (1920px)
- Adapts layout: single column → two columns → three columns

---

## 📅 PHASE 2: FUTURE FEATURES (Documented)

**Photo Upload**:
- Upload up to 5 photos per temple
- Auto-compress before storage
- Display as gallery

**Statistics Dashboard**:
- Total temples count
- Visited vs unvisited
- Temples per prefecture (bar chart)
- Visit timeline

**Custom Sorting**:
- By name, date, visit status, prefecture
- Remember last sort preference

**Dark Mode Enhancement**:
- Schedule by time of day
- System preference detection

---

## 🎯 SUCCESS CRITERIA

The application is complete when:

- [x] Map loads with OSM tiles
- [x] Can add temples via pick mode
- [x] Filters work correctly
- [x] JSON export/import functional
- [x] Dark mode toggles smoothly
- [x] Mobile responsive (tested on real devices)
- [x] Database connects to Supabase
- [x] No console errors
- [x] Deployable to production
- [x] Documented and ready for GitHub

---

## 🔗 KEY RESOURCES

| Resource | URL |
|----------|-----|
| Leaflet.js | https://leafletjs.com/ |
| Supabase | https://supabase.com/ |
| Vite | https://vitejs.dev/ |
| Nominatim API | https://nominatim.openstreetmap.org/ |
| MDN Web Docs | https://developer.mozilla.org/ |
| Netlify | https://netlify.com/ |

---

## 📝 DOCUMENTATION STRUCTURE

**For Users**:
- README.md - Overview, features, screenshots
- GETTING_STARTED.md - 5-minute quickstart

**For Developers**:
- SETUP_LOCAL.md - Local development (30 min)
- ARCHITECTURE.md - Code structure, module docs
- SUPABASE_SETUP.md - Database configuration
- CONTRIBUTING.md - How to contribute

**For Deployment**:
- DEPLOYMENT.md - Netlify/Vercel/GitHub Pages
- PHASE2_ROADMAP.md - Feature planning

---

## 🏁 DELIVERY CHECKLIST

### Code
- [ ] All 11 modules complete
- [ ] All utility functions implemented
- [ ] All validation in place
- [ ] All error handling working
- [ ] No security vulnerabilities
- [ ] Runs without errors: `npm run dev`
- [ ] Builds successfully: `npm run build`

### Documentation
- [ ] README.md comprehensive
- [ ] ARCHITECTURE.md detailed
- [ ] SETUP_LOCAL.md tested
- [ ] SUPABASE_SETUP.md working
- [ ] DEPLOYMENT.md verified
- [ ] Code comments complete
- [ ] JSDoc on all functions

### Testing
- [ ] Loads in browser (Chrome, Firefox, Safari)
- [ ] Mobile responsive (DevTools)
- [ ] Database connects
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable (<3s load)

### Deployment
- [ ] Works on Netlify OR Vercel OR GitHub Pages
- [ ] Environment variables configured
- [ ] Custom domain optional
- [ ] Auto-deploy on git push
- [ ] HTTPS working

---

## 📞 NEXT STEPS

1. **Setup**: Follow SETUP_LOCAL.md (1-2 hours)
2. **Develop**: Create all modules and styles
3. **Test**: Verify all features work
4. **Document**: Write comprehensive guides
5. **Deploy**: Push to Netlify/Vercel
6. **Share**: Publish to GitHub
7. **Gather Feedback**: Iterate on Phase 2

---

## 🎓 LEARNING OUTCOMES

After completing this project, you will understand:

- ✅ Vanilla JavaScript ES6 modules
- ✅ Interactive mapping with Leaflet.js
- ✅ Backend-as-a-Service (Supabase)
- ✅ REST API integration
- ✅ Form validation and sanitization
- ✅ Local storage and caching
- ✅ Responsive CSS design
- ✅ Dark mode implementation
- ✅ Production deployment
- ✅ Project documentation

---

**PROJECT STATUS**: READY TO BUILD 🚀

**Estimated Time**: 40-80 hours development (depending on experience)

**Complexity**: Intermediate (ES6 modules, APIs, database)

**Scalability**: Ready for Phase 2 & 3 features

---

*Created: July 2026*  
*Type: Complete Web Application Specification*  
*License: MIT*  
*Status: Production Blueprint*
