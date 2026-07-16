```markdown
```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ cat README.md
```

# ⛩️ Inji-cho (隠寺手帖)

> A curated, interactive digital catalog of hidden shrines and temples. Built with a minimalist, respectful UI and real-time geospatial mapping to document and navigate lesser-known spiritual and historical sites.

<div align="center">

[![Status](https://img.shields.io/badge/STATUS-PHASE_2_ACTIVE-a6e3a1?style=for-the-badge&labelColor=1e1e2e)]()
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)]()
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-89b4fa?style=for-the-badge&labelColor=1e1e2e)](LICENSE)

</div>

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ ./build.sh --pipeline
```

```text
[Pipeline] GeoJSON Ingestion → Geocoding Validation → Leaflet Rendering → Interactive DOM Injection
Load Time: <150ms | Map Tiles: Optimized | Status: OPERATIONAL
```

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ htop --features
```

## ⚙️ Core Capabilities

| Module | Description | Impact |
|--------|-------------|--------|
| **Real-time Mapping** | Interactive, lightweight map rendering using Leaflet.js with custom minimal tile layers. | Provides immediate spatial context for remote or hidden locations. |
| **Offline-First Data** | Structured GeoJSON and local JSON caching for shrine metadata (history, coordinates, access notes). | Ensures core catalog functionality remains available in low-connectivity areas. |
| **Minimalist UI/UX** | Vanilla JS-driven DOM manipulation with a focus on typography, whitespace, and respectful presentation. | Eliminates bloat, allowing the content and locations to take center stage. |
| **Responsive Design** | Mobile-optimized layout with touch-friendly map controls and adaptive data cards. | Designed for on-the-ground exploration and field research. |

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ htop --stack
```

## 🛠️ Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Core Logic** | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) (ES6+) | Zero-framework overhead, maximum control over DOM and performance. |
| **Build Tool** | ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) | Blazing fast HMR and optimized production bundling. |
| **Mapping Engine** | ![Leaflet](https://img.shields.io/badge/Leaflet-77B900?style=flat&logo=leaflet&logoColor=white) | Lightweight, mobile-friendly, and highly customizable open-source maps. |
| **Data Format** | `GeoJSON` / `JSON` | Standardized, parseable format for geospatial coordinates and metadata. |
| **Styling** | Custom CSS / CSS Variables | Tailored aesthetic without the overhead of heavy utility frameworks. |

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ ./start.sh
```

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/afuckingco/inji-cho.git
cd inji-cho

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev

# 4. Open browser
#    Local: http://localhost:5173
```

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ tree -L 2 -I 'node_modules|dist|.git'
```

## 📂 Project Structure

```text
inji-cho/
├── index.html                # Main entry point
├── package.json              # Dependencies and Vite scripts
├── public/
│   ├── data/
│   │   └── shrines.geojson   # Core location and metadata database
│   └── assets/               # Icons, custom map markers, and static images
├── src/
│   ├── main.js               # Application entry and initialization
│   ├── map/
│   │   └── renderer.js       # Leaflet setup, tile layer config, and marker logic
│   ├── ui/
│   │   └── components.js     # Dynamic DOM generation for shrine detail cards
│   └── utils/
│       └── helpers.js        # Geocoding helpers and data parsing utilities
└── style.css                 # Global minimalist styling and responsive rules
```

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ cat KNOWN_LIMITATIONS.md
```

## ⚠️ Known Limitations

- **Geocoding Accuracy**: Remote or historically named shrines may have imprecise coordinates in open-source map data, requiring manual verification.
- **Tile Dependency**: While data is cached, base map tiles require an active internet connection unless a local tile server (e.g., OpenStreetMap offline) is configured.
- **Browser GPS Drift**: Mobile device GPS accuracy in dense forest or mountainous terrain (common for hidden shrines) may cause marker misalignment.

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ echo $ROADMAP
```

## 📈 Future Improvements (Phase 3)

- [ ] **PWA Conversion**: Add Service Workers for full offline map and catalog functionality.
- [ ] **Community Submissions**: Secure, moderated form for users to suggest new hidden locations with photo evidence.
- [ ] **AR Overlay**: Experimental WebXR integration to overlay directional markers through the device camera when on-site.
- [ ] **Multi-language Support**: i18n implementation for Japanese and English metadata.

---

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ connect --author
```

## 👤 Author

**Afiq Andico Pangimpian** — Developer, researcher, and digital archivist.

<div align="center">
  <a href="https://github.com/afuckingco" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/>
  </a>
  <a href="https://www.linkedin.com/in/pangimpian" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
  </a>
  <a href="mailto:anotherwaltzcompany@gmail.com" target="_blank">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white"/>
  </a>
</div>

> *Some places are meant to be found. This is the map to find them.*

```console
┌──(test㉿afuckingco)-[~/projects/inji-cho]
└─$ exit
```
> *Connection closed. Build something useful.*
```
