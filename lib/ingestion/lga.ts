/**
 * Spotting council names that are probably the same council.
 *
 * This module only ever *reports*. Nothing here merges a name, rewrites a row
 * or decides anything: `facts.lga_aliases` carries `approved_by` on every row
 * and CLAUDE.md states no import writes to it. The output is a worklist for a
 * human, and docs/LGA_ALIAS_CANDIDATES.md is where the proposals live.
 *
 * It replaces a prefix test — `others.some((o) => o.startsWith(lga))` — which
 * had three problems worth naming, because each is a different kind of wrong:
 *
 *   1. It only saw a suffix being added. `Blacktown` against `Blacktown City
 *      Council` matched; `The Hills Shire` against `Hills Shire Council` did
 *      not, because neither is a prefix of the other. The list was a floor and
 *      read like a total.
 *   2. It reported one bare name per group, the shortest. `Blacktown` on its
 *      own does not tell a reviewer what it might be a variant *of*.
 *   3. It conflated a site sitting in two councils with a spelling variant.
 *      `Fairfield City; Blacktown` starts with `Fairfield City`, so the cell
 *      naming two LGAs made a third name look like a variant. Those need
 *      opposite treatment: one may be merged by a human, the other must never
 *      be merged by anyone.
 *
 * The bias is deliberate: report too much rather than too little. A false
 * positive costs a reviewer a glance. A false negative leaves one council
 * silently split across two spellings, with its site count wrong in both,
 * and nobody looking.
 */

/**
 * A cell naming more than one council, e.g. `Penrith; Blacktown`.
 *
 * Deliberately only list punctuation, not the word "and". The two branches of
 * this module give opposite advice — one says a human may merge these, the
 * other says nobody may — so the multi-LGA test has to be precise rather than
 * generous. No council's name contains a semicolon or a slash, whereas plenty
 * could contain "and", and telling someone "never merge this" about a single
 * real council is a worse error than missing a separator this data never uses.
 */
export const MULTI_LGA_SEPARATOR = /[;/]/;

/**
 * Words that describe what kind of body a council is, rather than which one.
 *
 * Stripped from the end of a name, repeatedly, so `City Council` and `Shire
 * Council` both fall away. `regional` is here because NSW and QLD both use it
 * (`Queanbeyan-Palerang Regional`, `Western Downs Regional Council`).
 */
const BODY_WORDS = [
  'council',
  'city',
  'shire',
  'regional',
  'municipal',
  'municipality',
  'borough',
  'district',
  'area',
];

/** Forms that put the body word in front: `City of Ryde`, `Shire of Esperance`. */
const LEADING_FORMS = [/^the\s+/, /^(?:city|shire|town|municipality|borough)\s+of\s+/];

/**
 * A comparison key for a council name. Never stored, never displayed as data.
 *
 * `City of Ryde`, `Ryde City Council` and `Ryde` all reduce to `ryde`. That is
 * the point, and it is also why the result must not be written anywhere: the
 * key discards exactly the information that distinguishes two councils which
 * genuinely share a stem. Bayside Council in NSW and Bayside City Council in
 * Victoria are different councils and would share a key — which is a reason to
 * show a human, not a reason to merge.
 */
export function lgaKey(name: string): string {
  let s = name.toLowerCase();
  s = s.replace(/&/g, ' and ');
  // Hyphens and apostrophes are punctuation between words here, not structure:
  // `Queanbeyan-Palerang` and `Queanbeyan Palerang` are one council.
  s = s.replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();

  for (const form of LEADING_FORMS) s = s.replace(form, '');

  // Repeatedly, so `city council` and `shire council` both fall away entirely.
  //
  // This cannot strip a name to nothing: the match requires a leading space, so
  // there is always a word in front of the one being removed. A name that is
  // only a body word therefore keeps it, and `variantGroups` handles the one
  // way a key can still come back empty — a name made entirely of punctuation.
  let changed = true;
  while (changed) {
    changed = false;
    for (const word of BODY_WORDS) {
      if (s.endsWith(` ${word}`)) {
        s = s.slice(0, -(word.length + 1)).trim();
        changed = true;
      }
    }
  }

  return s;
}

export interface LgaSpelling {
  readonly name: string;
  readonly sites: number;
}

export interface LgaVariantGroup {
  /** The shared comparison key. Diagnostic only. */
  readonly key: string;
  /** Every raw spelling that reduced to it, commonest first. */
  readonly spellings: readonly LgaSpelling[];
}

function countBy(values: readonly string[]): Map<string, number> {
  const counts = new Map<string, number>();
  for (const v of values) counts.set(v, (counts.get(v) ?? 0) + 1);
  return counts;
}

/**
 * Cells that name more than one council.
 *
 * Reported separately and never grouped, because the answer is not an alias. A
 * site on a boundary genuinely in two LGAs needs the schema to hold two;
 * collapsing it to either asserts a jurisdiction nobody verified, and keeping
 * the joined string invents a council that does not exist.
 */
export function multiLgaValues(lgas: readonly string[]): LgaSpelling[] {
  const counts = countBy(lgas.filter((l) => MULTI_LGA_SEPARATOR.test(l)));
  return [...counts.entries()]
    .map(([name, sites]) => ({ name, sites }))
    .sort((a, b) => b.sites - a.sites || a.name.localeCompare(b.name));
}

/**
 * Groups of spellings that probably name the same council.
 *
 * Multi-LGA cells are excluded first. Two of them can normalise alike —
 * `Penrith; Blacktown` and `Penrith;Blacktown` both reduce to the same key — and
 * reporting those as a variant group would tell a reviewer that a human may
 * merge them, which is the opposite of what a cell naming two councils needs.
 */
export function variantGroups(lgas: readonly string[]): LgaVariantGroup[] {
  const single = lgas.filter((l) => !MULTI_LGA_SEPARATOR.test(l));
  const counts = countBy(single);

  const byKey = new Map<string, LgaSpelling[]>();
  for (const [name, sites] of counts) {
    const key = lgaKey(name);
    if (key === '') continue; // nothing left to compare on
    const bucket = byKey.get(key);
    if (bucket) bucket.push({ name, sites });
    else byKey.set(key, [{ name, sites }]);
  }

  return [...byKey.entries()]
    .filter(([, spellings]) => spellings.length > 1)
    .map(([key, spellings]) => ({
      key,
      spellings: [...spellings].sort(
        (a, b) => b.sites - a.sites || a.name.localeCompare(b.name),
      ),
    }))
    .sort((a, b) => a.key.localeCompare(b.key));
}

function line(s: LgaSpelling): string {
  return `  ${String(s.sites).padStart(4)} ${s.sites === 1 ? 'site ' : 'sites'}  ${s.name}`;
}

/** The console block the loader prints. Pure, so its wording is testable. */
export function renderLgaReview(
  groups: readonly LgaVariantGroup[],
  multi: readonly LgaSpelling[],
): string[] {
  const lines: string[] = [];

  if (groups.length > 0) {
    lines.push('');
    lines.push('Council names that look like the same council spelled differently.');
    lines.push('These are loaded verbatim. Resolving them is a human decision:');
    lines.push('add rows to facts.lga_aliases. The loader never guesses.');
    lines.push('Proposals live in docs/LGA_ALIAS_CANDIDATES.md.');
    for (const group of groups) {
      lines.push('');
      for (const s of group.spellings) lines.push(line(s));
    }
  }

  if (multi.length > 0) {
    lines.push('');
    lines.push('Cells naming more than one council. These are NOT aliases and must');
    lines.push('not be merged: a site in two LGAs needs the schema to hold two.');
    for (const s of multi) lines.push(line(s));
  }

  return lines;
}
