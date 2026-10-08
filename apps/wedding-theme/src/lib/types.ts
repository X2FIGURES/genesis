export type Lighting = "daylight" | "golden" | "candle";

export type Moment = "table" | "invitation" | "aisle" | "bouquet";

export type StyleTag = "garden" | "modern" | "classic" | "intimate";

export type SeasonTag =
  | "spring"
  | "summer"
  | "autumn"
  | "winter"
  | "all";

export type VenueTag =
  | "garden"
  | "ballroom"
  | "barn"
  | "beach"
  | "rooftop"
  | "intimate";

export type PaletteColor = {
  name: string;
  hex: string;
  /** Share of the palette, roughly 60/30/10 style. Sum ≈ 100. */
  weight: number;
  surface: string;
};

export type Theme = {
  id: string;
  name: string;
  mood: string;
  styleTags: StyleTag[];
  seasons: SeasonTag[];
  venues: VenueTag[];
  palette: PaletteColor[];
  metal: string;
  paper: string;
  florals: string;
  fabrics: string;
  tableware: string;
};

export type CoupleDetails = {
  names: string;
  date: string;
};
