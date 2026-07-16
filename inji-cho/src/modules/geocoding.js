// ===== Nominatim Reverse Geocoding =====

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';
const REQUEST_HEADERS = { 'Accept-Language': 'ja,en' };

// Simple in-memory cache + rate limiting (Nominatim usage policy: max 1 req/sec)
let lastRequestTime = 0;
const MIN_INTERVAL_MS = 1100;
const cache = new Map();

async function throttledFetch(url) {
  const now = Date.now();
  const wait = Math.max(0, lastRequestTime + MIN_INTERVAL_MS - now);
  if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  lastRequestTime = Date.now();
  const res = await fetch(url, { headers: REQUEST_HEADERS });
  if (!res.ok) throw new Error(`Nominatim request failed: ${res.status}`);
  return res.json();
}

export async function reverseGeocode(lat, lng) {
  const key = `${lat.toFixed(5)},${lng.toFixed(5)}`;
  if (cache.has(key)) return cache.get(key);

  const url = `${NOMINATIM_BASE}/reverse?format=jsonv2&lat=${lat}&lon=${lng}&zoom=14&addressdetails=1`;
  try {
    const data = await throttledFetch(url);
    const result = {
      address: data.display_name || '',
      prefecture: data.address?.state || data.address?.province || '',
      city: data.address?.city || data.address?.town || data.address?.village || ''
    };
    cache.set(key, result);
    return result;
  } catch (e) {
    console.error('Reverse geocoding failed:', e);
    return { address: '', prefecture: '', city: '' };
  }
}

export async function searchAddress(query) {
  if (!query || query.trim().length < 3) return [];
  const url = `${NOMINATIM_BASE}/search?format=jsonv2&q=${encodeURIComponent(query)}&countrycodes=jp&limit=5`;
  try {
    const data = await throttledFetch(url);
    return data.map((item) => ({
      displayName: item.display_name,
      lat: parseFloat(item.lat),
      lng: parseFloat(item.lon)
    }));
  } catch (e) {
    console.error('Address search failed:', e);
    return [];
  }
}
