import { facts, isConfigured } from '@/lib/supabase/server';
import type { LgaAliasRow } from '@/lib/types';

/**
 * Resolving a recorded council name to the spelling the site chose to show.
 *
 * `facts.lga_aliases` holds equivalences a named human approved. This module
 * applies them for display and for filtering, and does nothing else: the stored
 * value on a site is never rewritten, so what the pipeline loaded stays exactly
 * as it was loaded and the alias table stays the only place the merge is
 * recorded.
 *
 * Resolution is an **exact match on an approved alias**, and nothing more.
 * `lib/ingestion/lga.ts` can normalise `The Hills Shire` and `Hills Shire
 * Council` onto one key, but that is a suggestion engine for a human reviewing
 * the pipeline's output, and the app must not use it: guessing here would merge
 * two councils on screen that nobody approved merging, which is precisely what
 * `docs/QUALITY.md` grades the GovMarket aggregator C for doing.
 *
 * A cell naming two councils — `Penrith; Blacktown` — matches no alias and so
 * passes through untouched. That is correct. It is not a spelling variant and
 * must never be collapsed onto either council.
 */

/** Approved equivalences, oldest-approved first. Empty when unconfigured. */
export async function listLgaAliases(): Promise<LgaAliasRow[]> {
  if (!isConfigured()) return [];

  const { data, error } = await facts().from('lga_aliases').select('*').order('alias');
  if (error) throw new Error(`Failed to load council aliases: ${error.message}`);
  return data ?? [];
}

/** alias -> canonical, for repeated lookups over a page's worth of sites. */
export function aliasMap(aliases: readonly LgaAliasRow[]): ReadonlyMap<string, string> {
  return new Map(aliases.map((a) => [a.alias, a.canonical]));
}

export interface ResolvedLga {
  /** The spelling to show. The canonical one where an alias applied. */
  readonly display: string;
  /** What the site actually carries, always. */
  readonly recorded: string;
  /** True when an approved alias changed the displayed spelling. */
  readonly normalised: boolean;
}

/**
 * Resolve one recorded name.
 *
 * Returns null for a site with no council recorded, so a caller renders its own
 * gap state rather than inventing a placeholder here.
 */
export function resolveLga(
  recorded: string | null,
  aliases: ReadonlyMap<string, string>,
): ResolvedLga | null {
  if (recorded === null || recorded === '') return null;

  const canonical = aliases.get(recorded);
  if (canonical === undefined || canonical === recorded) {
    return { display: recorded, recorded, normalised: false };
  }
  return { display: canonical, recorded, normalised: true };
}

/**
 * Every recorded spelling that resolves to the same council as `name`.
 *
 * This is what makes a filter work: asked for `Blacktown City Council`, a query
 * has to look for the sites recorded as `Blacktown` too, or the filter returns
 * 4 of 15. `name` itself is always included, so a council with no alias still
 * filters correctly.
 */
export function spellingsOf(name: string, aliases: readonly LgaAliasRow[]): string[] {
  const canonical = aliases.find((a) => a.alias === name)?.canonical ?? name;
  const spellings = new Set<string>([name, canonical]);
  for (const a of aliases) {
    if (a.canonical === canonical) spellings.add(a.alias);
  }
  return [...spellings].sort((a, b) => a.localeCompare(b, 'en-AU'));
}

/**
 * The distinct councils represented, as displayed names.
 *
 * Two spellings of one council collapse to one entry, which is the whole point:
 * a filter listing both `Blacktown` and `Blacktown City Council` offers the
 * reader a distinction the project has decided does not exist.
 */
export function distinctLgas(
  recorded: readonly (string | null)[],
  aliases: ReadonlyMap<string, string>,
): string[] {
  const names = new Set<string>();
  for (const value of recorded) {
    const resolved = resolveLga(value, aliases);
    if (resolved) names.add(resolved.display);
  }
  return [...names].sort((a, b) => a.localeCompare(b, 'en-AU'));
}
