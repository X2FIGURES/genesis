"use client";

import type { PaletteColor } from "@/lib/types";

type Props = {
  palette: PaletteColor[];
  activeSurface?: string | null;
  onSelect: (surface: string) => void;
};

export function WeightedBar({ palette, activeSurface, onSelect }: Props) {
  return (
    <div className="weighted-bar">
      <div
        className="weighted-track"
        role="listbox"
        aria-label="Palette by how much each color is used"
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
              style={{
                flexGrow: c.weight,
                background: c.hex,
              }}
              title={`${c.name} · ${c.weight}% · ${c.surface}`}
              onClick={() => onSelect(c.surface)}
            >
              <span className="sr-only">
                {c.name}, {c.weight} percent, used on {c.surface}
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
                {c.name}
                <em>{c.weight}%</em>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
