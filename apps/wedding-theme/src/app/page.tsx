import { Suspense } from "react";
import { Visualizer } from "@/components/Visualizer";

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="atelier">
          <p className="eyebrow">Wedding theme visualizer</p>
          <h1 className="brand">Atelier</h1>
          <p style={{ color: "var(--muted)" }}>Loading your palette…</p>
        </main>
      }
    >
      <Visualizer />
    </Suspense>
  );
}
