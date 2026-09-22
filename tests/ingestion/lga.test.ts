import { describe, expect, it } from 'vitest';

import {
  lgaKey,
  multiLgaValues,
  renderLgaReview,
  variantGroups,
} from '@/lib/ingestion/lga';

/** Every council spelling in the research corpus, one entry per site. */
const CORPUS = [
  ...Array<string>(11).fill('Blacktown'),
  ...Array<string>(4).fill('Blacktown City Council'),
  ...Array<string>(4).fill('Penrith'),
  ...Array<string>(4).fill('Penrith City Council'),
  ...Array<string>(5).fill('Lane Cove'),
  'Lane Cove Council',
  ...Array<string>(2).fill('Fairfield City'),
  'Fairfield City Council',
  'The Hills Shire',
  ...Array<string>(2).fill('Hills Shire Council'),
  'Fairfield City; Blacktown',
  'Penrith; Blacktown',
  'Bayside',
  ...Array<string>(2).fill('Camden'),
  'Cumberland',
  'City of Parramatta',
  ...Array<string>(12).fill('City of Ryde'),
  'Sutherland Shire',
  'Queanbeyan-Palerang Regional',
  'Western Downs Regional Council',
  ...Array<string>(2).fill('Willoughby City'),
];

describe('lgaKey', () => {
  it('reduces the three common forms of one council to one key', () => {
    expect(lgaKey('Ryde')).toBe('ryde');
    expect(lgaKey('City of Ryde')).toBe('ryde');
    expect(lgaKey('Ryde City Council')).toBe('ryde');
  });

  it('strips a leading article', () => {
    // The case the old prefix test could not see at all.
    expect(lgaKey('The Hills Shire')).toBe(lgaKey('Hills Shire Council'));
  });

  it('strips stacked body words, not just one', () => {
    expect(lgaKey('Fairfield City Council')).toBe('fairfield');
    expect(lgaKey('Wingecarribee Shire Council')).toBe('wingecarribee');
    expect(lgaKey('Western Downs Regional Council')).toBe('western downs');
  });

  it('treats punctuation between words as a space', () => {
    expect(lgaKey('Queanbeyan-Palerang Regional')).toBe('queanbeyan palerang');
    expect(lgaKey('Queanbeyan Palerang')).toBe('queanbeyan palerang');
  });

  it('folds an ampersand', () => {
    expect(lgaKey('Ballina & District')).toBe(lgaKey('Ballina and District'));
  });

  it('keeps a name that is only a body word', () => {
    // Stripping requires a leading space, so the loop cannot empty a name.
    expect(lgaKey('Council')).toBe('council');
    expect(lgaKey('Shire')).toBe('shire');
  });

  it('returns an empty key only for a name with no letters or digits', () => {
    expect(lgaKey('---')).toBe('');
    expect(lgaKey('Ryde')).not.toBe('');
  });

  it('does not merge councils that merely share a word', () => {
    // The expensive failure is a wrong merge, so these must stay distinct.
    expect(lgaKey('Camden')).not.toBe(lgaKey('Campbelltown'));
    expect(lgaKey('Port Phillip')).not.toBe(lgaKey('Port Stephens'));
    expect(lgaKey('Blacktown')).not.toBe(lgaKey('Blacktown Heights'));
    expect(lgaKey('Bayside')).not.toBe(lgaKey('Bay'));
  });
});

describe('variantGroups', () => {
  const groups = variantGroups(CORPUS);
  const keys = groups.map((g) => g.key);

  it('finds every pair in the corpus', () => {
    expect(keys).toEqual(['blacktown', 'fairfield', 'hills', 'lane cove', 'penrith']);
  });

  it('finds the pair the old prefix test missed', () => {
    // Regression guard. `other.startsWith(lga)` reported neither of these,
    // because neither is a prefix of the other.
    const hills = groups.find((g) => g.key === 'hills');
    expect(hills?.spellings.map((s) => s.name).sort()).toEqual([
      'Hills Shire Council',
      'The Hills Shire',
    ]);
  });

  it('reports both spellings, not just the shorter one', () => {
    // The old output was a bare list of shortest names, which never said what
    // a name was a variant of.
    for (const group of groups) expect(group.spellings.length).toBeGreaterThan(1);
  });

  it('carries the site count for each spelling, commonest first', () => {
    const blacktown = groups.find((g) => g.key === 'blacktown');
    expect(blacktown?.spellings).toEqual([
      { name: 'Blacktown', sites: 11 },
      { name: 'Blacktown City Council', sites: 4 },
    ]);
  });

  it('breaks a count tie by name so the output is stable', () => {
    const penrith = groups.find((g) => g.key === 'penrith');
    expect(penrith?.spellings.map((s) => s.name)).toEqual([
      'Penrith',
      'Penrith City Council',
    ]);
  });

  it('never groups a multi-LGA cell with a single council', () => {
    // `Fairfield City; Blacktown` starts with `Fairfield City`, which is how
    // the old test came to flag a name because of a cell naming two councils.
    for (const group of groups) {
      for (const s of group.spellings) expect(s.name).not.toContain(';');
    }
  });

  it('never reports two multi-LGA cells as variants of each other', () => {
    // These normalise alike, so without the exclusion they would be reported as
    // one council spelled two ways — advice to merge two cells that each name
    // two councils.
    expect(variantGroups(['Penrith; Blacktown', 'Penrith;Blacktown'])).toEqual([]);
  });

  it('ignores a name that is only punctuation rather than bucketing it', () => {
    // Such a name normalises to the empty key; grouping on it would put every
    // unrelated junk value in one bucket.
    expect(variantGroups(['---', '***'])).toEqual([]);
  });

  it('reports nothing when every council is spelled one way', () => {
    expect(variantGroups(['Camden', 'Camden', 'Cumberland'])).toEqual([]);
  });

  it('reports nothing for an empty corpus', () => {
    expect(variantGroups([])).toEqual([]);
  });

  it('groups three spellings of one council together', () => {
    const [group] = variantGroups(['Ryde', 'City of Ryde', 'Ryde City Council']);
    expect(group?.spellings).toHaveLength(3);
  });
});

describe('multiLgaValues', () => {
  it('finds the cells naming two councils', () => {
    expect(multiLgaValues(CORPUS).map((s) => s.name)).toEqual([
      'Fairfield City; Blacktown',
      'Penrith; Blacktown',
    ]);
  });

  it('accepts a slash as a separator too', () => {
    expect(multiLgaValues(['Penrith/Blacktown'])).toHaveLength(1);
  });

  it('does not treat the word "and" as a separator', () => {
    // A real council may be named "X and Y"; saying "never merge this" about
    // one would be worse guidance than missing a separator the data never uses.
    expect(multiLgaValues(['Ballina and District'])).toEqual([]);
  });

  it('counts repeats rather than listing them twice', () => {
    expect(multiLgaValues(['A; B', 'A; B'])).toEqual([{ name: 'A; B', sites: 2 }]);
  });
});

describe('renderLgaReview', () => {
  const text = () => renderLgaReview(variantGroups(CORPUS), multiLgaValues(CORPUS)).join('\n');

  it('names the table and the document a reviewer needs', () => {
    expect(text()).toContain('facts.lga_aliases');
    expect(text()).toContain('docs/LGA_ALIAS_CANDIDATES.md');
  });

  it('says the loader never guesses', () => {
    expect(text()).toContain('The loader never guesses');
  });

  it('warns that multi-LGA cells must not be merged', () => {
    expect(text()).toMatch(/NOT aliases and must\nnot be merged/);
  });

  it('agrees with English on one site', () => {
    expect(text()).toContain('1 site   The Hills Shire');
    expect(text()).toContain('11 sites  Blacktown');
  });

  it('prints nothing at all when there is nothing to review', () => {
    expect(renderLgaReview([], [])).toEqual([]);
  });

  it('prints only the relevant section when one is empty', () => {
    const variantsOnly = renderLgaReview(variantGroups(['Ryde', 'City of Ryde']), []);
    expect(variantsOnly.join('\n')).not.toContain('more than one council');
  });
});
