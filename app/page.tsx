// app/page.tsx — Home (Epic A): briefing block with live StatCards above the
// fold, "check your area" entry, start-here path ≤ 2 taps, ClaimVsRecord.
import Link from "next/link";
import { getClaimVsRecordPairs, getEvents, getSites } from "@/lib/db";
import { sumCapacity } from "@/lib/rollups";
import { withinMonths } from "@/lib/dates";
import StatCard from "@/components/primitives/StatCard";
import AreaSearch from "@/components/blocks/AreaSearch";
import ClaimVsRecord from "@/components/blocks/ClaimVsRecord";
import { getLocalities } from "@/lib/db";
import { value } from "@/lib/gap";

export default async function HomePage() {
  const [sites, events, pairs, localities] = await Promise.all([
    getSites(),
    getEvents(),
    getClaimVsRecordPairs(),
    getLocalities(),
  ]);

  const quarterEvents = events.filter((e) => withinMonths(e.date, 3)).length;
  const committedMW = sumCapacity(sites.map((s) => s.totalCapacityMW));

  return (
    <div className="space-y-10">
      <section aria-labelledby="briefing" className="space-y-4">
        <h1 id="briefing" className="text-3xl font-bold">
          What is actually happening with AI data centres in Australia?
        </h1>
        <p className="max-w-prose text-base" style={{ color: "var(--ink-700)" }}>
          A public observatory: every site, event and figure below comes from a dated,
          cited record. Where a source has not published a number, we say so instead of
          guessing. New here? Start with{" "}
          <Link href="/about#explainer" className="underline font-medium">
            what an AI data centre is, in numbers
          </Link>
          , then check your area below.
        </p>
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard label="Sites tracked" field={value(sites.length)} asOf="2026-09-30" href="/sites" />
          <StatCard label="Total committed capacity" field={committedMW} unit="MW" asOf="2026-09-30" href="/sites" />
          <StatCard label="Events this quarter" field={value(quarterEvents)} asOf="2026-09-30" href="/timeline" />
        </div>
      </section>

      <section aria-labelledby="area">
        <h2 id="area" className="mb-3 text-xl font-bold">
          Is there one near me?
        </h2>
        <AreaSearch localities={localities} />
      </section>

      <ClaimVsRecord pairs={pairs} />

      <section className="grid gap-4 md:grid-cols-3">
        {[
          { href: "/timeline", title: "Timeline", desc: "Six tracks of dated events: planning, construction, media, political, community, financial." },
          { href: "/map", title: "Map", desc: "Every tracked site as a point on the map, with status and capacity." },
          { href: "/essays", title: "Video essays (opinion)", desc: "Editorial analysis comparing public perception with the records. Clearly separated from data." },
        ].map((c) => (
          <Link key={c.href} href={c.href} className="rounded-lg border p-4 hover:shadow-md transition-shadow" style={{ borderColor: "var(--line)", background: "var(--card)" }}>
            <h3 className="font-bold">{c.title}</h3>
            <p className="mt-1 text-sm" style={{ color: "var(--ink-700)" }}>{c.desc}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
