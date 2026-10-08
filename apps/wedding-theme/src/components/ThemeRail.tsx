"use client";

import type { Theme } from "@/lib/types";

type Props = {
  themes: Theme[];
  activeId: string;
  onSelect: (id: string) => void;
  compareId?: string | null;
};

export function ThemeRail({ themes, activeId, onSelect, compareId }: Props) {
  return (
    <div className="theme-rail" role="listbox" aria-label="Wedding themes">
      {themes.map((t) => {
        const on = t.id === activeId;
        const isCompare = t.id === compareId;
        return (
          <button
            key={t.id}
            type="button"
            role="option"
            aria-selected={on}
            className={`theme-chip${on ? " is-on" : ""}${isCompare ? " is-compare" : ""}`}
            onClick={() => onSelect(t.id)}
          >
            <span className="theme-chip-swatches" aria-hidden>
              {t.palette.slice(0, 4).map((c) => (
                <i key={c.hex} style={{ background: c.hex }} />
              ))}
            </span>
            <span className="theme-chip-name">{t.name}</span>
          </button>
        );
      })}
    </div>
  );
}
