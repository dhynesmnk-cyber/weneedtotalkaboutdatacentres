import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getEntity, linkedRecordsForEntity } from '@/lib/entities';
import { citationsFor } from '@/lib/evidence';
import { isConfigured } from '@/lib/supabase/server';
import { SourcePanel } from '@/components/SourcePanel';
import { NotConnected } from '@/components/NotConnected';
import {
  formatDate,
  formatEventCategory,
  formatMw,
  formatSiteStatus,
} from '@/lib/format';

export const dynamic = 'force-dynamic';

/**
 * Entity profile. Published only for entities flagged major by public
 * prominence, per docs/SPEC.md: the project tracks organisations and public
 * figures, not private individuals.
 *
 * Sites and events here come from confirmed links only. RLS filters proposed
 * links out before they reach this page.
 */
export default async function EntityPage({ params }: { params: { id: string } }) {
  if (!isConfigured()) {
    return <NotConnected what="entity records" />;
  }

  const entity = await getEntity(params.id);
  if (!entity) notFound();

  // A profile exists only for major entities. Anything else is a record in the
  // database, not a published page.
  if (!entity.major_flag) notFound();

  const [{ sites, events }, citations] = await Promise.all([
    linkedRecordsForEntity(entity.id),
    citationsFor('entities', entity.id),
  ]);

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{entity.name}</h1>
        <p className="mt-2 text-slate-700">
          {[entity.type, entity.role].filter(Boolean).join(' · ') ||
            'No type or role recorded'}
        </p>
      </div>

      {entity.public_actions_summary && (
        <section aria-labelledby="actions-heading">
          <h2 id="actions-heading" className="text-lg font-semibold text-slate-900">
            Public actions
          </h2>
          <p className="mt-2 whitespace-pre-line text-slate-800">
            {entity.public_actions_summary}
          </p>
        </section>
      )}

      <SourcePanel citations={citations} />

      <section aria-labelledby="entity-sites-heading">
        <h2 id="entity-sites-heading" className="text-lg font-semibold text-slate-900">
          Linked sites
        </h2>
        {sites.length === 0 ? (
          <p className="mt-2 text-sm text-slate-700">No confirmed site links.</p>
        ) : (
          <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
            {sites.map((site) => (
              <li key={site.id} className="px-4 py-3">
                <Link
                  href={`/sites/${site.id}`}
                  className="font-medium text-fact-ink underline underline-offset-2"
                >
                  {site.name}
                </Link>
                <p className="text-sm text-slate-700">
                  {[formatSiteStatus(site.status), formatMw(site.total_capacity_mw)]
                    .filter(Boolean)
                    .join(' · ') || 'No status or capacity recorded'}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="entity-events-heading">
        <h2 id="entity-events-heading" className="text-lg font-semibold text-slate-900">
          Linked events
        </h2>
        {events.length === 0 ? (
          <p className="mt-2 text-sm text-slate-700">No confirmed event links.</p>
        ) : (
          <ul className="mt-3 space-y-3">
            {events.map((event) => (
              <li key={event.id} className="rounded border border-slate-200 px-4 py-3">
                <div className="flex flex-wrap items-baseline gap-x-3">
                  <span className="rounded border border-fact-edge bg-fact-wash px-2 py-0.5 text-xs font-medium text-fact-ink">
                    {formatEventCategory(event.category)}
                  </span>
                  <time dateTime={event.date} className="text-sm text-slate-600">
                    {formatDate(event.date)}
                  </time>
                </div>
                <p className="mt-1 font-medium">{event.title}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
