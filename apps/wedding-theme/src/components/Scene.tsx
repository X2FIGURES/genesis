"use client";

import type { CoupleDetails, Lighting, Moment, Theme } from "@/lib/types";

type Props = {
  theme: Theme;
  moment: Moment;
  lighting: Lighting;
  couple: CoupleDetails;
  highlightSurface?: string | null;
  compareTheme?: Theme | null;
  holdingCompare?: boolean;
};

function colors(theme: Theme) {
  const p = theme.palette;
  return {
    linen: p.find((c) => c.surface === "linen")?.hex ?? p[0].hex,
    napkin: p.find((c) => c.surface === "napkin")?.hex ?? p[1].hex,
    florals: p.find((c) => c.surface === "florals")?.hex ?? p[2].hex,
    metal: p.find((c) => c.surface === "metal")?.hex ?? p[3].hex,
    ink: p.find((c) => c.surface === "ink")?.hex ?? p[4].hex,
    paper: p[0].hex,
    accent: p[2]?.hex ?? p[1].hex,
  };
}

function lightingOverlay(lighting: Lighting) {
  if (lighting === "daylight") return null;
  if (lighting === "golden") {
    return (
      <rect
        width="1200"
        height="800"
        fill="#E8B86D"
        opacity="0.18"
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
        opacity="0.28"
        style={{ mixBlendMode: "multiply" }}
      />
      <radialGradient id="candleGlow" cx="50%" cy="42%" r="45%">
        <stop offset="0%" stopColor="#FFD9A0" stopOpacity="0.35" />
        <stop offset="55%" stopColor="#C4783A" stopOpacity="0.12" />
        <stop offset="100%" stopColor="#000" stopOpacity="0" />
      </radialGradient>
      <rect width="1200" height="800" fill="url(#candleGlow)" />
    </>
  );
}

function TableScene({
  c,
  highlight,
}: {
  c: ReturnType<typeof colors>;
  highlight?: string | null;
}) {
  const dim = (surface: string) =>
    highlight && highlight !== surface ? 0.35 : 1;

  return (
    <g>
      {/* room wash */}
      <rect width="1200" height="800" fill={c.linen} opacity="0.35" />
      <ellipse cx="600" cy="720" rx="520" ry="60" fill="#2F2B28" opacity="0.06" />

      {/* table top */}
      <ellipse
        cx="600"
        cy="520"
        rx="420"
        ry="160"
        fill={c.linen}
        opacity={dim("linen")}
        style={{ transition: "fill 220ms ease, opacity 180ms ease" }}
      />
      <ellipse
        cx="600"
        cy="520"
        rx="420"
        ry="160"
        fill="none"
        stroke="#2F2B28"
        strokeOpacity="0.08"
        strokeWidth="2"
      />

      {/* runner */}
      <path
        d="M280 500 Q600 440 920 500 Q600 560 280 500Z"
        fill={c.napkin}
        opacity={0.55 * dim("napkin")}
        style={{ transition: "fill 220ms ease, opacity 180ms ease" }}
      />

      {/* plates + napkins left */}
      {[380, 520, 660, 800].map((x, i) => (
        <g key={i} opacity={dim("napkin")}>
          <ellipse
            cx={x}
            cy={540 + (i % 2) * 8}
            rx="48"
            ry="22"
            fill="#F8F5EF"
            stroke={c.metal}
            strokeWidth="2"
            style={{ transition: "stroke 220ms ease" }}
          />
          <rect
            x={x - 14}
            y={528 + (i % 2) * 8}
            width="28"
            height="36"
            rx="3"
            fill={c.napkin}
            transform={`rotate(${-12 + i * 4} ${x} ${540})`}
            style={{ transition: "fill 220ms ease" }}
          />
          <line
            x1={x + 36}
            y1={530}
            x2={x + 42}
            y2={560}
            stroke={c.metal}
            strokeWidth="2.5"
            strokeLinecap="round"
            style={{ transition: "stroke 220ms ease" }}
          />
        </g>
      ))}

      {/* centerpiece */}
      <g opacity={dim("florals")}>
        <ellipse cx="600" cy="500" rx="70" ry="28" fill={c.florals} opacity="0.9" />
        <ellipse cx="560" cy="488" rx="28" ry="36" fill={c.accent} opacity="0.85" />
        <ellipse cx="640" cy="486" rx="30" ry="38" fill={c.florals} />
        <ellipse cx="600" cy="470" rx="24" ry="32" fill={c.accent} opacity="0.75" />
        <ellipse cx="580" cy="500" rx="16" ry="14" fill={c.napkin} opacity="0.7" />
        <ellipse cx="625" cy="498" rx="14" ry="12" fill={c.accent} opacity="0.65" />
        {/* leaves */}
        <path
          d="M520 500 Q500 470 530 460"
          fill="none"
          stroke={c.florals}
          strokeWidth="6"
          strokeLinecap="round"
          opacity="0.7"
        />
        <path
          d="M680 498 Q710 465 685 455"
          fill="none"
          stroke={c.florals}
          strokeWidth="6"
          strokeLinecap="round"
          opacity="0.7"
        />
      </g>

      {/* candles */}
      {[520, 680].map((x) => (
        <g key={x} opacity={dim("metal")}>
          <rect
            x={x - 6}
            y="430"
            width="12"
            height="52"
            rx="2"
            fill="#F8F5EF"
          />
          <rect
            x={x - 10}
            y="478"
            width="20"
            height="10"
            rx="2"
            fill={c.metal}
            style={{ transition: "fill 220ms ease" }}
          />
          <ellipse cx={x} cy="426" rx="5" ry="8" fill="#F5D08A" opacity="0.9" />
        </g>
      ))}

      {/* invite card on table edge */}
      <g opacity={dim("ink")} transform="translate(180 560) rotate(-8)">
        <rect
          width="120"
          height="160"
          rx="4"
          fill={c.paper}
          stroke={c.metal}
          strokeWidth="1.5"
          style={{ transition: "fill 220ms ease, stroke 220ms ease" }}
        />
        <rect x="16" y="28" width="88" height="2" fill={c.ink} opacity="0.35" />
        <rect x="28" y="48" width="64" height="3" fill={c.ink} opacity="0.55" />
        <rect x="36" y="62" width="48" height="2" fill={c.ink} opacity="0.35" />
        <rect x="24" y="100" width="72" height="1.5" fill={c.metal} opacity="0.6" />
      </g>
    </g>
  );
}

function InvitationScene({
  c,
  couple,
  highlight,
}: {
  c: ReturnType<typeof colors>;
  couple: CoupleDetails;
  highlight?: string | null;
}) {
  const dim = (surface: string) =>
    highlight && highlight !== surface ? 0.35 : 1;
  const names = couple.names.trim() || "Amara & James";
  const date = couple.date.trim() || "14 · 06 · 2027";

  return (
    <g>
      <rect width="1200" height="800" fill={c.linen} opacity="0.45" />
      {/* envelope */}
      <g opacity={dim("linen")} transform="translate(220 180)">
        <rect
          width="420"
          height="280"
          rx="8"
          fill={c.napkin}
          style={{ transition: "fill 220ms ease" }}
        />
        <path
          d="M0 0 L210 140 L420 0"
          fill={c.linen}
          opacity="0.85"
          style={{ transition: "fill 220ms ease" }}
        />
        <circle cx="210" cy="150" r="14" fill={c.florals} opacity="0.9" />
      </g>
      {/* invitation card */}
      <g opacity={dim("ink")} transform="translate(520 140)">
        <rect
          width="380"
          height="520"
          rx="6"
          fill={c.paper}
          stroke={c.metal}
          strokeWidth="2"
          style={{ transition: "fill 220ms ease, stroke 220ms ease" }}
        />
        <text
          x="190"
          y="90"
          textAnchor="middle"
          fill={c.metal}
          fontFamily="Georgia, serif"
          fontSize="14"
          letterSpacing="6"
          style={{ transition: "fill 220ms ease" }}
        >
          TOGETHER WITH THEIR FAMILIES
        </text>
        <text
          x="190"
          y="180"
          textAnchor="middle"
          fill={c.ink}
          fontFamily="Georgia, serif"
          fontSize="42"
          fontStyle="italic"
          style={{ transition: "fill 220ms ease" }}
        >
          {names}
        </text>
        <line
          x1="120"
          y1="220"
          x2="260"
          y2="220"
          stroke={c.metal}
          strokeWidth="1"
        />
        <text
          x="190"
          y="270"
          textAnchor="middle"
          fill={c.ink}
          fontFamily="Georgia, serif"
          fontSize="18"
          letterSpacing="3"
          opacity="0.75"
        >
          {date}
        </text>
        <text
          x="190"
          y="320"
          textAnchor="middle"
          fill={c.ink}
          fontFamily="Georgia, serif"
          fontSize="14"
          opacity="0.5"
        >
          request the honour of your presence
        </text>
        {/* floral corner */}
        <g opacity={dim("florals")}>
          <ellipse cx="60" cy="450" rx="36" ry="28" fill={c.florals} />
          <ellipse cx="95" cy="470" rx="28" ry="22" fill={c.accent} opacity="0.85" />
          <ellipse cx="320" cy="60" rx="30" ry="24" fill={c.florals} opacity="0.8" />
          <ellipse cx="345" cy="85" rx="22" ry="18" fill={c.accent} opacity="0.7" />
        </g>
      </g>
    </g>
  );
}

function AisleScene({
  c,
  highlight,
}: {
  c: ReturnType<typeof colors>;
  highlight?: string | null;
}) {
  const dim = (surface: string) =>
    highlight && highlight !== surface ? 0.35 : 1;

  return (
    <g>
      <rect width="1200" height="800" fill={c.linen} opacity="0.4" />
      {/* sky / back wall */}
      <rect y="0" width="1200" height="360" fill={c.napkin} opacity="0.35" />
      {/* aisle runner */}
      <path
        d="M480 800 L520 360 L680 360 L720 800Z"
        fill={c.linen}
        opacity={dim("linen")}
        style={{ transition: "fill 220ms ease, opacity 180ms ease" }}
      />
      <path
        d="M510 800 L540 360 L660 360 L690 800Z"
        fill={c.napkin}
        opacity={0.5 * dim("napkin")}
      />
      {/* arch */}
      <g opacity={dim("florals")}>
        <path
          d="M360 420 Q600 180 840 420"
          fill="none"
          stroke={c.florals}
          strokeWidth="28"
          strokeLinecap="round"
          opacity="0.85"
        />
        <path
          d="M380 420 Q600 220 820 420"
          fill="none"
          stroke={c.accent}
          strokeWidth="14"
          strokeLinecap="round"
          opacity="0.7"
        />
        {[420, 500, 700, 780].map((x, i) => (
          <ellipse
            key={x}
            cx={x}
            cy={300 + (i % 2) * 40}
            rx="28"
            ry="34"
            fill={i % 2 ? c.florals : c.accent}
            opacity="0.85"
          />
        ))}
      </g>
      {/* pew florals */}
      {[200, 280, 920, 1000].map((x, i) => (
        <g key={x} opacity={dim("florals")}>
          <ellipse
            cx={x}
            cy="620"
            rx="40"
            ry="50"
            fill={i % 2 ? c.florals : c.accent}
            opacity="0.8"
          />
          <rect
            x={x - 8}
            y="660"
            width="16"
            height="80"
            fill={c.metal}
            opacity={dim("metal")}
          />
        </g>
      ))}
    </g>
  );
}

function BouquetScene({
  c,
  highlight,
}: {
  c: ReturnType<typeof colors>;
  highlight?: string | null;
}) {
  const dim = (surface: string) =>
    highlight && highlight !== surface ? 0.35 : 1;

  return (
    <g>
      <rect width="1200" height="800" fill={c.linen} opacity="0.5" />
      <ellipse cx="600" cy="700" rx="180" ry="40" fill="#2F2B28" opacity="0.06" />
      {/* stems */}
      <g opacity={dim("florals")}>
        {[560, 580, 600, 620, 640].map((x, i) => (
          <path
            key={x}
            d={`M${x} 520 Q${x + (i - 2) * 8} 620 ${x + (i - 2) * 12} 720`}
            fill="none"
            stroke={c.florals}
            strokeWidth="4"
            opacity="0.7"
          />
        ))}
        {/* blooms */}
        <ellipse cx="560" cy="420" rx="70" ry="80" fill={c.florals} />
        <ellipse cx="640" cy="400" rx="75" ry="85" fill={c.accent} opacity="0.9" />
        <ellipse cx="600" cy="360" rx="60" ry="70" fill={c.florals} opacity="0.85" />
        <ellipse cx="520" cy="460" rx="45" ry="50" fill={c.accent} opacity="0.75" />
        <ellipse cx="680" cy="450" rx="48" ry="55" fill={c.florals} opacity="0.8" />
        <ellipse cx="600" cy="480" rx="40" ry="35" fill={c.napkin} opacity="0.7" />
        {/* leaves */}
        <path
          d="M480 500 Q430 460 460 420"
          fill={c.florals}
          opacity="0.6"
        />
        <path
          d="M720 490 Q780 450 750 410"
          fill={c.florals}
          opacity="0.6"
        />
      </g>
      {/* ribbon */}
      <g opacity={dim("napkin")}>
        <rect
          x="560"
          y="560"
          width="80"
          height="28"
          rx="4"
          fill={c.napkin}
          style={{ transition: "fill 220ms ease" }}
        />
        <path
          d="M560 574 Q520 600 540 640"
          fill="none"
          stroke={c.napkin}
          strokeWidth="10"
          strokeLinecap="round"
        />
        <path
          d="M640 574 Q680 600 660 640"
          fill="none"
          stroke={c.napkin}
          strokeWidth="10"
          strokeLinecap="round"
        />
      </g>
      {/* boutonniere hint */}
      <g opacity={dim("metal")} transform="translate(860 480)">
        <ellipse cx="40" cy="40" rx="36" ry="42" fill={c.florals} opacity="0.85" />
        <ellipse cx="55" cy="55" rx="20" ry="22" fill={c.accent} />
        <rect x="32" y="78" width="16" height="50" fill={c.metal} rx="2" />
      </g>
    </g>
  );
}

export function Scene({
  theme,
  moment,
  lighting,
  couple,
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
        aria-label={`${active.name} ${moment} preview`}
      >
        <defs>
          <filter id="paperGrain">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.85"
              numOctaves="3"
              stitchTiles="stitch"
            />
            <feColorMatrix type="saturate" values="0" />
            <feBlend in="SourceGraphic" mode="multiply" />
          </filter>
        </defs>

        {moment === "table" && (
          <TableScene c={c} highlight={highlightSurface} />
        )}
        {moment === "invitation" && (
          <InvitationScene
            c={c}
            couple={couple}
            highlight={highlightSurface}
          />
        )}
        {moment === "aisle" && (
          <AisleScene c={c} highlight={highlightSurface} />
        )}
        {moment === "bouquet" && (
          <BouquetScene c={c} highlight={highlightSurface} />
        )}

        {lightingOverlay(lighting)}

        {/* soft vignette */}
        <radialGradient id="vignette" cx="50%" cy="45%" r="65%">
          <stop offset="55%" stopColor="#000" stopOpacity="0" />
          <stop offset="100%" stopColor="#2F2B28" stopOpacity="0.18" />
        </radialGradient>
        <rect width="1200" height="800" fill="url(#vignette)" />
      </svg>

      {/* linen grain overlay */}
      <div className="scene-grain pointer-events-none absolute inset-0" />
    </div>
  );
}
