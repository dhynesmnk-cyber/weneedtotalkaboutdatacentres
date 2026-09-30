// app/sites/page.tsx — sortable site list + CSV export (E2) + rollup table (E1).
import Link from "next/link";
import { getSites } from "@/lib/db";
import { buildRollups, STATUS_LABELS } from "@/lib/rollups";
import { exportTable, fieldToCell } from "@/lib/csv";
import FieldValue from "@/components/primitives/FieldValue";
import DownloadCsv from "@/components/blocks/DownloadCsv";

export const metadata = { title: "Sites & entities" };

export default async function SitesPage() {
  const sites = await getSites();
  const csv = exportTable(
    [
      { header: "Name", cell: (s: (typeof sites)[number]) => s.name },
      { header: "LGA", cell: (s) => s.lgaName },
      { header: "Status", cell: (s) => fieldToCell(s.status) },
      { header: "Total capacity MW", cell: (s) => fieldToCell(s.totalCapacityMW) },
      { header: "Live capacity MW", cell: (s) => fieldToCell(s.liveCapacityMW) },
      { header: "Slug", cell: (s) => s.slug },
    ],
    sites,
  );

  const rollups = buildRollups(
    sites.map((s) => ({ state: s.lgaCode.slice(0, 3), status: s.status, totalCapacityMW: s.totalCapacityMW })),
  );

  return (
    <div className="space-y-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Tracked sites</h1>
          <p className="mt-1 text-sm" style={{ color: "var(--ink-700)" }}>
            Every column shows a value or an explicit gap flag — never a blank.
          </p>
        </div>
        <DownloadCsv filename="observatory-sites.csv" csv={csv} />
      </header>

      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b text-left" style={{ borderColor: "var(--line)" }}>
            <th className="py-2 pr-4">Site</th>
            <th className="py-2 pr-4">LGA</th>
            <th className="py-2 pr-4">Status</th>
            <th className="py-2 pr-4">Total MW</th>
            <th className="py-2">Live MW</th>
          </tr>
        </thead>
        <tbody>
          {sites.map((s) => (
            <tr key={s.id} className="border-b" style={{ borderColor: "var(--line)" }}>
              <td className="py-2 pr-4 font-medium">
                <Link href={`/sites/${s.slug}`} className="underline decoration-dotted">{s.name}</Link>
              </td>
              <td className="py-2 pr-4">{s.lgaName}</td>
              <td className="py-2 pr-4"><FieldValue field={s.status} render={(v) => STATUS_LABELS[v]} /></td>
              <td className="py-2 pr-4"><FieldValue field={s.totalCapacityMW} render={(v) => `${v} MW`} /></td>
              <td className="py-2"><FieldValue field={s.liveCapacityMW} render={(v) => `${v} MW`} /></td>
            </tr>
          ))}
        </tbody>
      </table>

      <section aria-labelledby="rollups">
        <h2 id="rollups" className="text-xl font-bold">Capacity by region and status</h2>
        <p className="text-xs mb-2" style={{ color: "var(--ink-500)" }}>
          Produced by the Postgres rollup view in production; totals show a gap flag if any member is unverified.
        </p>
        <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {rollups.map((r) => (
            <li key={`${r.state}-${r.status}`} className="rounded border p-3 text-sm" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
              <strong>{r.state}</strong> · {STATUS_LABELS[r.status]} · {r.siteCount} site{r.siteCount > 1 ? "s" : ""} ·{" "}
              <FieldValue field={r.totalCapacityMW} render={(v) => `${new Intl.NumberFormat("en-AU").format(v)} MW`} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
