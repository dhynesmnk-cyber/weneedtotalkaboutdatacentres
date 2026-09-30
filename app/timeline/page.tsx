// app/timeline/page.tsx — Timeline entry point (SPEC priority 1) with the
// track selector, rolling window and accessible list fallback.
import { getEvents } from "@/lib/db";
import TimelineTracks from "@/components/blocks/TimelineTracks";

export const metadata = { title: "Timeline" };

export default async function TimelinePage() {
  const events = await getEvents();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Timeline of dated events</h1>
        <p className="mt-2 max-w-prose text-sm" style={{ color: "var(--ink-700)" }}>
          Six combinable tracks. Default view shows major events from the last 12
          months; widen the window or enable all tracks for the full record. Every
          event links to its sources.
        </p>
      </header>
      <TimelineTracks events={events} />
    </div>
  );
}
