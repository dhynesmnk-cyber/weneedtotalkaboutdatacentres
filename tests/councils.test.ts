import { describe, expect, it } from 'vitest';

import { aliasMap, distinctLgas, resolveLga, spellingsOf } from '@/lib/councils';
import type { LgaAliasRow } from '@/lib/types';

/** The five equivalences approved on 2026-09-23, as they sit in the database. */
const alias = (a: string, c: string): LgaAliasRow => ({
  alias: a,
  canonical: c,
  approved_by: 'David',
  approved_at: '2026-09-23T00:00:00Z',
  note: null,
});

const APPROVED: LgaAliasRow[] = [
  alias('Blacktown', 'Blacktown City Council'),
  alias('Penrith', 'Penrith City Council'),
  alias('Lane Cove', 'Lane Cove Council'),
  alias('Fairfield City', 'Fairfield City Council'),
  alias('The Hills Shire', 'Hills Shire Council'),
];

const MAP = aliasMap(APPROVED);

describe('resolveLga', () => {
  it('shows the canonical spelling where an alias applies', () => {
    expect(resolveLga('Blacktown', MAP)).toEqual({
      display: 'Blacktown City Council',
      recorded: 'Blacktown',
      normalised: true,
    });
  });

  it('keeps the recorded value alongside the display value', () => {
    // The record page shows both. A merge a human approved is still a merge,
    // and the site record is entitled to say what the source said.
    expect(resolveLga('The Hills Shire', MAP)?.recorded).toBe('The Hills Shire');
  });

  it('leaves a canonical value untouched and unmarked', () => {
    expect(resolveLga('Blacktown City Council', MAP)).toEqual({
      display: 'Blacktown City Council',
      recorded: 'Blacktown City Council',
      normalised: false,
    });
  });

  it('leaves a council with no alias alone', () => {
    expect(resolveLga('City of Ryde', MAP)).toEqual({
      display: 'City of Ryde',
      recorded: 'City of Ryde',
      normalised: false,
    });
  });

  it('never merges a cell naming two councils', () => {
    // `Penrith; Blacktown` is a site in two LGAs, not a spelling of either.
    // Collapsing it would assert a jurisdiction nobody verified.
    expect(resolveLga('Penrith; Blacktown', MAP)).toEqual({
      display: 'Penrith; Blacktown',
      recorded: 'Penrith; Blacktown',
      normalised: false,
    });
  });

  it('matches exactly, and never guesses', () => {
    // lib/ingestion/lga.ts would normalise all of these onto `blacktown`. That
    // is a suggestion engine for a human reviewing a load; the app must not use
    // it, or it merges councils nobody approved merging.
    for (const near of ['blacktown', 'BLACKTOWN', 'Blacktown ', 'Blacktown Council']) {
      expect(resolveLga(near, MAP)?.normalised).toBe(false);
    }
  });

  it('returns null for a site with no council recorded', () => {
    // So the caller renders its own gap state rather than a placeholder.
    expect(resolveLga(null, MAP)).toBeNull();
    expect(resolveLga('', MAP)).toBeNull();
  });

  it('passes everything through when no alias is approved', () => {
    const none = aliasMap([]);
    expect(resolveLga('Blacktown', none)).toEqual({
      display: 'Blacktown',
      recorded: 'Blacktown',
      normalised: false,
    });
  });
});

describe('spellingsOf', () => {
  it('finds every spelling of a council from its canonical name', () => {
    // The filter case: asked for the canonical and matching only it, a query
    // would return 4 sites of 15 and look correct.
    expect(spellingsOf('Blacktown City Council', APPROVED)).toEqual([
      'Blacktown',
      'Blacktown City Council',
    ]);
  });

  it('finds every spelling from an alias too', () => {
    expect(spellingsOf('Blacktown', APPROVED)).toEqual([
      'Blacktown',
      'Blacktown City Council',
    ]);
  });

  it('returns a council with no alias as itself', () => {
    expect(spellingsOf('City of Ryde', APPROVED)).toEqual(['City of Ryde']);
  });

  it('does not leak spellings of a different council', () => {
    expect(spellingsOf('Penrith', APPROVED)).not.toContain('Blacktown');
  });

  it('handles three spellings of one council', () => {
    const three = [alias('Ryde', 'City of Ryde'), alias('Ryde City Council', 'City of Ryde')];
    expect(spellingsOf('City of Ryde', three)).toEqual([
      'City of Ryde',
      'Ryde',
      'Ryde City Council',
    ]);
  });
});

describe('distinctLgas', () => {
  it('collapses two spellings of one council into one entry', () => {
    expect(distinctLgas(['Blacktown', 'Blacktown City Council'], MAP)).toEqual([
      'Blacktown City Council',
    ]);
  });

  it('keeps genuinely different councils apart', () => {
    expect(distinctLgas(['Blacktown', 'Penrith', 'City of Ryde'], MAP)).toEqual([
      'Blacktown City Council',
      'City of Ryde',
      'Penrith City Council',
    ]);
  });

  it('lists a multi-LGA cell as its own entry rather than merging it', () => {
    expect(distinctLgas(['Penrith', 'Penrith; Blacktown'], MAP)).toEqual([
      'Penrith City Council',
      'Penrith; Blacktown',
    ]);
  });

  it('drops sites with no council recorded', () => {
    expect(distinctLgas([null, 'Blacktown', null], MAP)).toEqual(['Blacktown City Council']);
  });

  it('sorts in Australian English', () => {
    expect(distinctLgas(['Wollongong', 'Bayside', 'Camden'], MAP)).toEqual([
      'Bayside',
      'Camden',
      'Wollongong',
    ]);
  });
});
