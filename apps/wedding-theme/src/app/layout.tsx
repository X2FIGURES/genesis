import type { Metadata } from "next";
import { Cormorant_Garamond, Inter } from "next/font/google";
import "./globals.css";

const display = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["500", "600"],
  style: ["normal", "italic"],
  variable: "--font-display",
  display: "swap",
});

const sans = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ui",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Atelier · Wedding party colors",
  description:
    "Pick a wedding theme and see what the bridesmaids and groomsmen wear — dress, suit, tie, pocket square, boutonniere.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body
        style={
          {
            ["--serif" as string]:
              "var(--font-display), Palatino, Georgia, serif",
            ["--sans" as string]:
              "var(--font-ui), system-ui, -apple-system, sans-serif",
          } as React.CSSProperties
        }
      >
        {children}
      </body>
    </html>
  );
}
