// ===== Application Entry & Bootstrap =====
import '../main.css';
import { initTheme, toggleTheme } from './theme.js';
import { initMap, renderMarkers, focusOnTemple, fitToMarkers, enableClickToAdd } from './map.js';
import { fetchTemples, createTemple, updateTemple, deleteTemple } from './db.js';
import { validateTemple, sanitizeTemple } from './validators.js';
import { filterTemples } from './markers.js';
import {
  showNotification, populateFilterDropdowns, bindSearchInput,
  getFormData, showFormErrors, clearFormErrors, openModal, closeModal,
  updateStatsDisplay
} from './ui.js';
import { exportToJSON, importFromJSON, createAutoBackup } from './storage.js';
import { reverseGeocode } from './geocoding.js';
import { calculateDistance } from '../utils/helpers.js';
import { FEATURE_FLAGS } from '../utils/constants.js';

const state = {
  temples: [],
  filters: { search: '', prefecture: '', region: '', status: '' },
  editingId: null,
  userLocation: null
};

async function bootstrap() {
  initTheme();
  initMap('map');
  populateFilterDropdowns();
  bindEvents();

  state.temples = await fetchTemples();
  refresh();

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      state.userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      refresh();
    });
  }
}

function refresh() {
  const filtered = filterTemples(state.temples, state.filters);
  renderMarkers(filtered, { onEdit: openEditModal, onDelete: handleDelete });
  updateStatsDisplay(state.temples);
  renderList(filtered);
}

function renderList(temples) {
  const listEl = document.getElementById('temple-list');
  if (!listEl) return;

  listEl.innerHTML = temples.map((t) => {
    const dist = state.userLocation
      ? calculateDistance(state.userLocation.lat, state.userLocation.lng, t.lat, t.lng).toFixed(1) + ' km'
      : '';
    return `
      <li class="temple-list-item" data-id="${t.id}">
        <span class="temple-name">${t.name}</span>
        <span class="temple-pref">${t.prefecture || ''}</span>
        ${dist ? `<span class="temple-dist">${dist}</span>` : ''}
      </li>`;
  }).join('');

  listEl.querySelectorAll('.temple-list-item').forEach((li) => {
    li.addEventListener('click', () => focusOnTemple(li.dataset.id));
  });
}

function bindEvents() {
  document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);

  const searchInput = document.getElementById('search-input');
  if (searchInput) bindSearchInput(searchInput, (val) => { state.filters.search = val; refresh(); });

  document.getElementById('filter-prefecture')?.addEventListener('change', (e) => {
    state.filters.prefecture = e.target.value; refresh();
  });
  document.getElementById('filter-region')?.addEventListener('change', (e) => {
    state.filters.region = e.target.value; refresh();
  });
  document.getElementById('filter-status')?.addEventListener('change', (e) => {
    state.filters.status = e.target.value; refresh();
  });

  document.getElementById('btn-add-temple')?.addEventListener('click', () => openEditModal(null));
  document.getElementById('btn-fit-map')?.addEventListener('click', fitToMarkers);
  document.getElementById('btn-export')?.addEventListener('click', () => exportToJSON(state.temples));
  document.getElementById('import-file-input')?.addEventListener('change', handleImport);

  const form = document.getElementById('temple-form');
  form?.addEventListener('submit', handleFormSubmit);
  document.getElementById('btn-cancel-form')?.addEventListener('click', () => closeModal('temple-modal'));

  document.getElementById('btn-use-map-click')?.addEventListener('click', () => {
    showNotification('Click anywhere on the map to set coordinates', 'info');
    enableClickToAdd(async (lat, lng) => {
      document.getElementById('field-lat').value = lat.toFixed(6);
      document.getElementById('field-lng').value = lng.toFixed(6);
      const geo = await reverseGeocode(lat, lng);
      if (geo.prefecture) document.getElementById('field-prefecture').value = geo.prefecture;
      if (geo.address) document.getElementById('field-address').value = geo.address;
    });
  });
}

function openEditModal(id) {
  state.editingId = id;
  const form = document.getElementById('temple-form');
  clearFormErrors(form);

  if (id) {
    const temple = state.temples.find((t) => t.id === id);
    if (!temple) return;
    Object.entries(temple).forEach(([key, val]) => {
      const field = form.querySelector(`[name="${key}"]`);
      if (!field) return;
      if (field.type === 'checkbox') field.checked = Boolean(val);
      else field.value = val ?? '';
    });
  } else {
    form.reset();
  }
  openModal('temple-modal');
}

async function handleFormSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const raw = getFormData(form);
  const { valid, errors } = validateTemple(raw);

  if (!valid) {
    showFormErrors(form, errors);
    return;
  }

  const clean = sanitizeTemple(raw);

  try {
    if (state.editingId) {
      const updated = await updateTemple(state.editingId, clean);
      const idx = state.temples.findIndex((t) => t.id === state.editingId);
      state.temples[idx] = updated;
      showNotification('Temple updated', 'success');
    } else {
      const created = await createTemple(clean);
      state.temples.push(created);
      showNotification('Temple added', 'success');
    }
    createAutoBackup(state.temples);
    closeModal('temple-modal');
    refresh();
  } catch (err) {
    console.error(err);
    showNotification('Something went wrong saving this temple', 'error');
  }
}

async function handleDelete(id) {
  if (!confirm('Delete this temple entry?')) return;
  try {
    await deleteTemple(id);
    state.temples = state.temples.filter((t) => t.id !== id);
    createAutoBackup(state.temples);
    refresh();
    showNotification('Temple deleted', 'success');
  } catch (err) {
    console.error(err);
    showNotification('Failed to delete temple', 'error');
  }
}

function handleImport(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const imported = importFromJSON(reader.result);
      for (const t of imported) {
        const created = await createTemple(t);
        state.temples.push(created);
      }
      refresh();
      showNotification(`Imported ${imported.length} temples`, 'success');
    } catch (err) {
      showNotification('Import failed: invalid file', 'error');
    }
  };
  reader.readAsText(file);
}

document.addEventListener('DOMContentLoaded', bootstrap);

if (FEATURE_FLAGS.ENABLE_CLUSTERING) {
  console.info('隠寺手帖 — clustering enabled');
}
