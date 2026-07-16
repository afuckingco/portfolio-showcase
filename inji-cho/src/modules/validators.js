// ===== Input Validation & Sanitization =====

export function sanitizeString(str) {
  if (typeof str !== 'string') return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML.trim();
}

export function validateTemple(data) {
  const errors = {};

  if (!data.name || !data.name.trim()) {
    errors.name = 'Name is required';
  } else if (data.name.length > 200) {
    errors.name = 'Name must be under 200 characters';
  }

  const lat = parseFloat(data.lat);
  const lng = parseFloat(data.lng);

  if (Number.isNaN(lat) || lat < -90 || lat > 90) {
    errors.lat = 'Latitude must be between -90 and 90';
  }
  if (Number.isNaN(lng) || lng < -180 || lng > 180) {
    errors.lng = 'Longitude must be between -180 and 180';
  }

  if (data.notes && data.notes.length > 2000) {
    errors.notes = 'Notes must be under 2000 characters';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}

export function sanitizeTemple(data) {
  return {
    name: sanitizeString(data.name),
    prefecture: sanitizeString(data.prefecture || ''),
    region: sanitizeString(data.region || ''),
    lat: parseFloat(data.lat),
    lng: parseFloat(data.lng),
    notes: sanitizeString(data.notes || ''),
    visited: Boolean(data.visited),
    visitDate: data.visitDate || null,
    address: sanitizeString(data.address || '')
  };
}

export function isValidCoordinate(lat, lng) {
  return (
    !Number.isNaN(lat) &&
    !Number.isNaN(lng) &&
    lat >= -90 && lat <= 90 &&
    lng >= -180 && lng <= 180
  );
}

export function validateImportData(json) {
  try {
    const parsed = typeof json === 'string' ? JSON.parse(json) : json;
    if (!Array.isArray(parsed)) {
      return { valid: false, error: 'Import data must be an array of temples' };
    }
    const invalid = parsed.filter(t => !t.name || !isValidCoordinate(parseFloat(t.lat), parseFloat(t.lng)));
    if (invalid.length > 0) {
      return { valid: false, error: `${invalid.length} entries have missing/invalid name or coordinates` };
    }
    return { valid: true, data: parsed };
  } catch (e) {
    return { valid: false, error: 'Invalid JSON file' };
  }
}
