// ===== DOM Events, Forms, Notifications =====
import { NOTIFICATION_DURATION_MS, REGIONS, PREFECTURES } from '../utils/constants.js';
import { debounce } from '../utils/helpers.js';

export function showNotification(message, type = 'info') {
  const container = document.getElementById('notifications') || createNotificationContainer();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('toast-visible'));

  setTimeout(() => {
    toast.classList.remove('toast-visible');
    setTimeout(() => toast.remove(), 300);
  }, NOTIFICATION_DURATION_MS);
}

function createNotificationContainer() {
  const el = document.createElement('div');
  el.id = 'notifications';
  el.className = 'notifications-container';
  document.body.appendChild(el);
  return el;
}

export function populateSelect(selectEl, options, { includeEmpty = true, emptyLabel = 'All' } = {}) {
  selectEl.innerHTML = '';
  if (includeEmpty) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = emptyLabel;
    selectEl.appendChild(opt);
  }
  options.forEach((val) => {
    const opt = document.createElement('option');
    opt.value = val;
    opt.textContent = val;
    selectEl.appendChild(opt);
  });
}

export function populateFilterDropdowns() {
  const prefEl = document.getElementById('filter-prefecture');
  const regionEl = document.getElementById('filter-region');
  if (prefEl) populateSelect(prefEl, PREFECTURES);
  if (regionEl) populateSelect(regionEl, REGIONS);
}

export function bindSearchInput(inputEl, onSearch) {
  inputEl.addEventListener('input', debounce((e) => onSearch(e.target.value), 300));
}

export function getFormData(formEl) {
  const formData = new FormData(formEl);
  const data = {};
  for (const [key, value] of formData.entries()) {
    data[key] = value;
  }
  data.visited = formEl.querySelector('[name="visited"]')?.checked || false;
  return data;
}

export function showFormErrors(formEl, errors) {
  formEl.querySelectorAll('.field-error').forEach((el) => el.remove());
  Object.entries(errors).forEach(([field, message]) => {
    const input = formEl.querySelector(`[name="${field}"]`);
    if (!input) return;
    const errEl = document.createElement('span');
    errEl.className = 'field-error';
    errEl.textContent = message;
    input.insertAdjacentElement('afterend', errEl);
    input.classList.add('input-invalid');
  });
}

export function clearFormErrors(formEl) {
  formEl.querySelectorAll('.field-error').forEach((el) => el.remove());
  formEl.querySelectorAll('.input-invalid').forEach((el) => el.classList.remove('input-invalid'));
}

export function openModal(modalId) {
  document.getElementById(modalId)?.classList.add('modal-open');
}

export function closeModal(modalId) {
  document.getElementById(modalId)?.classList.remove('modal-open');
}

export function updateStatsDisplay(temples) {
  const total = temples.length;
  const visited = temples.filter((t) => t.visited).length;
  const remaining = total - visited;
  const pct = total ? Math.round((visited / total) * 100) : 0;

  const totalEl = document.getElementById('stat-total');
  const visitedEl = document.getElementById('stat-visited');
  const remainingEl = document.getElementById('stat-remaining');
  const pctEl = document.getElementById('stat-percent');

  if (totalEl) totalEl.textContent = total;
  if (visitedEl) visitedEl.textContent = visited;
  if (remainingEl) remainingEl.textContent = remaining;
  if (pctEl) pctEl.textContent = `${pct}%`;
}
