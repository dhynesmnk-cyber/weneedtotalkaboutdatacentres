import { formatFactStatus } from '@/lib/format';
import type { FactStatus } from '@/lib/types';

/**
 * How well a record is established: verified, reported, or only claimed.
 *
 * This is the distinction the project exists to make (docs/SPEC.md: a claimed
 * record "is never presented to a reader as verified"), so each level differs
 * in shape and symbol as well as colour, and always says what it means in
 * words. Claimed is outlined and dashed with a quotation mark: it is someone's
 * statement, not a finding.
 */

const STYLE: Record<FactStatus, { mark: string; className: string }> = {
  verified: { mark: '✓', className: 'border-fact-ink bg-fact-ink text-white' },
  reported: { mark: '◐', className: 'border-fact-edge bg-fact-wash text-fact-ink' },
  claimed: { mark: '“', className: 'border-dashed border-slate-500 bg-white text-slate-800' },
  gap: { mark: '◌', className: 'border-gap-edge bg-gap-wash text-gap-ink' },
};

/** What each level means, for a reader. docs/UI.md and /how-to-read use the same words. */
export const EVIDENCE_MEANING: Record<FactStatus, string> = {
  verified:
    'Read in a primary document: a planning record, a regulator, legislation, or the company’s own release.',
  reported: 'From credible secondary reporting of a primary document, and attributed to it.',
  claimed:
    'A developer’s or industry body’s own statement. No one has independently confirmed it.',
  gap: 'Not yet established from any source.',
};

export function EvidenceBadge({
  status,
  size = 'md',
}: {
  status: FactStatus;
  size?: 'sm' | 'md';
}) {
  const { mark, className } = STYLE[status];
  return (
    <span
      className={`inline-flex items-center gap-1 whitespace-nowrap rounded border font-medium ${className} ${
        size === 'sm' ? 'px-1.5 py-0 text-xs' : 'px-2 py-0.5 text-sm'
      }`}
    >
      <span aria-hidden="true">{mark}</span>
      {formatFactStatus(status)}
    </span>
  );
}
