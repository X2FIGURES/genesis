import type { Theme } from "@/lib/types";

/**
 * Theme = the colors the wedding party wears.
 * Surfaces: dress (bridesmaids) · suit · tie · pocket · boutonniere
 * Seeded from Themes & Palettes theme rows (attire-first).
 */
export const themes: Theme[] = [
  {
    id: "garden-sage",
    name: "Garden Sage",
    mood: "Soft greens on the girls, champagne accents on the guys.",
    styleTags: ["garden"],
    seasons: ["spring", "summer"],
    venues: ["garden", "barn"],
    palette: [
      { name: "Sage dress", hex: "#9DAE8F", weight: 40, surface: "dress" },
      { name: "Stone suit", hex: "#6E6A63", weight: 28, surface: "suit" },
      { name: "Champagne tie", hex: "#C9AE7C", weight: 14, surface: "tie" },
      { name: "Ivory pocket", hex: "#F4EFE6", weight: 10, surface: "pocket" },
      { name: "Olive boutonniere", hex: "#7E9272", weight: 8, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Sage midi or floor-length, soft A-line",
      fabric: "Chiffon or soft crepe",
    },
    groomsmen: {
      suit: "Stone or warm grey suit",
      accessories: "Champagne tie, ivory pocket square, olive boutonniere",
    },
    florals: "Eucalyptus, olive, garden roses",
  },
  {
    id: "blush-champagne",
    name: "Blush Champagne",
    mood: "Dusty rose dresses, warm champagne on the groomsmen.",
    styleTags: ["classic", "intimate"],
    seasons: ["spring", "autumn"],
    venues: ["ballroom", "garden", "intimate"],
    palette: [
      { name: "Dusty rose", hex: "#D8A9A4", weight: 42, surface: "dress" },
      { name: "Warm taupe suit", hex: "#8A7A6E", weight: 26, surface: "suit" },
      { name: "Champagne tie", hex: "#E8D7B9", weight: 14, surface: "tie" },
      { name: "Blush pocket", hex: "#E8C4BE", weight: 10, surface: "pocket" },
      { name: "Rose boutonniere", hex: "#C99A9E", weight: 8, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Dusty rose — mix of necklines, same color",
      fabric: "Satin or chiffon",
    },
    groomsmen: {
      suit: "Warm taupe or soft mocha",
      accessories: "Champagne tie, blush pocket, rose boutonniere",
    },
    florals: "Garden roses, peonies, dusty miller",
  },
  {
    id: "midnight-ink",
    name: "Midnight Ink",
    mood: "Evening black-tie energy — muted rose on the girls, ink on the guys.",
    styleTags: ["modern", "classic"],
    seasons: ["autumn", "winter"],
    venues: ["ballroom", "rooftop"],
    palette: [
      { name: "Muted rose", hex: "#B98C88", weight: 36, surface: "dress" },
      { name: "Ink suit", hex: "#1C1A1E", weight: 32, surface: "suit" },
      { name: "Champagne tie", hex: "#D8C29C", weight: 14, surface: "tie" },
      { name: "Ivory pocket", hex: "#F2EBDF", weight: 10, surface: "pocket" },
      { name: "Dark rose pin", hex: "#8E6562", weight: 8, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Muted rose — sleek column or soft bias",
      fabric: "Satin or crepe",
    },
    groomsmen: {
      suit: "Black or near-ink three-piece / dinner jacket",
      accessories: "Champagne tie or bow, ivory pocket, dark rose boutonniere",
    },
    florals: "Dark roses, anemone, eucalyptus",
  },
  {
    id: "citrus-riviera",
    name: "Citrus Riviera",
    mood: "Beach-club bright — lemon-kissed dresses, cream or light navy suits.",
    styleTags: ["modern", "garden"],
    seasons: ["summer"],
    venues: ["beach", "garden", "rooftop"],
    palette: [
      { name: "Sea-salt dress", hex: "#E8F0EC", weight: 34, surface: "dress" },
      { name: "Cream suit", hex: "#F3EAD7", weight: 28, surface: "suit" },
      { name: "Navy tie", hex: "#34507A", weight: 16, surface: "tie" },
      { name: "Powder pocket", hex: "#B7CCE3", weight: 12, surface: "pocket" },
      { name: "Citrus pin", hex: "#E9A23B", weight: 10, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Sea-salt or soft citrus mist — light and breezy",
      fabric: "Linen-blend or chiffon",
    },
    groomsmen: {
      suit: "Cream double-breasted or light navy / powder blue",
      accessories: "Navy tie, powder pocket, citrus or floral pin, tan loafers",
    },
    florals: "Lemon branches, marigolds, white bougainvillea",
  },
  {
    id: "chartreuse-burgundy",
    name: "Chartreuse & Burgundy",
    mood: "High-contrast fashion — chartreuse or blush on girls, wine on the guys.",
    styleTags: ["modern"],
    seasons: ["autumn", "winter"],
    venues: ["ballroom", "rooftop"],
    palette: [
      { name: "Blush dress", hex: "#E8C4C0", weight: 34, surface: "dress" },
      { name: "Wine suit", hex: "#5E1A2B", weight: 30, surface: "suit" },
      { name: "Gold tie", hex: "#C9A24B", weight: 14, surface: "tie" },
      { name: "Cream pocket", hex: "#F6EFE2", weight: 12, surface: "pocket" },
      { name: "Chartreuse pin", hex: "#B5C21E", weight: 10, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Blush or soft chartreuse — statement color, clean cut",
      fabric: "Taffeta, velvet accents, or crepe",
    },
    groomsmen: {
      suit: "Wine-lees burgundy (or aubergine) — double-breasted welcome",
      accessories: "Gold accents, cream pocket, chartreuse or gold pin",
    },
    florals: "Burgundy dahlias, green hellebores, chartreuse amaranthus",
  },
  {
    id: "ivory-classic",
    name: "Ivory Classic",
    mood: "Timeless — soft ivory/pearl dresses, charcoal or black suits.",
    styleTags: ["classic"],
    seasons: ["all"],
    venues: ["ballroom", "garden"],
    palette: [
      { name: "Pearl dress", hex: "#E8E0D4", weight: 40, surface: "dress" },
      { name: "Charcoal suit", hex: "#3A3632", weight: 30, surface: "suit" },
      { name: "Champagne tie", hex: "#C9AE7C", weight: 14, surface: "tie" },
      { name: "White pocket", hex: "#FBFAF7", weight: 10, surface: "pocket" },
      { name: "White rose", hex: "#F0E6D4", weight: 6, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Pearl / soft ivory — classic silhouette",
      fabric: "Chiffon or satin",
    },
    groomsmen: {
      suit: "Charcoal or black",
      accessories: "Champagne tie, white linen pocket (TV fold), white rose",
    },
    florals: "White roses, spray roses, greenery",
  },
  {
    id: "swan-ballet",
    name: "Swan Lake",
    mood: "Balletcore soft pinks with black-tie groomsmen.",
    styleTags: ["classic", "intimate"],
    seasons: ["spring", "winter"],
    venues: ["ballroom", "intimate"],
    palette: [
      { name: "Tutu pink", hex: "#F1E6E3", weight: 38, surface: "dress" },
      { name: "Black suit", hex: "#111111", weight: 30, surface: "suit" },
      { name: "Black bow", hex: "#1C1C1C", weight: 12, surface: "tie" },
      { name: "Ivory pocket", hex: "#F6F1E5", weight: 12, surface: "pocket" },
      { name: "Blush pin", hex: "#E8C4C4", weight: 8, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Tutu pink / soft blush — romantic, light",
      fabric: "Tulle, satin ribbon details",
    },
    groomsmen: {
      suit: "Black dinner jacket or three-piece",
      accessories: "Self-tied black bow, ivory pocket, blush accent pin",
    },
    florals: "Peonies, white anemones, ranunculus",
  },
  {
    id: "terracotta-grove",
    name: "Terracotta Grove",
    mood: "Warm earth — terracotta dresses, sand or olive suits.",
    styleTags: ["garden", "intimate"],
    seasons: ["summer", "autumn"],
    venues: ["garden", "barn"],
    palette: [
      { name: "Terracotta dress", hex: "#C4785A", weight: 40, surface: "dress" },
      { name: "Sand suit", hex: "#B48A60", weight: 26, surface: "suit" },
      { name: "Olive tie", hex: "#8A9A6E", weight: 14, surface: "tie" },
      { name: "Clay pocket", hex: "#EFE4D6", weight: 12, surface: "pocket" },
      { name: "Dried citrus", hex: "#C9A66B", weight: 8, surface: "boutonniere" },
    ],
    bridesmaid: {
      dress: "Terracotta — earthy, gathered or wrap",
      fabric: "Linen or soft crepe",
    },
    groomsmen: {
      suit: "Sand / stone linen or light wool",
      accessories: "Olive tie, clay pocket, dried citrus or olive pin",
    },
    florals: "Dried citrus, olive, terracotta roses",
  },
];

export function getTheme(id: string | null | undefined): Theme {
  return themes.find((t) => t.id === id) ?? themes[0];
}
