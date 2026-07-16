// ===== Local Storage Adapter (JSON export/import + persistence) =====
import { STORAGE_KEY, SETTINGS_KEY } from '../utils/constants.js';
import { downloadFile } from '../utils/helpers.js';

export function loadTemples() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Failed to load temples from localStorage:', e);
    return [];
  }
}

export function saveTemples(temples) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(temples));
    return true;
  } catch (e) {
    console.error('Failed to save temples to localStorage:', e);
    return false;
  }
}

export function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

export function saveSettings(settings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    return true;
  } catch (e) {
    console.error('Failed to save settings:', e);
    return false;
  }
}

export function exportToJSON(temples) {
  const payload = {
    exportedAt: new Date().toISOString(),
    app: 'inji-cho',
    version: 1,
    temples
  };
  downloadFile(
    `injicho-backup-${Date.now()}.json`,
    JSON.stringify(payload, null, 2)
  );
}

export function importFromJSON(fileText) {
  const parsed = JSON.parse(fileText);
  if (Array.isArray(parsed)) return parsed;
  if (parsed && Array.isArray(parsed.temples)) return parsed.temples;
  throw new Error('Unrecognized backup format');
}

export function clearAllData() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(SETTINGS_KEY);
}

export function createAutoBackup(temples) {
  try {
    const backups = JSON.parse(localStorage.getItem('injicho_auto_backups') || '[]');
    backups.unshift({ timestamp: Date.now(), count: temples.length, data: temples });
    const trimmed = backups.slice(0, 5); // keep last 5 snapshots
    localStorage.setItem('injicho_auto_backups', JSON.stringify(trimmed));
  } catch (e) {
    console.warn('Auto-backup failed:', e);
  }
}
