/**
 * The vocabulary map between the curation pipeline and this database.
 *
 * Every reconciliation decision lives here, in one file, so it can be reviewed
 * as a whole rather than discovered a line at a time inside a loader. The
 * reasoning behind each one is in docs/PIPELINE_MAPPING.md.
 *
 * The governing rule: a mapping may rename, but it may never reinterpret. Where
 * the two systems genuinely disagree about what a value means, the value is
 * carried across intact and the schema is widened to hold it. Where a value has
 * no honest destination, this module throws rather than guessing.
 */

import type { ConfidenceLevel, FactStatus, SiteStatus, SourceCredibility } from '@/lib/types';

/** Raised when a value has no honest destination. Never swallowed. */
export class UnmappedValueError extends Error {
  constructor(
    readonly domain: string,
    readonly value: string,
  ) {
    super(
      `No mapping for ${domain} value "${value}". ` +
        'Add it to lib/ingestion/vocabulary.ts and document the decision in ' +
        'docs/PIPELINE_MAPPING.md, or correct it in the pipeline. It is not ' +
        'mapped to a near-enough value.',
    );
    this.name = 'UnmappedValueError';
  }
}

/**
 * Site lifecycle.
 *
 * Only one of these is a rename: the pipeline's `operational` and this schema's
 * `operating` are the same state spelled two ways. Every other value is carried
 * across unchanged, because the alternatives are all falsifications:
 *
 *   refused -> withdrawn would recast an authority's refusal as a proponent's
 *   decision to walk away. Those are opposite stories about who stopped a
 *   project.
 *
 *   rumoured -> proposed would promote an unverified rumour into an apparent
 *   formal proposal. An observatory whose subject is public perception versus
 *   research data cannot afford to make that particular error.
 */
export const SITE_STATUS_MAP: Record<string, SiteStatus> = {
  rumoured: 'rumoured',
  pre_lodgement: 'pre_lodgement',
  lodged: 'lodged',
  approved: 'approved',
  under_construction: 'under_construction',
  operational: 'operating', // the one rename
  refused: 'refused',
  withdrawn: 'withdrawn',
  cancelled: 'cancelled',
};

export function mapSiteStatus(value: string | null | undefined): SiteStatus | null {
  if (value === null || value === undefined || value === '') return null;

  const mapped = SITE_STATUS_MAP[value];
  if (!mapped) throw new UnmappedValueError('site_status', value);
  return mapped;
}

/**
 * Claim strength. The pipeline shouts these; this schema does not.
 *
 * `gap` is deliberately preserved rather than dropped. A row whose value is
 * established as absent is a different record from one nobody has looked at,
 * and flattening the two would lose the distinction this project is built on.
 */
export const FACT_STATUS_MAP: Record<string, FactStatus> = {
  VERIFIED: 'verified',
  REPORTED: 'reported',
  CLAIMED: 'claimed',
  GAP: 'gap',
};

export function mapFactStatus(value: string | null | undefined): FactStatus | null {
  if (value === null || value === undefined || value === '') return null;

  const mapped = FACT_STATUS_MAP[value];
  if (!mapped) throw new UnmappedValueError('fact_status', value);
  return mapped;
}

export function mapConfidence(value: string | null | undefined): ConfidenceLevel | null {
  if (value === null || value === undefined || value === '') return null;
  if (value === 'low' || value === 'medium' || value === 'high') return value;
  throw new UnmappedValueError('confidence', value);
}

export function mapCredibility(value: string | null | undefined): SourceCredibility | null {
  if (value === null || value === undefined || value === '') return null;
  if (value === 'A' || value === 'B' || value === 'C' || value === 'D') return value;
  throw new UnmappedValueError('credibility', value);
}

/**
 * Fields that are renamed on the way across, and nothing more.
 *
 * `lng` wins over `lon` because it is already in lib/types.ts, SiteMap.tsx and
 * the sites_coords_paired constraint. Changing the database to match the
 * pipeline would be the larger edit and would gain nothing.
 */
export const FIELD_RENAMES: Record<string, string> = {
  lon: 'lng',
};

/**
 * Fields the loader must never populate, with the reason.
 *
 * This is an enforced absence, not a comment. `live_capacity_mw` is the trap:
 * `it_capacity_mw` is sitting right there and looks like it would do. It would
 * not. IT capacity is a design rating for the load available to racks; live
 * capacity is what is energised today. Filling one from the other would put a
 * number in front of a reader that no source ever published.
 */
export const NEVER_POPULATED: Record<string, string> = {
  live_capacity_mw:
    'The pipeline has no live capacity figure. it_capacity_mw is a design ' +
    'rating, not what is energised, and substituting it would fabricate a claim.',
  major_flag:
    'Whether an entity is major enough to profile is a human editorial ' +
    'judgement (docs/SPEC.md "Entity profiles"), not an import artefact.',
  approved_by: 'No agent publishes content.',
  approved_at: 'No agent publishes content.',
};
