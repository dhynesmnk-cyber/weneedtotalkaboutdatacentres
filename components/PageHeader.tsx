import type { ReactNode } from 'react';

const LAYER = {
  record: { label: 'The record', ink: 'text-fact-ink' },
  analysis: { label: 'Analysis', ink: 'text-editorial-ink' },
} as const;

/**
 * A page's title block: which layer it belongs to, the title, and a standfirst.
 *
 * The kicker names the layer in that layer's colour, so a reader landing from
 * a search engine knows at once whether they are reading the record or an
 * argument about it.
 */
export function PageHeader({
  layer,
  kicker,
  title,
  children,
}: {
  layer: keyof typeof LAYER;
  /** Overrides the layer's name, e.g. "The record · Sites". */
  kicker?: string;
  title: ReactNode;
  /** The standfirst: what this page is for, in a sentence or two. */
  children?: ReactNode;
}) {
  const { label, ink } = LAYER[layer];
  return (
    <header>
      <p className={`kicker ${ink}`}>{kicker ?? label}</p>
      <h1 className="page-title mt-2">{title}</h1>
      {children && <div className="standfirst mt-3 space-y-2">{children}</div>}
    </header>
  );
}
