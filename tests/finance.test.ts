import { describe, expect, it } from 'vitest';
import {
  annualPowerCostAud,
  developmentYieldPct,
  impliedValueAud,
  missingMetrics,
  netOperatingIncome,
  yieldAgreesWithStated,
} from '@/lib/finance';
import type { CaseStudyMetrics } from '@/lib/types';

/**
 * The governing property of this module is that a missing input produces a
 * missing output. Most of these tests exist to prove that a gap never becomes a
 * zero, because a zero that should be a gap is a fabricated figure.
 */

const complete: CaseStudyMetrics = {
  total_capex_aud: 1_000_000_000,
  annual_revenue_aud: 200_000_000,
  annual_opex_aud: 120_000_000,
  development_yield_pct: 8,
  stabilised_cap_rate_pct: 6.5,
  power_cost_per_kw: 180,
};

describe('netOperatingIncome', () => {
  it('subtracts opex from revenue', () => {
    expect(netOperatingIncome(complete)).toBe(80_000_000);
  });

  it('returns null when revenue is missing rather than treating it as zero', () => {
    const { annual_revenue_aud: _omitted, ...rest } = complete;
    expect(netOperatingIncome(rest)).toBeNull();
  });

  it('returns null when opex is missing rather than assuming no costs', () => {
    const { annual_opex_aud: _omitted, ...rest } = complete;
    expect(netOperatingIncome(rest)).toBeNull();
  });

  it('accepts a genuine zero opex, which is different from an absent one', () => {
    expect(netOperatingIncome({ ...complete, annual_opex_aud: 0 })).toBe(
      200_000_000,
    );
  });

  it('returns a negative income rather than clamping it', () => {
    expect(
      netOperatingIncome({ ...complete, annual_opex_aud: 250_000_000 }),
    ).toBe(-50_000_000);
  });

  it('rejects NaN, which can arrive from a bad parse', () => {
    expect(netOperatingIncome({ ...complete, annual_revenue_aud: NaN })).toBeNull();
  });
});

describe('developmentYieldPct', () => {
  it('expresses net income as a percentage of capex', () => {
    expect(developmentYieldPct(complete)).toBeCloseTo(8, 10);
  });

  it('returns null when capex is missing', () => {
    const { total_capex_aud: _omitted, ...rest } = complete;
    expect(developmentYieldPct(rest)).toBeNull();
  });

  it('returns null when capex is zero rather than dividing by it', () => {
    expect(developmentYieldPct({ ...complete, total_capex_aud: 0 })).toBeNull();
  });

  it('returns null when any income input is missing', () => {
    const { annual_opex_aud: _omitted, ...rest } = complete;
    expect(developmentYieldPct(rest)).toBeNull();
  });
});

describe('impliedValueAud', () => {
  it('capitalises net income at the stated rate', () => {
    // 80,000,000 / 0.065
    expect(impliedValueAud(complete)).toBeCloseTo(1_230_769_230.77, 1);
  });

  it('returns null when the cap rate is missing', () => {
    const { stabilised_cap_rate_pct: _omitted, ...rest } = complete;
    expect(impliedValueAud(rest)).toBeNull();
  });

  it('returns null for a zero cap rate rather than returning Infinity', () => {
    expect(
      impliedValueAud({ ...complete, stabilised_cap_rate_pct: 0 }),
    ).toBeNull();
  });
});

describe('annualPowerCostAud', () => {
  it('converts megawatts to kilowatts before applying the per-kW cost', () => {
    // 180 AUD/kW * 150 MW * 1000 kW/MW
    expect(annualPowerCostAud(complete, 150)).toBe(27_000_000);
  });

  it('returns null when capacity is unknown', () => {
    expect(annualPowerCostAud(complete, null)).toBeNull();
  });

  it('returns null when the per-kW cost is unknown', () => {
    const { power_cost_per_kw: _omitted, ...rest } = complete;
    expect(annualPowerCostAud(rest, 150)).toBeNull();
  });
});

describe('missingMetrics', () => {
  it('reports nothing missing when all six are present', () => {
    expect(missingMetrics(complete)).toEqual([]);
  });

  it('names every absent metric', () => {
    expect(missingMetrics({ total_capex_aud: 1000 })).toEqual([
      'annual_revenue_aud',
      'annual_opex_aud',
      'development_yield_pct',
      'stabilised_cap_rate_pct',
      'power_cost_per_kw',
    ]);
  });

  it('treats all six as missing for an empty metrics object', () => {
    expect(missingMetrics({})).toHaveLength(6);
  });
});

describe('yieldAgreesWithStated', () => {
  it('agrees when the stated yield matches the calculation', () => {
    expect(yieldAgreesWithStated(complete)).toBe(true);
  });

  it('disagrees when the stated yield is materially different', () => {
    expect(
      yieldAgreesWithStated({ ...complete, development_yield_pct: 12 }),
    ).toBe(false);
  });

  it('tolerates rounding in the stated figure', () => {
    expect(
      yieldAgreesWithStated({ ...complete, development_yield_pct: 8.05 }),
    ).toBe(true);
  });

  it('returns null rather than false when there is nothing to compare', () => {
    const { development_yield_pct: _omitted, ...rest } = complete;
    expect(yieldAgreesWithStated(rest)).toBeNull();
  });
});
