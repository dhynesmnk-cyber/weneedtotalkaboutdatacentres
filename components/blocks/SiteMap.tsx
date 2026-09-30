// components/blocks/SiteMap.tsx — single point layer (v1 rule: no GIS
// overlays). Popups carry status, capacity with gap badge, and links to the
// site profile and related essays (B3). List fallback for keyboard/SR users.

"use client";

import Link from "next/link";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Site } from "@/lib/types";
import FieldValue from "../primitives/FieldValue";
import { STATUS_LABELS } from "@/lib/rollups";

const icon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

export default function SiteMap({ sites }: { sites: readonly Site[] }) {
  return (
    <div className="space-y-3">
      <MapContainer
        center={[-30.5, 150]}
        zoom={5}
        scrollWheelZoom={false}
        style={{ height: 420, width: "100%", borderRadius: 8 }}
        aria-label="Map of tracked data centre sites"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {sites.map((s) => (
          <Marker key={s.id} position={[s.lat, s.lng]} icon={icon}>
            <Popup>
              <strong>{s.name}</strong>
              <br />
              Status: <FieldValue field={s.status} render={(v) => STATUS_LABELS[v]} />
              <br />
              Total capacity: <FieldValue field={s.totalCapacityMW} render={(v) => `${v} MW`} />
              <br />
              <Link href={`/sites/${s.slug}`} style={{ color: "var(--fact-accent)" }}>
                Open site profile →
              </Link>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      {/* Non-map alternative (WCAG: never map-only information) */}
      <details>
        <summary className="cursor-pointer text-sm font-medium">View all sites as a list</summary>
        <ul className="mt-2 space-y-1 text-sm">
          {sites.map((s) => (
            <li key={s.id}>
              <Link href={`/sites/${s.slug}`} className="underline decoration-dotted">
                {s.name}
              </Link>{" "}
              ({s.lgaName})
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
