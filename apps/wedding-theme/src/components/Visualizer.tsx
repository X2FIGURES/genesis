"use client";

import { useCallback, useEffect, useMemo, useState, useTransition } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { themes, getTheme } from "@/data/themes";
import type {
  AttireSurface,
  Lighting,
  Moment,
  SeasonTag,
  StyleTag,
  VenueTag,
} from "@/lib/types";
import { Scene } from "./Scene";
import { ThemeRail } from "./ThemeRail";
import { WeightedBar } from "./WeightedBar";

const MOMENTS: { id: Moment; label: string }[] = [
  { id: "party", label: "Party" },
  { id: "bridesmaids", label: "Bridesmaids" },
  { id: "groomsmen", label: "Groomsmen" },
];

const LIGHTING: { id: Lighting; label: string }[] = [
  { id: "daylight", label: "Daylight" },
  { id: "golden", label: "Golden hour" },
  { id: "candle", label: "Candlelight" },
];

const STYLES: { id: StyleTag | "all"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "garden", label: "Garden" },
  { id: "modern", label: "Modern" },
  { id: "classic", label: "Classic" },
  { id: "intimate", label: "Intimate" },
];

const SEASONS: { id: SeasonTag | "all"; label: string }[] = [
  { id: "all", label: "Any season" },
  { id: "spring", label: "Spring" },
  { id: "summer", label: "Summer" },
  { id: "autumn", label: "Autumn" },
  { id: "winter", label: "Winter" },
];

const VENUES: { id: VenueTag | "all"; label: string }[] = [
  { id: "all", label: "Any venue" },
  { id: "garden", label: "Garden" },
  { id: "ballroom", label: "Ballroom" },
  { id: "barn", label: "Barn" },
  { id: "beach", label: "Beach" },
  { id: "rooftop", label: "Rooftop" },
  { id: "intimate", label: "Intimate" },
];

function parseMoment(v: string | null): Moment {
  if (v === "bridesmaids" || v === "groomsmen" || v === "party") return v;
  return "party";
}

function parseLighting(v: string | null): Lighting {
  if (v === "golden" || v === "candle" || v === "daylight") return v;
  return "daylight";
}

export function Visualizer() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [, startTransition] = useTransition();

  const themeId = searchParams.get("theme") ?? themes[0].id;
  const moment = parseMoment(searchParams.get("moment"));
  const lighting = parseLighting(searchParams.get("light"));

  const [styleFilter, setStyleFilter] = useState<StyleTag | "all">("all");
  const [seasonFilter, setSeasonFilter] = useState<SeasonTag | "all">("all");
  const [venueFilter, setVenueFilter] = useState<VenueTag | "all">("all");
  const [highlight, setHighlight] = useState<AttireSurface | null>(null);
  const [compareId, setCompareId] = useState<string | null>(null);
  const [holdingCompare, setHoldingCompare] = useState(false);
  const [copied, setCopied] = useState(false);

  const theme = getTheme(themeId);
  const compareTheme = compareId ? getTheme(compareId) : null;

  const filtered = useMemo(() => {
    return themes.filter((t) => {
      if (styleFilter !== "all" && !t.styleTags.includes(styleFilter))
        return false;
      if (
        seasonFilter !== "all" &&
        !t.seasons.includes(seasonFilter) &&
        !t.seasons.includes("all")
      )
        return false;
      if (venueFilter !== "all" && !t.venues.includes(venueFilter)) return false;
      return true;
    });
  }, [styleFilter, seasonFilter, venueFilter]);

  const setParams = useCallback(
    (patch: Record<string, string | null>) => {
      const next = new URLSearchParams(searchParams.toString());
      Object.entries(patch).forEach(([k, v]) => {
        if (v == null || v === "") next.delete(k);
        else next.set(k, v);
      });
      // Drop legacy invite params if present
      next.delete("names");
      next.delete("date");
      const q = next.toString();
      startTransition(() => {
        router.replace(q ? `${pathname}?${q}` : pathname, { scroll: false });
      });
    },
    [pathname, router, searchParams, startTransition],
  );

  useEffect(() => {
    if (!highlight) return;
    const t = window.setTimeout(() => setHighlight(null), 1800);
    return () => window.clearTimeout(t);
  }, [highlight]);

  useEffect(() => {
    if (filtered.length && !filtered.some((t) => t.id === theme.id)) {
      setParams({ theme: filtered[0].id });
    }
  }, [filtered, theme.id, setParams]);

  async function share() {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      window.prompt("Copy this link", url);
    }
  }

  function onThemeSelect(id: string) {
    if (compareId && id !== theme.id && id !== compareId) {
      setCompareId(id);
    }
    setParams({ theme: id });
  }

  function toggleCompare() {
    if (compareId) {
      setCompareId(null);
      setHoldingCompare(false);
      return;
    }
    const other = filtered.find((t) => t.id !== theme.id) ?? themes[1];
    setCompareId(other.id);
  }

  return (
    <div className="atelier">
      <header className="atelier-top">
        <div className="brand-block">
          <p className="eyebrow">Wedding party colors</p>
          <h1 className="brand">Atelier</h1>
        </div>
        <div className="top-actions">
          <button type="button" className="ghost-btn" onClick={toggleCompare}>
            {compareId ? "Exit compare" : "Compare"}
          </button>
          <button type="button" className="share-btn" onClick={share}>
            {copied ? "Link copied" : "Share look"}
          </button>
        </div>
      </header>

      <section className="hero-stage" aria-label="Party attire preview">
        <div
          className="scene-shell"
          onPointerDown={() => {
            if (compareId) setHoldingCompare(true);
          }}
          onPointerUp={() => setHoldingCompare(false)}
          onPointerLeave={() => setHoldingCompare(false)}
          onPointerCancel={() => setHoldingCompare(false)}
        >
          <Scene
            theme={theme}
            moment={moment}
            lighting={lighting}
            highlightSurface={highlight}
            compareTheme={compareTheme}
            holdingCompare={holdingCompare}
          />
          {compareId && (
            <p className="compare-hint">
              Hold to flip · {holdingCompare ? compareTheme?.name : theme.name}
            </p>
          )}
        </div>

        <div className="hero-meta">
          <p className="eyebrow">This theme dresses as</p>
          <h2 className="theme-title">{theme.name}</h2>
          <p className="theme-mood">{theme.mood}</p>

          <WeightedBar
            palette={theme.palette}
            activeSurface={highlight}
            onSelect={setHighlight}
          />

          <div className="moment-row" role="tablist" aria-label="Who to preview">
            {MOMENTS.map((m) => (
              <button
                key={m.id}
                type="button"
                role="tab"
                aria-selected={moment === m.id}
                className={moment === m.id ? "is-on" : undefined}
                onClick={() => setParams({ moment: m.id })}
              >
                {m.label}
              </button>
            ))}
          </div>

          <div className="light-row" role="radiogroup" aria-label="Lighting">
            {LIGHTING.map((l) => (
              <button
                key={l.id}
                type="button"
                role="radio"
                aria-checked={lighting === l.id}
                className={lighting === l.id ? "is-on" : undefined}
                onClick={() => setParams({ light: l.id })}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="controls" aria-label="Filters and themes">
        <div className="filter-row">
          <label>
            <span>Style</span>
            <select
              value={styleFilter}
              onChange={(e) =>
                setStyleFilter(e.target.value as StyleTag | "all")
              }
            >
              {STYLES.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Season</span>
            <select
              value={seasonFilter}
              onChange={(e) =>
                setSeasonFilter(e.target.value as SeasonTag | "all")
              }
            >
              {SEASONS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Venue</span>
            <select
              value={venueFilter}
              onChange={(e) =>
                setVenueFilter(e.target.value as VenueTag | "all")
              }
            >
              {VENUES.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <ThemeRail
          themes={filtered}
          activeId={theme.id}
          compareId={compareId}
          onSelect={onThemeSelect}
        />
      </section>

      <section className="details" aria-label="Attire details">
        <div className="materials">
          <p className="eyebrow">Bridesmaids</p>
          <h3>The dresses</h3>
          <dl>
            <div>
              <dt>Look</dt>
              <dd>{theme.bridesmaid.dress}</dd>
            </div>
            <div>
              <dt>Fabric</dt>
              <dd>{theme.bridesmaid.fabric}</dd>
            </div>
            <div>
              <dt>Florals with them</dt>
              <dd>{theme.florals}</dd>
            </div>
          </dl>
        </div>

        <div className="materials">
          <p className="eyebrow">Groomsmen</p>
          <h3>The suits</h3>
          <dl>
            <div>
              <dt>Suit</dt>
              <dd>{theme.groomsmen.suit}</dd>
            </div>
            <div>
              <dt>Accessories</dt>
              <dd>{theme.groomsmen.accessories}</dd>
            </div>
          </dl>
        </div>
      </section>

      <footer className="atelier-foot">
        <p>
          Atelier · lock the party colors · share with your tailor and dress shop
        </p>
      </footer>
    </div>
  );
}
