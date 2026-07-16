// ===== App Constants =====

export const APP_NAME = '隠寺手帖';
export const APP_NAME_ROMAJI = 'Inji-cho';
export const STORAGE_KEY = 'injicho_temples_v1';
export const THEME_KEY = 'injicho_theme';
export const SETTINGS_KEY = 'injicho_settings';

export const DEFAULT_MAP_CENTER = [36.2048, 138.2529]; // Japan center
export const DEFAULT_MAP_ZOOM = 6;

export const FEATURE_FLAGS = {
  USE_SUPABASE: import.meta.env.VITE_USE_SUPABASE === 'true',
  ENABLE_PHOTO_UPLOAD: false,   // Phase 2
  ENABLE_STATS_DASHBOARD: true,
  ENABLE_DARK_MODE: true,
  ENABLE_CLUSTERING: true
};

export const REGIONS = [
  'Hokkaido', 'Tohoku', 'Kanto', 'Chubu',
  'Kansai', 'Chugoku', 'Shikoku', 'Kyushu', 'Okinawa'
];

export const PREFECTURES = [
  'Hokkaido','Aomori','Iwate','Miyagi','Akita','Yamagata','Fukushima',
  'Ibaraki','Tochigi','Gunma','Saitama','Chiba','Tokyo','Kanagawa',
  'Niigata','Toyama','Ishikawa','Fukui','Yamanashi','Nagano','Gifu',
  'Shizuoka','Aichi','Mie','Shiga','Kyoto','Osaka','Hyogo','Nara',
  'Wakayama','Tottori','Shimane','Okayama','Hiroshima','Yamaguchi',
  'Tokushima','Kagawa','Ehime','Kochi','Fukuoka','Saga','Nagasaki',
  'Kumamoto','Oita','Miyazaki','Kagoshima','Okinawa'
];

export const VISIT_STATUS = {
  UNVISITED: 'unvisited',
  VISITED: 'visited',
  PLANNED: 'planned'
};

export const MARKER_COLORS = {
  [VISIT_STATUS.UNVISITED]: '#b23a48',
  [VISIT_STATUS.VISITED]: '#4a7c59',
  [VISIT_STATUS.PLANNED]: '#d4a017'
};

export const TORII_ICON_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="32" height="32">
  <rect x="6" y="10" width="28" height="4" rx="1" fill="{{color}}"/>
  <rect x="4" y="16" width="32" height="3" rx="1" fill="{{color}}"/>
  <rect x="10" y="10" width="4" height="24" fill="{{color}}"/>
  <rect x="26" y="10" width="4" height="24" fill="{{color}}"/>
</svg>`;

export const NOTIFICATION_DURATION_MS = 3500;
export const DEBOUNCE_DELAY_MS = 300;
