import type { CaseStudyMetrics } from '@/lib/types';

/**
 * Financial calculations for case studies.
 *
 * The governing rule is that a missing input produces a missing output. Every
 * function here returns null rather than substituting a default, assuming a
 * zero, or annualising from a partial figure. A derived number that quietly
 * treats an unknown opex as zero is a fabricated number, and fabricating is the
 * one thing this project may not do.
 *
 * Unit tests are mandatory for this module. See docs/CLAUDE.md conventions.
 */

/** Net operating income: revenue less operating expenditure, in AUD. */
export function netOperatingIncome(metrics: CaseStudyMetrics): number | null {
  const { annual_revenue_aud, annual_opex_aud } = metrics;
  if (!isFinitePositive(annual_revenue_aud)) return null;
  if (!isFiniteNonNegative(annual_opex_aud)) return null;
  return annual_revenue_aud - annual_opex_aud;
}

/**
 * Development yield: net operating income as a percentage of total capital
 * expenditure.
 *
 * Returned as a percentage, so 0.085 of capex is reported as 8.5.
 */
export function developmentYieldPct(metrics: CaseStudyMetrics): number | null {
  const noi = netOperatingIncome(metrics);
  if (noi === null) return null;

  const capex = metrics.total_capex_aud;
  if (!isFinitePositive(capex)) return null;

  return (noi / capex) * 100;
}

/**
 * Implied capitalised value at a given cap rate, in AUD.
 *
 * Both the income and the rate must be known. A cap rate of zero is rejected
 * rather than treated as a division edge case.
 */
export function impliedValueAud(metrics: CaseStudyMetrics): number | null {
  const noi = netOperatingIncome(metrics);
  if (noi === null) return null;

  const capRate = metrics.stabilised_cap_rate_pct;
  if (!isFinitePositive(capRate)) return null;

  return noi / (capRate / 100);
}

/**
 * Annual power cost for a site, in AUD.
 *
 * power_cost_per_kw is an annual cost per kilowatt, so capacity in megawatts is
 * converted to kilowatts first.
 */
export function annualPowerCostAud(
  metrics: CaseStudyMetrics,
  capacityMw: number | null,
): number | null {
  const perKw = metrics.power_cost_per_kw;
  if (!isFinitePositive(perKw)) return null;
  if (!isFinitePositive(capacityMw)) return null;

  return perKw * capacityMw * 1000;
}

/**
 * Which of the six metrics are absent.
 *
 * Used to raise gaps explicitly in the UI rather than rendering a metric card
 * with a blank where a figure should be.
 */
export function missingMetrics(
  metrics: CaseStudyMetrics,
): (keyof CaseStudyMetrics)[] {
  const expected: (keyof CaseStudyMetrics)[] = [
    'total_capex_aud',
    'annual_revenue_aud',
    'annual_opex_aud',
    'development_yield_pct',
    'stabilised_cap_rate_pct',
    'power_cost_per_kw',
  ];

  return expected.filter((key) => !isFiniteNumber(metrics[key]));
}

/**
 * Whether a stated development yield agrees with one calculated from the
 * underlying figures.
 *
 * Returns null when either is unavailable. A disagreement is a data quality
 * finding, not something to silently prefer one side of.
 */
export function yieldAgreesWithStated(
  metrics: CaseStudyMetrics,
  tolerancePct = 0.1,
): boolean | null {
  const calculated = developmentYieldPct(metrics);
  const stated = metrics.development_yield_pct;

  if (calculated === null) return null;
  if (!isFiniteNumber(stated)) return null;

  return Math.abs(calculated - stated) <= tolerancePct;
}

type Maybe = number | null | undefined;

function isFinitePositive(value: Maybe): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value > 0;
}

function isFiniteNonNegative(value: Maybe): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0;
}

function isFiniteNumber(value: Maybe): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}
