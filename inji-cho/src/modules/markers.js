// ===== Marker Utilities & Filtering =====
import { MARKER_COLORS, TORII_ICON_SVG } from '../utils/constants.js';
import L from 'leaflet';

export function createToriiIcon(status = 'unvisited') {
  const color = MARKER_COLORS[status] || MARKER_COLORS.unvisited;
  const svg = TORII_ICON_SVG.replace(/{{color}}/g, color);
  return L.divIcon({
    html: svg,
    className: 'torii-marker-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
}

export function statusOf(temple) {
  if (temple.visited) return 'visited';
  if (temple.visitDate && new Date(temple.visitDate) > new Date()) return 'planned';
  return 'unvisited';
}

export function filterTemples(temples, filters = {}) {
  return temples.filter((t) => {
    if (filters.prefecture && t.prefecture !== filters.prefecture) return false;
    if (filters.region && t.region !== filters.region) return false;
    if (filters.status && statusOf(t) !== filters.status) return false;
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const haystack = `${t.name} ${t.prefecture} ${t.notes || ''}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
}

export function buildPopupContent(temple) {
  const status = statusOf(temple);
  const statusLabel = { visited: '✅ Visited', planned: '📅 Planned', unvisited: '⛩️ Not yet visited' }[status];
  return `
    <div class="temple-popup">
      <h3>${escapeHtml(temple.name)}</h3>
      <p class="popup-meta">${escapeHtml(temple.prefecture || '')} ${temple.region ? '· ' + escapeHtml(temple.region) : ''}</p>
      <p class="popup-status">${statusLabel}</p>
      ${temple.notes ? `<p class="popup-notes">${escapeHtml(temple.notes)}</p>` : ''}
      <div class="popup-actions">
        <button data-action="edit" data-id="${temple.id}">Edit</button>
        <button data-action="delete" data-id="${temple.id}">Delete</button>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
