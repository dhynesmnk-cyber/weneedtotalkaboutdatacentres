import { describe, expect, it } from 'vitest';
import {
  deriveDataGaps,
  RowRejected,
  SITE_FACTUAL_FIELDS,
  transformEntity,
  transformSite,
  transformSourceRefs,
  transformSource,
  type KnownEntity,
  type PipelineRow,
} from '@/lib/ingestion/transform';
import { pipelineUuid } from '@/lib/ingestion/identity';
import { UnmappedValueError } from '@/lib/ingestion/vocabulary';

/** A site row shaped like the pipeline's, with the minimum to be valid. */
function siteRow(overrides: PipelineRow = {}): PipelineRow {
  return {
    id: 'SITE_TEST',
    name: 'Test Campus',
    status: 'operational',
    source_id: 'SRC_TEST',
    fact_status: 'VERIFIED',
    confidence: 'high',
    as_of_date: '2026-09-18',
    ...overrides,
  };
}

const entities = new Map<string, KnownEntity>([
  ['ENT_ACME', { uuid: pipelineUuid('entities', 'ENT_ACME'), name: 'Acme Data Centres' }],
]);

describe('transformSite', () => {
  it('renames lon to lng', () => {
    const { site } = transformSite(siteRow({ lat: -33.72, lon: 150.8 }));
    expect(site.lng).toBe(150.8);
    expect(site.lat).toBe(-33.72);
    expect(site).not.toHaveProperty('lon');
  });

  it('drops half a coordinate rather than placing a point on a meridian', () => {
    // sites_coords_paired would reject it anyway; failing here is clearer.
    const { site } = transformSite(siteRow({ lat: -33.72, lon: null }));
    expect(site.lat).toBeNull();
    expect(site.lng).toBeNull();
  });

  it('keeps the four capacity figures on four distinct columns', () => {
    const { site } = transformSite(
      siteRow({
        it_capacity_mw: 190,
        total_capacity_mw: 250,
        max_capacity_mw: 300,
        first_phase_mw: 60,
      }),
    );
    expect(site.it_capacity_mw).toBe(190);
    expect(site.total_capacity_mw).toBe(250);
    expect(site.max_capacity_mw).toBe(300);
    expect(site.first_phase_mw).toBe(60);
  });

  it('never sums or substitutes capacity figures', () => {
    const { site } = transformSite(siteRow({ it_capacity_mw: 190, max_capacity_mw: 300 }));
    // 490 would be the sum; 190 or 300 would be a substitution into total.
    expect(site.total_capacity_mw).toBeNull();
  });

  // The single most important assertion in this file.
  it('never populates live_capacity_mw, even when it_capacity_mw is present', () => {
    const { site } = transformSite(siteRow({ it_capacity_mw: 190, total_capacity_mw: 250 }));
    expect(site.live_capacity_mw).toBeNull();
  });

  it('rejects a site with no source rather than importing it uncited', () => {
    expect(() => transformSite(siteRow({ source_id: null }))).toThrow(RowRejected);
  });

  it('cites every site it accepts', () => {
    const { citations } = transformSite(siteRow());
    expect(citations).toHaveLength(1);
    expect(citations[0]?.source_id).toBe(pipelineUuid('sources', 'SRC_TEST'));
    expect(citations[0]?.record_type).toBe('sites');
  });

  it('carries fact_status and confidence through unchanged', () => {
    const { site } = transformSite(siteRow({ fact_status: 'CLAIMED', confidence: 'low' }));
    expect(site.fact_status).toBe('claimed');
    expect(site.confidence).toBe('low');
  });

  it('throws on a status it has no mapping for', () => {
    expect(() => transformSite(siteRow({ status: 'mothballed' }))).toThrow(UnmappedValueError);
  });

  it('loads the council name verbatim, without canonicalising it', () => {
    // 'Blacktown' and 'Blacktown City Council' both appear in the research.
    // Picking one would be an unsourced judgement about which council a site
    // sits in, made invisibly. See facts.lga_aliases.
    expect(transformSite(siteRow({ lga: 'Blacktown' })).site.lga).toBe('Blacktown');
    expect(transformSite(siteRow({ lga: 'Blacktown City Council' })).site.lga).toBe(
      'Blacktown City Council',
    );
  });

  describe('entity relationships', () => {
    it('proposes an operator link, never a confirmed one', () => {
      const { links } = transformSite(siteRow({ operator_id: 'ENT_ACME' }), entities);
      expect(links).toHaveLength(1);
      expect(links[0]?.state).toBe('proposed');
    });

    it('still records the operator name, which is a sourced fact', () => {
      const { site } = transformSite(siteRow({ operator_id: 'ENT_ACME' }), entities);
      expect(site.operator).toBe('Acme Data Centres');
    });

    it('proposes no link for an operator it cannot resolve', () => {
      const { links, site } = transformSite(siteRow({ operator_id: 'ENT_GHOST' }), entities);
      expect(links).toHaveLength(0);
      expect(site.operator).toBeNull();
    });
  });
});

describe('deriveDataGaps', () => {
  it('records a gap for every null factual field', () => {
    const { site, gaps } = transformSite(siteRow());
    const gapped = new Set(gaps.map((g) => g.field_name));

    for (const field of SITE_FACTUAL_FIELDS) {
      if (site[field] === null) expect(gapped).toContain(field);
    }
  });

  it('records no gap for a field that has a value', () => {
    const { gaps } = transformSite(siteRow({ lga: 'Penrith' }));
    expect(gaps.map((g) => g.field_name)).not.toContain('lga');
  });

  // The reason is the point. Anything stronger than `unknown` is a claim about
  // the world that needs a human and a source.
  it('only ever uses reason unknown', () => {
    const { gaps } = transformSite(siteRow());
    expect(gaps.length).toBeGreaterThan(0);
    for (const gap of gaps) {
      expect(gap.reason).toBe('unknown');
    }
  });

  it('never claims a source for a derived gap', () => {
    const { gaps } = transformSite(siteRow());
    for (const gap of gaps) expect(gap.source_id).toBeNull();
  });

  it('gaps live_capacity_mw rather than leaving it unexplained', () => {
    const { gaps } = transformSite(siteRow({ it_capacity_mw: 190 }));
    expect(gaps.map((g) => g.field_name)).toContain('live_capacity_mw');
  });

  it('records one gap per field, not several', () => {
    const { gaps } = transformSite(siteRow());
    const names = gaps.map((g) => g.field_name);
    expect(new Set(names).size).toBe(names.length);
  });

  it('does not treat bookkeeping columns as findings', () => {
    const names = deriveDataGaps('sites', 'x', {}).map((g) => g.field_name);
    for (const col of ['id', 'name', 'pipeline_id', 'fact_status', 'created_at']) {
      expect(names).not.toContain(col);
    }
  });
});

describe('transformSource', () => {
  const source: PipelineRow = {
    id: 'SRC_TEST',
    title: 'NSW Planning Portal project record',
    publisher: 'NSW Department of Planning',
    url: 'https://example.gov.au/x',
    doc_type: 'primary_planning_portal',
    accessed: '2026-09-18',
    credibility: 'A',
  };

  it('maps accessed onto retrieved_date and doc_type onto type', () => {
    const mapped = transformSource(source);
    expect(mapped.retrieved_date).toBe('2026-09-18');
    expect(mapped.type).toBe('primary_planning_portal');
    expect(mapped.credibility).toBe('A');
  });

  it('rejects a source with no retrieval date rather than back-filling today', () => {
    // Back-filling would assert a retrieval that did not happen.
    expect(() => transformSource({ ...source, accessed: null })).toThrow(RowRejected);
  });

  it('rejects a source with no title', () => {
    expect(() => transformSource({ ...source, title: null })).toThrow(RowRejected);
  });
});

describe('transformEntity', () => {
  const row: PipelineRow = {
    id: 'ENT_ACME',
    name: 'Acme Data Centres',
    entity_type: 'colocation_operator',
    source_id: 'SRC_TEST',
    fact_status: 'REPORTED',
    confidence: 'medium',
  };

  it('never flags an entity as major', () => {
    // Which entities are prominent enough to profile is a human judgement.
    expect(transformEntity(row).entity.major_flag).toBe(false);
  });

  it('cites the entity from its row-level source', () => {
    expect(transformEntity(row).citations).toHaveLength(1);
  });
});

describe('transformSourceRefs', () => {
  it('maps refs that point at tables this schema has', () => {
    const { citations } = transformSourceRefs([
      { id: 1, entity_table: 'sites', entity_rowid: 'SITE_TEST', source_id: 'SRC_TEST', quote: null },
    ]);
    expect(citations).toHaveLength(1);
    expect(citations[0]?.record_id).toBe(pipelineUuid('sites', 'SITE_TEST'));
  });

  it('reports refs it cannot place rather than dropping them silently', () => {
    const { citations, skipped } = transformSourceRefs([
      { id: 1, entity_table: 'lobbying', entity_rowid: 'LOB_1', source_id: 'SRC_TEST', quote: null },
    ]);
    expect(citations).toHaveLength(0);
    expect(skipped.lobbying).toBe(1);
  });

  it('does not pass a verbatim quote off as a field-level claim', () => {
    // citations.claim names the specific assertion a source supports, and
    // citationCoverage() matches it against field names. A quote is not that,
    // and mapping it across would manufacture coverage the research lacks.
    const { citations } = transformSourceRefs([
      {
        id: 1,
        entity_table: 'sites',
        entity_rowid: 'SITE_TEST',
        source_id: 'SRC_TEST',
        quote: 'The campus will draw 190 MW.',
      },
    ]);
    expect(citations[0]?.claim).toBeNull();
  });
});
