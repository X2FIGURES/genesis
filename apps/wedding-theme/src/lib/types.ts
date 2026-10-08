export type Lighting = "daylight" | "golden" | "candle";

/** What the bride is trying to lock — the wedding party look. */
export type Moment = "party" | "bridesmaids" | "groomsmen";

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

export type AttireSurface =
  | "dress"
  | "suit"
  | "tie"
  | "pocket"
  | "boutonniere";

export type PaletteColor = {
  name: string;
  hex: string;
  /** Share of the look, roughly 60/30/10. Sum ≈ 100. */
  weight: number;
  surface: AttireSurface;
};

export type Theme = {
  id: string;
  name: string;
  mood: string;
  styleTags: StyleTag[];
  seasons: SeasonTag[];
  venues: VenueTag[];
  /** Party palette — dress + suit + accessories. */
  palette: PaletteColor[];
  bridesmaid: {
    dress: string;
    fabric: string;
  };
  groomsmen: {
    suit: string;
    accessories: string;
  };
  florals: string;
};

export type CoupleDetails = {
  names: string;
  date: string;
};
