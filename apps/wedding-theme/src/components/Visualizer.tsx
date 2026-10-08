"use client";

import { useCallback, useEffect, useMemo, useState, useTransition } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { themes, getTheme } from "@/data/themes";
import type {
  CoupleDetails,
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
  { id: "table", label: "Table" },
  { id: "invitation", label: "Invite" },
  { id: "aisle", label: "Aisle" },
  { id: "bouquet", label: "Bouquet" },
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
  if (v === "invitation" || v === "aisle" || v === "bouquet" || v === "table")
    return v;
  return "table";
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
  const names = searchParams.get("names") ?? "";
  const date = searchParams.get("date") ?? "";

  const [styleFilter, setStyleFilter] = useState<StyleTag | "all">("all");
  const [seasonFilter, setSeasonFilter] = useState<SeasonTag | "all">("all");
  const [venueFilter, setVenueFilter] = useState<VenueTag | "all">("all");
  const [highlight, setHighlight] = useState<string | null>(null);
  const [compareId, setCompareId] = useState<string | null>(null);
  const [holdingCompare, setHoldingCompare] = useState(false);
  const [copied, setCopied] = useState(false);
  const [nameDraft, setNameDraft] = useState(names);
  const [dateDraft, setDateDraft] = useState(date);

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
      const q = next.toString();
      startTransition(() => {
        router.replace(q ? `${pathname}?${q}` : pathname, { scroll: false });
      });
    },
    [pathname, router, searchParams, startTransition],
  );

  useEffect(() => {
    setNameDraft(names);
    setDateDraft(date);
  }, [names, date]);

  useEffect(() => {
    if (!highlight) return;
    const t = window.setTimeout(() => setHighlight(null), 1600);
    return () => window.clearTimeout(t);
  }, [highlight]);

  // Keep active theme visible if filters hide it
  useEffect(() => {
    if (filtered.length && !filtered.some((t) => t.id === theme.id)) {
      setParams({ theme: filtered[0].id });
    }
  }, [filtered, theme.id, setParams]);

  const couple: CoupleDetails = {
    names: nameDraft,
    date: dateDraft,
  };

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
          <p className="eyebrow">Wedding theme visualizer</p>
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

      <section className="hero-stage" aria-label="Theme preview">
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
            couple={couple}
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
          <p className="eyebrow">Your palette</p>
          <h2 className="theme-title">{theme.name}</h2>
          <p className="theme-mood">{theme.mood}</p>

          <WeightedBar
            palette={theme.palette}
            activeSurface={highlight}
            onSelect={setHighlight}
          />

          <div className="moment-row" role="tablist" aria-label="Moments">
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

      <section className="details" aria-label="Personalize and materials">
        <div className="couple-form">
          <p className="eyebrow">On the invitation</p>
          <h3>Make it yours</h3>
          <p className="detail-lead">
            Names and date print on the invite moment — so the share link feels
            like your day.
          </p>
          <label>
            <span>Names</span>
            <input
              value={nameDraft}
              placeholder="Amara & James"
              onChange={(e) => setNameDraft(e.target.value)}
              onBlur={() => setParams({ names: nameDraft || null })}
            />
          </label>
          <label>
            <span>Date</span>
            <input
              value={dateDraft}
              placeholder="14 · 06 · 2027"
              onChange={(e) => setDateDraft(e.target.value)}
              onBlur={() => setParams({ date: dateDraft || null })}
            />
          </label>
        </div>

        <div className="materials">
          <p className="eyebrow">Materials</p>
          <h3>{theme.name}</h3>
          <dl>
            <div>
              <dt>Florals</dt>
              <dd>{theme.florals}</dd>
            </div>
            <div>
              <dt>Fabrics</dt>
              <dd>{theme.fabrics}</dd>
            </div>
            <div>
              <dt>Metals</dt>
              <dd>{theme.metal}</dd>
            </div>
            <div>
              <dt>Paper</dt>
              <dd>{theme.paper}</dd>
            </div>
            <div>
              <dt>Tableware</dt>
              <dd>{theme.tableware}</dd>
            </div>
          </dl>
        </div>
      </section>

      <footer className="atelier-foot">
        <p>
          Atelier · curated wedding themes · share the link with your florist
        </p>
      </footer>
    </div>
  );
}
