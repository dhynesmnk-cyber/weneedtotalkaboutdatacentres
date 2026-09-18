import Link from 'next/link';
import { listEssays } from '@/lib/editorial';
import { isConfigured } from '@/lib/supabase/server';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { DateStamp } from '@/components/DateStamp';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Essays' };

/**
 * Essay hub. Second entry point in docs/SPEC.md's priority order.
 *
 * Framed as editorial throughout, so a reader arriving here first is never in
 * doubt that they are reading argument rather than record.
 */
export default async function EssaysPage() {
  const essays = await listEssays();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Essays</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          Video essays and written analysis, newest first. This is the editorial
          layer: interpretation and argument, drawing on the sourced records but
          separate from them.
        </p>
      </div>

      {!isConfigured() ? (
        <NotConnected what="essays" />
      ) : essays.length === 0 ? (
        <NothingRecorded what="published essays" />
      ) : (
        <ul className="space-y-6">
          {essays.map((essay) => (
            <li
              key={essay.id}
              className="rounded-lg border-l-4 border-editorial-edge bg-editorial-wash/40 py-3 pl-4 pr-3"
            >
              <h2 className="text-lg font-semibold">
                <Link
                  href={`/essays/${essay.id}`}
                  className="text-editorial-ink underline underline-offset-2"
                >
                  {essay.title}
                </Link>
              </h2>
              <DateStamp publishDate={essay.publish_date} className="mt-1" />
              {essay.tags.length > 0 && (
                <ul className="mt-2 flex flex-wrap gap-2">
                  {essay.tags.map((tag) => (
                    <li
                      key={tag}
                      className="rounded border border-editorial-edge px-2 py-0.5 text-xs text-editorial-ink"
                    >
                      {tag}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
