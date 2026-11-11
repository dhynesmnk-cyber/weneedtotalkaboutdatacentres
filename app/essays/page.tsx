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
 * doubt that they are reading argument rather than record. The newest essay
 * leads, magazine style; the rest follow as a list.
 */
export default async function EssaysPage() {
  const essays = await listEssays({ kind: 'essay' });
  const [lead, ...rest] = essays;

  return (
    <div className="space-y-10">
      <div>
        <p className="kicker text-editorial-ink">Analysis</p>
        <h1 className="page-title mt-2">Essays</h1>
        <p className="standfirst mt-3">
          Video essays and written analysis, newest first. This is the editorial
          layer: interpretation and argument, drawing on the sourced records but
          separate from them. Every essay shows the record first, then where its
          argument begins.
        </p>
      </div>

      {!isConfigured() ? (
        <NotConnected what="essays" />
      ) : !lead ? (
        <NothingRecorded what="published essays" />
      ) : (
        <>
          <article className="border-y border-slate-200 py-8">
            <p className="kicker text-editorial-ink">Latest</p>
            <h2 className="mt-3 max-w-4xl font-serif text-title font-semibold text-slate-900">
              <Link href={`/essays/${lead.slug ?? lead.id}`} className="hover:underline hover:decoration-2 hover:underline-offset-4">
                {lead.title}
              </Link>
            </h2>
            {lead.standfirst && <p className="standfirst mt-3 font-serif">{lead.standfirst}</p>}
            <DateStamp publishDate={lead.publish_date} dataAsOfDate={lead.data_as_of_date} className="mt-4" />
          </article>

          {rest.length > 0 && (
            <ul className="divide-y divide-slate-200">
              {rest.map((essay) => (
                <li key={essay.id} className="py-6">
                  <h2 className="font-serif text-2xl font-semibold text-slate-900">
                    <Link href={`/essays/${essay.slug ?? essay.id}`} className="hover:underline hover:underline-offset-4">
                      {essay.title}
                    </Link>
                  </h2>
                  {essay.standfirst && <p className="mt-2 max-w-2xl text-slate-700">{essay.standfirst}</p>}
                  <DateStamp publishDate={essay.publish_date} dataAsOfDate={essay.data_as_of_date} className="mt-2" />
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
