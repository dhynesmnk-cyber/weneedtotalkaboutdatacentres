import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getSiteWithEvidence } from '@/lib/sites';
import { aliasMap, listLgaAliases, resolveLga } from '@/lib/councils';
import { listEventsForSite } from '@/lib/events';
import { linkedEntitiesForSite } from '@/lib/entities';
import { listCaseStudies } from '@/lib/editorial';
import { isConfigured } from '@/lib/supabase/server';
import { gapsByField, resolveField, type FieldEvidence } from '@/lib/evidence';
import { GapBadge, UnexplainedBadge } from '@/components/GapBadge';
import { SourcePanel } from '@/components/SourcePanel';
import { NotConnected } from '@/components/NotConnected';
import {
  formatDate,
  formatEventCategory,
  formatFieldName,
  formatMegalitres,
  formatMw,
  formatSiteStatus,
} from '@/lib/format';
import type { SiteRow } from '@/lib/types';

export const dynamic = 'force-dynamic';

/**
 * Site profile: every field, with a gap badge wherever a value is missing.
 *
 * The page renders all thirteen fields whether or not they hold values, because
 * which fields are unknown for a given site is itself a finding. A profile that
 * silently omits water usage tells the reader nothing; one that shows "Water
 * usage — Not disclosed" tells them something worth knowing.
 */
export default async function SitePage({ params }: { params: { id: string } }) {
  if (!isConfigured()) {
    return <NotConnected what="site records" />;
  }

  const record = await getSiteWithEvidence(params.id);
  if (!record) notFound();

  const { site, gaps, citations } = record;
  const byField = gapsByField(gaps);

  const [events, entities, caseStudies, aliases] = await Promise.all([
    listEventsForSite(site.id),
    linkedEntitiesForSite(site.id),
    listCaseStudies({ siteId: site.id }),
    listLgaAliases(),
  ]);

  // Shown in the approved spelling, as everywhere else, but this is the record
  // page: where an alias applied, it also says what the source actually said.
  // The merge is a decision a human made and a reader is entitled to see it.
  const council = resolveLga(site.lga, aliasMap(aliases));

  const fields: FieldEvidence<string>[] = [
    resolveField('operator', site.operator, byField),
    resolveField('status', formatSiteStatus(site.status), byField),
    resolveField('lga', council?.display ?? null, byField),
    resolveField('total_capacity_mw', formatMw(site.total_capacity_mw), byField),
    resolveField('live_capacity_mw', formatMw(site.live_capacity_mw), byField),
    resolveField('cooling_type', site.cooling_type, byField),
    resolveField('rack_density_kw', kw(site.rack_density_kw), byField),
    resolveField('grid_connection', site.grid_connection, byField),
    resolveField('water_usage', formatMegalitres(site.water_usage), byField),
    resolveField('notes', site.notes, byField),
  ];

  const known = fields.filter((f) => f.value !== null).length;

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{site.name}</h1>
        <p className="mt-2 text-sm text-slate-600">
          {known} of {fields.length} fields recorded. The rest are shown as gaps
          with a stated reason.
        </p>
      </div>

      <section aria-labelledby="record-heading">
        <h2 id="record-heading" className="text-lg font-semibold text-slate-900">
          Record
        </h2>

        <dl className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
          {fields.map((field) => (
            <div
              key={field.field}
              className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4"
            >
              <dt className="w-48 shrink-0 text-sm font-medium text-slate-600">
                {formatFieldName(field.field)}
              </dt>
              <dd className="text-slate-900">
                {field.value !== null ? (
                  field.value
                ) : field.gap !== null ? (
                  <GapBadge reason={field.gap} />
                ) : (
                  <UnexplainedBadge />
                )}
                {field.field === 'lga' && council?.normalised ? (
                  <p className="mt-1 text-sm text-slate-600">
                    Recorded as &ldquo;{council.recorded}&rdquo;. Shown in the
                    approved spelling for this council.
                  </p>
                ) : null}
              </dd>
            </div>
          ))}
          <div className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4">
            <dt className="w-48 shrink-0 text-sm font-medium text-slate-600">
              Coordinates
            </dt>
            <dd className="text-slate-900">
              {site.lat !== null && site.lng !== null ? (
                `${site.lat.toFixed(4)}, ${site.lng.toFixed(4)}`
              ) : byField.has('lat') ? (
                <GapBadge reason={byField.get('lat')!.reason} />
              ) : (
                <UnexplainedBadge />
              )}
            </dd>
          </div>
        </dl>
      </section>

      <SourcePanel citations={citations} />

      <section aria-labelledby="events-heading">
        <h2 id="events-heading" className="text-lg font-semibold text-slate-900">
          Events
        </h2>
        {events.length === 0 ? (
          <p className="mt-2 text-sm text-slate-700">No events recorded for this site.</p>
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
                {event.summary && (
                  <p className="mt-1 text-sm text-slate-700">{event.summary}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="entities-heading">
        <h2 id="entities-heading" className="text-lg font-semibold text-slate-900">
          Linked entities
        </h2>
        {entities.length === 0 ? (
          <p className="mt-2 text-sm text-slate-700">
            No confirmed entity links. Proposed links are not shown until a human
            confirms them.
          </p>
        ) : (
          <ul className="mt-3 flex flex-wrap gap-2">
            {entities.map((entity) => (
              <li key={entity.id}>
                <Link
                  href={`/entities/${entity.id}`}
                  className="rounded border border-fact-edge bg-fact-wash px-3 py-1 text-sm text-fact-ink underline underline-offset-2"
                >
                  {entity.name}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      {caseStudies.length > 0 && (
        <section aria-labelledby="analysis-heading">
          <h2 id="analysis-heading" className="text-lg font-semibold text-slate-900">
            Analysis of this site
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Editorial, not record. Published separately from the data above.
          </p>
          <ul className="mt-3 space-y-2">
            {caseStudies.map((study) => (
              <li key={study.id}>
                <Link
                  href={`/case-studies/${study.id}`}
                  className="text-editorial-ink underline underline-offset-2"
                >
                  {study.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function kw(value: SiteRow['rack_density_kw']): string | null {
  return Number.isFinite(value) ? `${value} kW` : null;
}
