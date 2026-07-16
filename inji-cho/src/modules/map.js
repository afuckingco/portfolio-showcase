// ===== Leaflet.js Map (markers, popups, clustering) =====
import L from 'leaflet';
import 'leaflet.markercluster';
import { DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, FEATURE_FLAGS } from '../utils/constants.js';
import { createToriiIcon, statusOf, buildPopupContent } from './markers.js';

let map = null;
let markerLayer = null;
let markerIndex = new Map(); // id -> leaflet marker

export function initMap(containerId = 'map') {
  map = L.map(containerId, {
    center: DEFAULT_MAP_CENTER,
    zoom: DEFAULT_MAP_ZOOM,
    zoomControl: true
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);

  markerLayer = FEATURE_FLAGS.ENABLE_CLUSTERING
    ? L.markerClusterGroup({ maxClusterRadius: 50 })
    : L.layerGroup();

  markerLayer.addTo(map);
  return map;
}

export function getMap() {
  return map;
}

export function renderMarkers(temples, { onEdit, onDelete } = {}) {
  markerLayer.clearLayers();
  markerIndex.clear();

  temples.forEach((temple) => {
    if (Number.isNaN(temple.lat) || Number.isNaN(temple.lng)) return;

    const icon = createToriiIcon(statusOf(temple));
    const marker = L.marker([temple.lat, temple.lng], { icon });
    marker.bindPopup(buildPopupContent(temple));

    marker.on('popupopen', () => {
      const popupEl = marker.getPopup().getElement();
      popupEl.querySelector('[data-action="edit"]')?.addEventListener('click', () => onEdit?.(temple.id));
      popupEl.querySelector('[data-action="delete"]')?.addEventListener('click', () => onDelete?.(temple.id));
    });

    markerLayer.addLayer(marker);
    markerIndex.set(temple.id, marker);
  });
}

export function focusOnTemple(id) {
  const marker = markerIndex.get(id);
  if (marker && map) {
    map.setView(marker.getLatLng(), 14, { animate: true });
    marker.openPopup();
  }
}

export function fitToMarkers() {
  if (!map || markerIndex.size === 0) return;
  const group = L.featureGroup(Array.from(markerIndex.values()));
  map.fitBounds(group.getBounds().pad(0.15));
}

export function enableClickToAdd(callback) {
  map.on('click', (e) => callback(e.latlng.lat, e.latlng.lng));
}

export function getCurrentCenter() {
  return map ? map.getCenter() : { lat: DEFAULT_MAP_CENTER[0], lng: DEFAULT_MAP_CENTER[1] };
}
