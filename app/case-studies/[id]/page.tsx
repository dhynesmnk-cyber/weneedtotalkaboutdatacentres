import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getCaseStudy } from '@/lib/editorial';
import { getSite } from '@/lib/sites';
import { citationsFor, gapsByField, gapsFor } from '@/lib/evidence';
import { isConfigured } from '@/lib/supabase/server';
import {
  developmentYieldPct,
  impliedValueAud,
  missingMetrics,
  netOperatingIncome,
  yieldAgreesWithStated,
} from '@/lib/finance';
import { SourcePanel } from '@/components/SourcePanel';
import { DateStamp } from '@/components/DateStamp';
import { GapBadge, UnexplainedBadge } from '@/components/GapBadge';
import {
  EditorialBlock,
  FactOpinionDivider,
} from '@/components/FactOpinionDivider';
import { NotConnected } from '@/components/NotConnected';
import { formatAudCompact, formatFieldName, formatPct } from '@/lib/format';
import type { CaseStudyMetrics, DataGapRow } from '@/lib/types';

export const dynamic = 'force-dynamic';

/**
 * Case study: metric cards, then narrative, then sources.
 *
 * The metrics are factual figures living in an editorial table — the one
 * deliberate boundary crossing in the model — so they sit above the fact/opinion
 * divider and carry gap badges like any other fact. The narrative sits below it.
 *
 * Where a stated development yield disagrees with one calculated from the
 * underlying figures, the page says so rather than picking a side.
 */
export default async function CaseStudyPage({
  params,
}: {
  params: { id: string };
}) {
  if (!isConfigured()) {
    return <NotConnected what="case studies" />;
  }

  const study = await getCaseStudy(params.id);
  if (!study) notFound();

  const [citations, gaps, site] = await Promise.all([
    citationsFor('case_studies', study.id),
    gapsFor('case_studies', study.id),
    study.site_id ? getSite(study.site_id) : Promise.resolve(null),
  ]);

  const byField = gapsByField(gaps);
  const metrics = study.metrics;
  const absent = missingMetrics(metrics);

  const noi = netOperatingIncome(metrics);
  const calculatedYield = developmentYieldPct(metrics);
  const impliedValue = impliedValueAud(metrics);
  const agreement = yieldAgreesWithStated(metrics);

  return (
    <article className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">{study.title}</h1>
        <DateStamp
          publishDate={study.publish_date}
          dataAsOfDate={study.data_as_of_date}
          className="mt-2"
        />
        {site && (
          <p className="mt-2 text-sm">
            <Link
              href={`/sites/${site.id}`}
              className="text-fact-ink underline underline-offset-2"
            >
              {site.name}
            </Link>
          </p>
        )}
      </header>

      <section aria-labelledby="metrics-heading">
        <h2 id="metrics-heading" className="text-lg font-semibold text-slate-900">
          Figures
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Sourced figures, not projections. Missing values are gaps, never
          estimates.
        </p>

        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            field="total_capex_aud"
            value={formatAudCompact(metrics.total_capex_aud)}
            gaps={byField}
          />
          <MetricCard
            field="annual_revenue_aud"
            value={formatAudCompact(metrics.annual_revenue_aud)}
            gaps={byField}
          />
          <MetricCard
            field="annual_opex_aud"
            value={formatAudCompact(metrics.annual_opex_aud)}
            gaps={byField}
          />
          <MetricCard
            field="development_yield_pct"
            value={formatPct(metrics.development_yield_pct)}
            gaps={byField}
          />
          <MetricCard
            field="stabilised_cap_rate_pct"
            value={formatPct(metrics.stabilised_cap_rate_pct)}
            gaps={byField}
          />
          <MetricCard
            field="power_cost_per_kw"
            value={formatAudCompact(metrics.power_cost_per_kw)}
            gaps={byField}
          />
        </div>

        {absent.length > 0 && (
          <p className="mt-3 rounded border border-gap-edge bg-gap-wash px-3 py-2 text-sm text-gap-ink">
            {absent.length} of 6 figures are not recorded:{' '}
            {absent.map(formatFieldName).join(', ')}. Nothing has been
            interpolated to fill them.
          </p>
        )}
      </section>

      <section aria-labelledby="derived-heading">
        <h2 id="derived-heading" className="text-lg font-semibold text-slate-900">
          Derived
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Calculated from the figures above. A derived value is shown only when
          every input it needs is present.
        </p>

        <dl className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
          <DerivedRow label="Net operating income" value={formatAudCompact(noi)} />
          <DerivedRow
            label="Development yield (calculated)"
            value={formatPct(calculatedYield)}
          />
          <DerivedRow
            label="Implied value at stated cap rate"
            value={formatAudCompact(impliedValue)}
          />
        </dl>

        {agreement === false && (
          <p className="mt-3 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-900">
            The stated development yield does not match the figure calculated
            from capex, revenue and opex. Both are shown above. This is a data
            quality finding and should be resolved against the sources rather
            than by preferring one.
          </p>
        )}
      </section>

      <SourcePanel citations={citations} />

      <FactOpinionDivider label="Analysis" />

      {study.narrative && (
        <EditorialBlock>
          <div className="max-w-none whitespace-pre-line text-slate-800">
            {study.narrative}
          </div>
        </EditorialBlock>
      )}
    </article>
  );
}

function MetricCard({
  field,
  value,
  gaps,
}: {
  field: keyof CaseStudyMetrics;
  value: string | null;
  gaps: Map<string, DataGapRow>;
}) {
  const gap = gaps.get(field);

  return (
    <div className="rounded-lg border border-fact-edge bg-fact-wash p-4">
      <p className="text-sm font-medium text-slate-600">{formatFieldName(field)}</p>
      <div className="mt-2 text-xl font-semibold text-fact-ink">
        {value !== null ? (
          value
        ) : gap ? (
          <GapBadge reason={gap.reason} />
        ) : (
          <UnexplainedBadge />
        )}
      </div>
    </div>
  );
}

function DerivedRow({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4">
      <dt className="w-64 shrink-0 text-sm font-medium text-slate-600">{label}</dt>
      <dd className="font-semibold text-slate-900">
        {value ?? (
          <span className="text-sm font-normal italic text-slate-500">
            Not calculable from the recorded figures
          </span>
        )}
      </dd>
    </div>
  );
}
