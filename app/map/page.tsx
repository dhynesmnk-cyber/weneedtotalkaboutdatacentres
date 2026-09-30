// app/map/page.tsx — point map (v1: single layer, no GIS overlays).
import { getSites } from "@/lib/db";
import dynamic from "next/dynamic";

export const metadata = { title: "Map" };

const SiteMap = dynamic(() => import("@/components/blocks/SiteMap"), { ssr: false });

export default async function MapPage() {
  const sites = await getSites();
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Where are they?</h1>
      <p className="max-w-prose text-sm" style={{ color: "var(--ink-700)" }}>
        One point per tracked site. Click a marker for status and capacity; use the
        list below the map if you prefer not to interact with the map.
      </p>
      <SiteMap sites={sites} />
    </div>
  );
}
