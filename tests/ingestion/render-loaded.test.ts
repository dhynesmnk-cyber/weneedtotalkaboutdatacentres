import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { createElement } from 'react';

import fixture from '../fixtures/loaded-site.json';
import { GapBadge, UnexplainedBadge } from '@/components/GapBadge';
import { SourcePanel } from '@/components/SourcePanel';
import { gapsByField, resolveField } from '@/lib/evidence';
import { formatFactStatus, formatMw, formatSiteStatus } from '@/lib/format';
import type { CitationWithSource, DataGapRow, SiteRow } from '@/lib/types';

/**
 * Renders real rows, not invented ones.
 *
 * tests/fixtures/loaded-site.json is a verbatim dump of what the anon role can
 * read after scripts/test-load.sh has run: one real site, its real gaps and its
 * real citations. Regenerate it with the query in that script if the pipeline
 * changes.
 *
 * The app reads through PostgREST, which needs a Supabase project, so this is
 * not the same as seeing the page in a browser. What it does prove is the part
 * that could silently go wrong: that a row shaped the way the loader writes it
 * produces the reader-facing output it should.
 */

const site = fixture.site as unknown as SiteRow;
const gaps = fixture.gaps as unknown as DataGapRow[];
const citations = fixture.citations as unknown as CitationWithSource[];

describe('a real loaded site', () => {
  it('is the record the research actually holds', () => {
    expect(site.name).toBe('Mamre Road Data Centre Campus');
    expect(site.lga).toBe('Penrith');
    expect(site.pipeline_id).toBe('SITE_MAMRE_ROAD');
  });

  it('renders a status the original six values could not express', () => {
    // 'lodged' is one of the five values migration 0005 added. Before it, this
    // site would have had to be recorded as 'proposed', which is a different
    // claim: an application before an authority, not merely an intention.
    expect(site.status).toBe('lodged');
    expect(formatSiteStatus(site.status)).toBe('Lodged');
  });

  it('keeps its two capacity figures apart', () => {
    expect(formatMw(site.it_capacity_mw)).toBe('1,000 MW');
    expect(formatMw(site.max_capacity_mw)).toBe('1,200 MW');
    // Neither was substituted into total, and nothing was summed to 2200.
    expect(site.total_capacity_mw).toBeNull();
  });

  it('shows no live capacity, because none was ever published', () => {
    expect(site.live_capacity_mw).toBeNull();
  });
});

describe('gap badges over real gaps', () => {
  const byField = gapsByField(gaps);

  it('explains every empty field rather than leaving it blank', () => {
    for (const field of ['total_capacity_mw', 'water_usage', 'cooling_type']) {
      expect(byField.has(field)).toBe(true);
    }
  });

  it('renders the reason, not a bare marker', () => {
    const gap = byField.get('water_usage');
    expect(gap).toBeDefined();

    const html = renderToStaticMarkup(createElement(GapBadge, { reason: gap!.reason }));
    expect(html).toContain('Not yet researched');
  });

  it('never claims a stronger reason than the research supports', () => {
    for (const gap of gaps) {
      expect(gap.reason).toBe('unknown');
      const html = renderToStaticMarkup(createElement(GapBadge, { reason: gap.reason }));
      expect(html).not.toContain('Not disclosed');
      expect(html).not.toContain('Withheld');
    }
  });

  it('renders no unexplained-value defect for this site', () => {
    // resolveField returns `unexplained` only when a field has neither a value
    // nor a gap. If the loader ever stopped deriving gaps, this would flip and
    // the page would paint real research as a data-quality defect.
    for (const field of ['water_usage', 'cooling_type', 'grid_connection']) {
      const resolved = resolveField(
        field,
        site[field as keyof SiteRow] as unknown,
        byField,
      );
      expect(resolved.unexplained).toBe(false);
      expect(resolved.gap).toBe('unknown');
    }

    // The defect badge still exists and still says so, for a field that really
    // does lack both.
    expect(renderToStaticMarkup(createElement(UnexplainedBadge))).toContain('No value recorded');
  });
});

describe('the source panel over real citations', () => {
  it('names the real publisher and links the real source', () => {
    const html = renderToStaticMarkup(
      createElement(SourcePanel, { citations }),
    );

    expect(html).toContain('NSW Department of Planning');
    expect(html).toContain('NSW Planning Portal');
    expect(html).toContain('rel="noopener noreferrer"');
  });

  it('shows a citation for a site the reader can actually reach', () => {
    expect(citations.length).toBeGreaterThan(0);
    for (const citation of citations) {
      expect(citation.source).not.toBeNull();
    }
  });
});

describe('claimed records stay marked as claimed', () => {
  it('does not present a proponent assertion as a verified fact', () => {
    const claimed = fixture.claimed as { name: string; fact_status: string }[];
    expect(claimed.length).toBeGreaterThan(0);

    for (const row of claimed) {
      expect(row.fact_status).toBe('claimed');
      expect(formatFactStatus('claimed')).toBe('Claimed by proponent');
      expect(formatFactStatus('claimed')).not.toBe(formatFactStatus('verified'));
    }
  });
});
