import type { ReactNode } from 'react';

/**
 * Separates verified fact from editorial analysis.
 *
 * The two layers are separate in the database and must stay separate on screen.
 * The divider is not decoration: it is the reader's cue that what follows is
 * argument rather than record, and it is announced to assistive technology as
 * well as shown.
 */
export function FactOpinionDivider({
  label = 'Analysis begins here',
  description = 'What follows is the authors’ interpretation, not a sourced finding.',
}: {
  label?: string;
  description?: string;
}) {
  return (
    <div className="my-8" role="separator" aria-label={label}>
      <div className="flex items-center gap-3">
        <span className="h-px flex-1 bg-editorial-edge" />
        <span
          className="rounded-full border border-editorial-edge bg-editorial-wash px-3
                     py-1 text-xs font-semibold uppercase tracking-wide text-editorial-ink"
        >
          {label}
        </span>
        <span className="h-px flex-1 bg-editorial-edge" />
      </div>
      <p className="mt-2 text-center text-sm text-slate-600">{description}</p>
    </div>
  );
}

/** Wraps fact-layer content so its provenance is visible without reading it. */
export function FactBlock({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-lg border-l-4 border-fact-edge bg-fact-wash/40 py-1 pl-4">
      {children}
    </div>
  );
}

/** Wraps editorial content. Always paired with a divider above it. */
export function EditorialBlock({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-lg border-l-4 border-editorial-edge bg-editorial-wash/40 py-1 pl-4">
      {children}
    </div>
  );
}
