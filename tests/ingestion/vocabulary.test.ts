import { describe, expect, it } from 'vitest';
import {
  mapConfidence,
  mapCredibility,
  mapFactStatus,
  mapSiteStatus,
  NEVER_POPULATED,
  SITE_STATUS_MAP,
  UnmappedValueError,
} from '@/lib/ingestion/vocabulary';
import { SITE_STATUSES } from '@/lib/types';

describe('site status', () => {
  it('maps every status the pipeline actually uses', () => {
    // The seven values present in data-pipeline's sites table today, plus the
    // two its schema permits but no row currently carries.
    for (const value of [
      'operational',
      'approved',
      'lodged',
      'pre_lodgement',
      'rumoured',
      'under_construction',
      'withdrawn',
      'refused',
      'cancelled',
    ]) {
      expect(SITE_STATUSES).toContain(mapSiteStatus(value));
    }
  });

  it('renames operational to operating, the one synonym', () => {
    expect(mapSiteStatus('operational')).toBe('operating');
  });

  // These two are the mapping's load-bearing refusals. If someone later
  // "simplifies" the vocabulary by collapsing them onto the original six
  // values, these fail rather than quietly changing what the record says.
  it('does not recast a refusal as a withdrawal', () => {
    expect(mapSiteStatus('refused')).toBe('refused');
    expect(mapSiteStatus('refused')).not.toBe('withdrawn');
  });

  it('does not promote a rumour into a formal proposal', () => {
    expect(mapSiteStatus('rumoured')).toBe('rumoured');
    expect(mapSiteStatus('rumoured')).not.toBe('proposed');
  });

  it('passes null through rather than inventing a status', () => {
    expect(mapSiteStatus(null)).toBeNull();
    expect(mapSiteStatus('')).toBeNull();
  });

  it('throws on an unknown status instead of guessing a near-enough one', () => {
    expect(() => mapSiteStatus('mothballed')).toThrow(UnmappedValueError);
  });

  it('maps only to values the enum actually has', () => {
    for (const mapped of Object.values(SITE_STATUS_MAP)) {
      expect(SITE_STATUSES).toContain(mapped);
    }
  });
});

describe('fact status', () => {
  it('lowercases the pipeline vocabulary', () => {
    expect(mapFactStatus('VERIFIED')).toBe('verified');
    expect(mapFactStatus('REPORTED')).toBe('reported');
    expect(mapFactStatus('CLAIMED')).toBe('claimed');
  });

  it('preserves GAP rather than dropping it', () => {
    // A value established as absent is a different record from one nobody has
    // looked at. Flattening the two loses the distinction.
    expect(mapFactStatus('GAP')).toBe('gap');
  });

  it('never silently upgrades a claim', () => {
    expect(mapFactStatus('CLAIMED')).not.toBe('verified');
    expect(mapFactStatus('CLAIMED')).not.toBe('reported');
  });

  it('throws on an unknown status', () => {
    expect(() => mapFactStatus('PROBABLY')).toThrow(UnmappedValueError);
  });
});

describe('confidence and credibility', () => {
  it('accepts the three confidence levels', () => {
    expect(mapConfidence('high')).toBe('high');
    expect(mapConfidence('medium')).toBe('medium');
    expect(mapConfidence('low')).toBe('low');
  });

  it('accepts credibility grades A to D', () => {
    for (const grade of ['A', 'B', 'C', 'D']) {
      expect(mapCredibility(grade)).toBe(grade);
    }
  });

  it('rejects a grade outside the scale rather than clamping it', () => {
    expect(() => mapCredibility('E')).toThrow(UnmappedValueError);
    expect(() => mapConfidence('very high')).toThrow(UnmappedValueError);
  });
});

describe('the never-populated list', () => {
  it('names live_capacity_mw and says why', () => {
    expect(NEVER_POPULATED).toHaveProperty('live_capacity_mw');
    expect(NEVER_POPULATED.live_capacity_mw).toMatch(/fabricate|design rating/i);
  });

  it('names the fields that would amount to publishing', () => {
    expect(NEVER_POPULATED).toHaveProperty('major_flag');
    expect(NEVER_POPULATED).toHaveProperty('approved_by');
    expect(NEVER_POPULATED).toHaveProperty('approved_at');
  });
});
