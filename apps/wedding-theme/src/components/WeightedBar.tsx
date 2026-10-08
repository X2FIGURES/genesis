"use client";

import type { AttireSurface, PaletteColor } from "@/lib/types";

const SURFACE_LABEL: Record<AttireSurface, string> = {
  dress: "Bridesmaid dress",
  suit: "Suit",
  tie: "Tie / bow",
  pocket: "Pocket square",
  boutonniere: "Boutonniere",
};

type Props = {
  palette: PaletteColor[];
  activeSurface?: AttireSurface | null;
  onSelect: (surface: AttireSurface) => void;
};

export function WeightedBar({ palette, activeSurface, onSelect }: Props) {
  return (
    <div className="weighted-bar">
      <div
        className="weighted-track"
        role="listbox"
        aria-label="Who wears each color"
      >
        {palette.map((c) => {
          const on = activeSurface === c.surface;
          return (
            <button
              key={c.hex + c.name}
              type="button"
              role="option"
              aria-selected={on}
              className={`weighted-swatch${on ? " is-on" : ""}`}
              style={{ flexGrow: c.weight, background: c.hex }}
              title={`${c.name} · ${SURFACE_LABEL[c.surface]} · ${c.weight}%`}
              onClick={() => onSelect(c.surface)}
            >
              <span className="sr-only">
                {c.name} on {SURFACE_LABEL[c.surface]}, {c.weight} percent
              </span>
            </button>
          );
        })}
      </div>
      <ul className="weighted-legend">
        {palette.map((c) => (
          <li key={c.name}>
            <button
              type="button"
              className={activeSurface === c.surface ? "is-on" : undefined}
              onClick={() => onSelect(c.surface)}
            >
              <i style={{ background: c.hex }} aria-hidden />
              <span>
                {SURFACE_LABEL[c.surface]}
                <em>{c.name}</em>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
