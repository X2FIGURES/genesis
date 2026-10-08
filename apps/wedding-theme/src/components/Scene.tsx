"use client";

import type { AttireSurface, Lighting, Moment, Theme } from "@/lib/types";

type Props = {
  theme: Theme;
  moment: Moment;
  lighting: Lighting;
  highlightSurface?: AttireSurface | null;
  compareTheme?: Theme | null;
  holdingCompare?: boolean;
};

function colors(theme: Theme) {
  const p = theme.palette;
  const get = (s: AttireSurface, fallback: number) =>
    p.find((c) => c.surface === s)?.hex ?? p[fallback]?.hex ?? "#ccc";
  return {
    dress: get("dress", 0),
    suit: get("suit", 1),
    tie: get("tie", 2),
    pocket: get("pocket", 3),
    boutonniere: get("boutonniere", 4),
    skin: "#E8D5C4",
    hair: "#3A2F2A",
    shirt: "#F7F3EC",
  };
}

function LightingWash({ lighting }: { lighting: Lighting }) {
  if (lighting === "daylight") return null;
  if (lighting === "golden") {
    return (
      <rect
        width="1200"
        height="800"
        fill="#E8B86D"
        opacity="0.16"
        style={{ mixBlendMode: "soft-light" }}
      />
    );
  }
  return (
    <>
      <rect
        width="1200"
        height="800"
        fill="#1A1210"
        opacity="0.22"
        style={{ mixBlendMode: "multiply" }}
      />
      <radialGradient id="candleGlow" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stopColor="#FFD9A0" stopOpacity="0.32" />
        <stop offset="60%" stopColor="#C4783A" stopOpacity="0.1" />
        <stop offset="100%" stopColor="#000" stopOpacity="0" />
      </radialGradient>
      <rect width="1200" height="800" fill="url(#candleGlow)" />
    </>
  );
}

function Bridesmaid({
  c,
  x,
  highlight,
  label,
}: {
  c: ReturnType<typeof colors>;
  x: number;
  highlight?: AttireSurface | null;
  label?: string;
}) {
  const dim = highlight && highlight !== "dress" ? 0.28 : 1;
  return (
    <g transform={`translate(${x} 80)`} opacity={dim} style={{ transition: "opacity 180ms ease" }}>
      {/* head */}
      <circle cx="110" cy="58" r="36" fill={c.skin} />
      <ellipse cx="110" cy="42" rx="38" ry="28" fill={c.hair} />
      {/* neck */}
      <rect x="98" y="88" width="24" height="28" fill={c.skin} />
      {/* bodice */}
      <path
        d="M55 118 C70 108 150 108 165 118 L175 210 C140 225 80 225 45 210 Z"
        fill={c.dress}
        style={{ transition: "fill 220ms ease" }}
      />
      {/* skirt — big color mass */}
      <path
        d="M45 205 C20 280 10 420 25 560 L195 560 C210 420 200 280 175 205 Z"
        fill={c.dress}
        style={{ transition: "fill 220ms ease" }}
      />
      {/* soft fold lines */}
      <path
        d="M90 220 Q100 380 85 540"
        fill="none"
        stroke="#2F2B28"
        strokeOpacity="0.08"
        strokeWidth="3"
      />
      <path
        d="M140 225 Q135 390 150 545"
        fill="none"
        stroke="#2F2B28"
        strokeOpacity="0.07"
        strokeWidth="3"
      />
      {/* arms */}
      <path
        d="M55 130 Q20 200 35 280"
        fill="none"
        stroke={c.skin}
        strokeWidth="18"
        strokeLinecap="round"
      />
      <path
        d="M165 130 Q200 200 185 280"
        fill="none"
        stroke={c.skin}
        strokeWidth="18"
        strokeLinecap="round"
      />
      {label && (
        <text
          x="110"
          y="600"
          textAnchor="middle"
          fill="#7A736C"
          fontFamily="system-ui, sans-serif"
          fontSize="18"
          letterSpacing="3"
        >
          {label}
        </text>
      )}
    </g>
  );
}

function Groomsman({
  c,
  x,
  highlight,
  label,
}: {
  c: ReturnType<typeof colors>;
  x: number;
  highlight?: AttireSurface | null;
  label?: string;
}) {
  const dimSuit =
    highlight && !["suit", "tie", "pocket", "boutonniere"].includes(highlight)
      ? 0.28
      : 1;
  const dim = (s: AttireSurface) =>
    highlight && highlight !== s ? 0.35 : 1;

  return (
    <g transform={`translate(${x} 80)`} opacity={dimSuit} style={{ transition: "opacity 180ms ease" }}>
      {/* head */}
      <circle cx="110" cy="58" r="36" fill={c.skin} />
      <path d="M72 50 Q110 10 148 50 L145 70 Q110 55 75 70 Z" fill={c.hair} />
      <rect x="98" y="88" width="24" height="26" fill={c.skin} />

      {/* jacket body */}
      <path
        d="M48 118 L55 420 L165 420 L172 118 C150 108 70 108 48 118 Z"
        fill={c.suit}
        opacity={dim("suit")}
        style={{ transition: "fill 220ms ease, opacity 180ms ease" }}
      />
      {/* lapels */}
      <path
        d="M110 118 L72 200 L110 230 Z"
        fill={c.suit}
        opacity={0.85 * dim("suit")}
        style={{ filter: "brightness(0.92)", transition: "fill 220ms ease" }}
      />
      <path
        d="M110 118 L148 200 L110 230 Z"
        fill={c.suit}
        opacity={0.85 * dim("suit")}
        style={{ filter: "brightness(0.88)", transition: "fill 220ms ease" }}
      />
      {/* shirt V */}
      <path d="M110 118 L95 200 L110 210 L125 200 Z" fill={c.shirt} />

      {/* tie — clear accent */}
      <path
        d="M110 130 L100 145 L110 280 L120 145 Z"
        fill={c.tie}
        opacity={dim("tie")}
        style={{ transition: "fill 220ms ease, opacity 180ms ease" }}
      />
      <path
        d="M100 145 L110 158 L120 145 L110 138 Z"
        fill={c.tie}
        opacity={dim("tie")}
        style={{ transition: "fill 220ms ease" }}
      />

      {/* pocket square */}
      <rect
        x="138"
        y="195"
        width="22"
        height="14"
        fill={c.pocket}
        opacity={dim("pocket")}
        style={{ transition: "fill 220ms ease, opacity 180ms ease" }}
      />
      <path
        d="M138 195 L149 185 L160 195"
        fill={c.pocket}
        opacity={dim("pocket")}
      />

      {/* boutonniere */}
      <g opacity={dim("boutonniere")} style={{ transition: "opacity 180ms ease" }}>
        <circle cx="68" cy="175" r="14" fill={c.boutonniere} style={{ transition: "fill 220ms ease" }} />
        <circle cx="78" cy="168" r="9" fill={c.tie} opacity="0.7" />
        <rect x="64" y="186" width="4" height="22" fill="#6B8A5E" rx="1" />
      </g>

      {/* trousers */}
      <path
        d="M55 418 L50 560 L100 560 L110 430 L120 560 L170 560 L165 418 Z"
        fill={c.suit}
        opacity={0.92 * dim("suit")}
        style={{ transition: "fill 220ms ease" }}
      />

      {/* arms */}
      <path
        d="M52 130 Q18 210 40 300"
        fill="none"
        stroke={c.suit}
        strokeWidth="22"
        strokeLinecap="round"
        opacity={dim("suit")}
      />
      <path
        d="M168 130 Q202 210 180 300"
        fill="none"
        stroke={c.suit}
        strokeWidth="22"
        strokeLinecap="round"
        opacity={dim("suit")}
      />
      <circle cx="40" cy="308" r="12" fill={c.skin} />
      <circle cx="180" cy="308" r="12" fill={c.skin} />

      {label && (
        <text
          x="110"
          y="600"
          textAnchor="middle"
          fill="#7A736C"
          fontFamily="system-ui, sans-serif"
          fontSize="18"
          letterSpacing="3"
        >
          {label}
        </text>
      )}
    </g>
  );
}

export function Scene({
  theme,
  moment,
  lighting,
  highlightSurface,
  compareTheme,
  holdingCompare,
}: Props) {
  const active = holdingCompare && compareTheme ? compareTheme : theme;
  const c = colors(active);

  return (
    <div className="scene-frame relative h-full w-full overflow-hidden">
      <svg
        viewBox="0 0 1200 800"
        className="h-full w-full"
        preserveAspectRatio="xMidYMid slice"
        role="img"
        aria-label={`${active.name} wedding party attire`}
      >
        {/* calm linen ground */}
        <rect width="1200" height="800" fill="#EDE6DA" />
        <rect width="1200" height="800" fill={c.dress} opacity="0.08" />
        <ellipse cx="600" cy="720" rx="420" ry="36" fill="#2F2B28" opacity="0.05" />

        {moment === "party" && (
          <>
            <Bridesmaid c={c} x={250} highlight={highlightSurface} label="BRIDESMAID" />
            <Groomsman c={c} x={720} highlight={highlightSurface} label="GROOMSMAN" />
          </>
        )}
        {moment === "bridesmaids" && (
          <>
            <Bridesmaid c={c} x={160} highlight={highlightSurface} />
            <Bridesmaid c={c} x={430} highlight={highlightSurface} label="BRIDESMAIDS" />
            <Bridesmaid c={c} x={700} highlight={highlightSurface} />
          </>
        )}
        {moment === "groomsmen" && (
          <>
            <Groomsman c={c} x={160} highlight={highlightSurface} />
            <Groomsman c={c} x={430} highlight={highlightSurface} label="GROOMSMEN" />
            <Groomsman c={c} x={700} highlight={highlightSurface} />
          </>
        )}

        <LightingWash lighting={lighting} />
      </svg>
      <div className="scene-grain pointer-events-none absolute inset-0" />
    </div>
  );
}
