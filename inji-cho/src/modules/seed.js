// ===== Seed Data: 20 real temples across Japan =====
// Coordinates from publicly known locations. Used to bootstrap the demo on
// first load (or any time the user clicks "Reset to demo" in About modal).

export const SEED_TEMPLES = [
  {
    name: 'Sensō-ji',
    prefecture: 'Tokyo',
    region: 'Asakusa',
    lat: 35.7148, lng: 139.7967,
    notes: 'Tokyo\'s oldest temple, founded 645 AD. Iconic Kaminarimon gate and Nakamise shopping street.',
    visited: true,
  },
  {
    name: 'Meiji Jingū',
    prefecture: 'Tokyo',
    region: 'Shibuya',
    lat: 35.6764, lng: 139.6993,
    notes: 'Shinto shrine dedicated to Emperor Meiji. Forest park with 100,000 donated trees.',
    visited: true,
  },
  {
    name: 'Fushimi Inari Taisha',
    prefecture: 'Kyoto',
    region: 'Fushimi',
    lat: 34.9671, lng: 135.7727,
    notes: 'Famous for thousands of vermilion torii gates winding up Mount Inari.',
    visited: true,
  },
  {
    name: 'Kinkaku-ji (Golden Pavilion)',
    prefecture: 'Kyoto',
    region: 'Kita-ku',
    lat: 35.0394, lng: 135.7292,
    notes: 'Zen Buddhist temple covered in gold leaf, reflected in the kyōko-chi pond.',
    visited: false,
  },
  {
    name: 'Kiyomizu-dera',
    prefecture: 'Kyoto',
    region: 'Higashiyama',
    lat: 34.9949, lng: 135.7850,
    notes: 'Famous wooden stage perched on the hillside, with sweeping views of Kyoto.',
    visited: true,
  },
  {
    name: 'Tōdai-ji',
    prefecture: 'Nara',
    region: 'Nara',
    lat: 34.6892, lng: 135.8398,
    notes: 'Great Buddha (Daibutsu) housed in one of the world\'s largest wooden buildings.',
    visited: false,
  },
  {
    name: 'Kasuga Taisha',
    prefecture: 'Nara',
    region: 'Nara',
    lat: 34.6760, lng: 135.8484,
    notes: 'Famous shrine with ~3000 bronze and stone lanterns lining the approach.',
    visited: false,
  },
  {
    name: 'Hōryū-ji',
    prefecture: 'Nara',
    region: 'Ikaruga',
    lat: 34.6144, lng: 135.7334,
    notes: 'World\'s oldest surviving wooden structures (early 7th century).',
    visited: false,
  },
  {
    name: 'Itsukushima Shrine',
    prefecture: 'Hiroshima',
    region: 'Miyajima',
    lat: 34.2958, lng: 132.3197,
    notes: 'Famous floating torii gate in Hiroshima Bay. UNESCO World Heritage.',
    visited: false,
  },
  {
    name: 'Hiroshima Peace Memorial',
    prefecture: 'Hiroshima',
    region: 'Naka-ku',
    lat: 34.3955, lng: 132.4536,
    notes: 'Genbaku Dome, preserved at hypocenter of 1945 atomic bombing.',
    visited: false,
  },
  {
    name: 'Kōyasan (Okunoin)',
    prefecture: 'Wakayama',
    region: 'Kōya',
    lat: 34.2127, lng: 135.5866,
    notes: 'Mount Kōya, headquarters of Shingon Buddhism. Mausoleum of Kūkai under ancient cedars.',
    visited: false,
  },
  {
    name: 'Kumamoto Castle',
    prefecture: 'Kumamoto',
    region: 'Chūō-ku',
    lat: 32.8067, lng: 130.7056,
    notes: 'One of Japan\'s most famous castles (shrine grounds within complex).',
    visited: false,
  },
  {
    name: 'Dazaifu Tenmangū',
    prefecture: 'Fukuoka',
    region: 'Dazaifu',
    lat: 33.5223, lng: 130.5312,
    notes: 'Shinto shrine dedicated to Sugawara no Michizane, deity of learning.',
    visited: false,
  },
  {
    name: 'Hakone Shrine',
    prefecture: 'Kanagawa',
    region: 'Hakone',
    lat: 35.2328, lng: 139.0243,
    notes: 'Famous torii gate on the shores of Lake Ashi, gateway to Mt. Fuji views.',
    visited: true,
  },
  {
    name: 'Zenkō-ji',
    prefecture: 'Nagano',
    region: 'Nagano',
    lat: 36.6614, lng: 138.1873,
    notes: 'One of the oldest Buddhist temples in Japan, founded in the 7th century.',
    visited: false,
  },
  {
    name: 'Sapporo Hokkaidō Jingū',
    prefecture: 'Hokkaido',
    region: 'Sapporo',
    lat: 43.0564, lng: 141.3053,
    notes: 'Major Shinto shrine in Sapporo, surrounded by a quiet urban forest.',
    visited: false,
  },
  {
    name: 'Tsukiji Hongan-ji',
    prefecture: 'Tokyo',
    region: 'Chūō-ku',
    lat: 35.6654, lng: 139.7710,
    notes: 'Pure Land Buddhist temple with striking modern stone architecture.',
    visited: true,
  },
  {
    name: 'Nikkō Tōshō-gū',
    prefecture: 'Tochigi',
    region: 'Nikkō',
    lat: 36.7580, lng: 139.5993,
    notes: 'Lavishly decorated shrine-mausoleum of Tokugawa Ieyasu, UNESCO site.',
    visited: false,
  },
  {
    name: 'Ryoan-ji',
    prefecture: 'Kyoto',
    region: 'Ukyō-ku',
    lat: 35.0399, lng: 135.7180,
    notes: 'Famous Zen rock garden with 15 stones on white sand.',
    visited: true,
  },
  {
    name: 'Shirakawa-gō (Shirakawa Hachiman)',
    prefecture: 'Gifu',
    region: 'Shirakawa',
    lat: 36.2582, lng: 136.9055,
    notes: 'UNESCO village of gasshō-zukuri farmhouses with adjacent historic shrine.',
    visited: false,
  },
];

/**
 * Optionally enrich seed temples with timestamps + deterministic IDs.
 * Used when injecting seed data so the resulting records look like user
 * data with stable IDs.
 */
export function buildSeedTemples() {
  return SEED_TEMPLES.map((t, i) => ({
    ...t,
    id: `seed_${String(i + 1).padStart(2, '0')}`,
    visitDate: t.visited ? new Date(Date.now() - (i + 1) * 86400000 * 30).toISOString() : null,
    createdAt: new Date(Date.now() - (SEED_TEMPLES.length - i) * 86400000 * 7).toISOString(),
    updatedAt: new Date().toISOString(),
  }));
}
