/**
 * Load the curation pipeline into the Postgres fact layer.
 *
 * Reads data-pipeline/exports/australian_data_centre_observatory.db and emits a
 * single transactional SQL file. It writes nothing to any database itself; a
 * human applies the artefact, having read it.
 *
 *   npx tsx scripts/ingestion/load-pipeline.ts --out .artifacts/load-pipeline.sql
 *   npx tsx scripts/ingestion/load-pipeline.ts --dry-run
 *
 * Validation discipline is borrowed from data-pipeline/scripts/load_pack.py:
 * an explicit table allow-list, a required source for every row, rejection
 * rather than silent dropping, and an audit row for every run.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

import { header, literal, upsert } from '@/lib/ingestion/sql';
import {
  RowRejected,
  transformEntity,
  transformSite,
  transformSource,
  transformSourceRefs,
  type DerivedCitation,
  type KnownEntity,
  type PipelineRow,
} from '@/lib/ingestion/transform';

const LOADER_VERSION = 'load-pipeline/1.0.0';
const SOURCE_SYSTEM = 'au-dc-observatory';

const REPO_ROOT = join(__dirname, '..', '..');
const PIPELINE_DB = join(
  REPO_ROOT,
  'data-pipeline',
  'exports',
  'australian_data_centre_observatory.db',
);

/**
 * The only tables this loader may write to.
 *
 * editorial is absent by design, not by omission: no code path here can reach
 * an essay or a case study, so "no agent publishes content" is enforced by the
 * shape of the program rather than by remembering.
 */
const ALLOWED_TABLES = [
  'facts.sources',
  'facts.entities',
  'facts.sites',
  'facts.citations',
  'facts.data_gaps',
  'facts.links',
  'facts.ingest_runs',
] as const;

interface Report {
  counts: Record<string, number>;
  rejected: string[];
  skippedRefs: Record<string, number>;
  unmatchedLgas: string[];
}

function readTable(db: DatabaseSync, table: string): PipelineRow[] {
  return db.prepare(`select * from ${table}`).all() as PipelineRow[];
}

function main(): void {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const outIndex = args.indexOf('--out');
  const outPath =
    outIndex >= 0 && args[outIndex + 1]
      ? (args[outIndex + 1] as string)
      : join(REPO_ROOT, '.artifacts', 'load-pipeline.sql');

  const digest = createHash('sha256').update(readFileSync(PIPELINE_DB)).digest('hex');
  const db = new DatabaseSync(PIPELINE_DB, { readOnly: true });

  const report: Report = { counts: {}, rejected: [], skippedRefs: {}, unmatchedLgas: [] };

  // --- sources -------------------------------------------------------------
  const sources = [];
  for (const row of readTable(db, 'sources')) {
    try {
      sources.push(transformSource(row));
    } catch (error) {
      if (!(error instanceof RowRejected)) throw error;
      report.rejected.push(error.message);
    }
  }
  report.counts['facts.sources'] = sources.length;

  // --- entities ------------------------------------------------------------
  const entities = [];
  const citations: DerivedCitation[] = [];
  const entitiesByPipelineId = new Map<string, KnownEntity>();

  for (const row of readTable(db, 'entities')) {
    try {
      const { entity, citations: entityCitations } = transformEntity(row);
      entities.push(entity);
      citations.push(...entityCitations);
      if (entity.pipeline_id) {
        entitiesByPipelineId.set(entity.pipeline_id, {
          uuid: entity.id,
          name: entity.name,
        });
      }
    } catch (error) {
      if (!(error instanceof RowRejected)) throw error;
      report.rejected.push(error.message);
    }
  }
  report.counts['facts.entities'] = entities.length;

  // --- sites, and the gaps and links they imply ----------------------------
  const sites = [];
  const gaps = [];
  const links = [];

  for (const row of readTable(db, 'sites')) {
    try {
      const transformed = transformSite(row, entitiesByPipelineId);
      sites.push(transformed.site);
      gaps.push(...transformed.gaps);
      links.push(...transformed.links);
      citations.push(...transformed.citations);
    } catch (error) {
      if (!(error instanceof RowRejected)) throw error;
      report.rejected.push(error.message);
    }
  }
  report.counts['facts.sites'] = sites.length;
  report.counts['facts.data_gaps'] = gaps.length;
  report.counts['facts.links'] = links.length;

  // --- citations from source_refs -----------------------------------------
  const refs = transformSourceRefs(readTable(db, 'source_refs'));
  citations.push(...refs.citations);
  report.skippedRefs = refs.skipped;

  // Only cite sources that were actually loaded: a citation pointing at a
  // rejected source would violate the foreign key, and silently dropping the
  // citation instead would hide the rejection.
  const loadedSourceIds = new Set(sources.map((s) => s.id));
  const usable = citations.filter((c) => loadedSourceIds.has(c.source_id));
  const orphaned = citations.length - usable.length;

  // Deduplicate on the same key as citations_unique_record_source, so a single
  // statement cannot conflict with itself.
  const seen = new Set<string>();
  const deduped = usable.filter((c) => {
    const key = `${c.record_type}|${c.record_id}|${c.source_id}|${c.claim ?? ''}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  report.counts['facts.citations'] = deduped.length;

  // --- council names that need a human ------------------------------------
  // Reported, never fixed. See facts.lga_aliases.
  const lgas = [...new Set(sites.map((s) => s.lga).filter((l): l is string => l !== null))];
  report.unmatchedLgas = lgas
    .filter((lga) => lgas.some((other) => other !== lga && other.startsWith(lga)))
    .sort();

  db.close();

  // --- emit ----------------------------------------------------------------
  const sql = [
    header({
      loaderVersion: LOADER_VERSION,
      sourceSystem: SOURCE_SYSTEM,
      sourceDigest: digest,
      counts: report.counts,
    }),
    'begin;\n\n',
    '-- Sources first: everything else references them.\n',
    upsert('facts.sources', sources, '(pipeline_id) where pipeline_id is not null', {
      cast: { credibility: 'facts.source_credibility' },
    }),
    '\n',
    upsert('facts.entities', entities, '(pipeline_id) where pipeline_id is not null', {
      cast: { fact_status: 'facts.fact_status', confidence: 'facts.confidence_level' },
    }),
    '\n',
    upsert('facts.sites', sites, '(pipeline_id) where pipeline_id is not null', {
      cast: {
        status: 'facts.site_status',
        fact_status: 'facts.fact_status',
        confidence: 'facts.confidence_level',
      },
    }),
    '\n',
    // A citation is fully described by the record, source and claim it joins,
    // so re-inserting an identical one has nothing to say. Two rows asserting
    // the same source for the same claim is not twice the evidence.
    upsert('facts.citations', deduped, "(record_type, record_id, source_id, coalesce(claim, ''))", {
      doNothing: true,
      cast: { record_type: 'facts.citable_record' },
    }),
    '\n',
    upsert('facts.data_gaps', gaps, '(record_type, record_id, field_name)', {
      updateColumns: ['reason', 'source_id'],
      cast: { record_type: 'facts.citable_record', reason: 'facts.gap_reason' },
    }),
    '\n',
    '-- Derived links are proposals. Only a human sets confirmed, and until one\n',
    '-- does these are invisible to the public API by policy (0004).\n',
    // Matches links_unique_triple, which coalesces the three endpoints against
    // a sentinel uuid because null is not equal to null in a unique index.
    upsert(
      'facts.links',
      links,
      "(coalesce(site_id, '00000000-0000-0000-0000-000000000000'::uuid), " +
        "coalesce(entity_id, '00000000-0000-0000-0000-000000000000'::uuid), " +
        "coalesce(event_id, '00000000-0000-0000-0000-000000000000'::uuid))",
      { updateColumns: ['state'], cast: { state: 'facts.link_state' } },
    ),
    '\n',
    `insert into facts.ingest_runs (source_system, source_digest, loader_version, rows_by_table, notes)\nvalues (${literal(SOURCE_SYSTEM)}, ${literal(digest)}, ${literal(LOADER_VERSION)}, ${literal(report.counts)}, ${literal(
      `${report.rejected.length} rows rejected; ${orphaned} citations dropped for an unloaded source`,
    )});\n`,
    '\n',
    POST_LOAD_ASSERTIONS,
    '\ncommit;\n',
  ].join('');

  // --- report --------------------------------------------------------------
  console.log(`Pipeline digest sha256:${digest}`);
  for (const [table, count] of Object.entries(report.counts)) {
    console.log(`  ${table.padEnd(20)} ${count}`);
  }
  if (orphaned > 0) console.log(`  citations dropped (source not loaded): ${orphaned}`);

  if (report.rejected.length > 0) {
    console.log(`\n${report.rejected.length} rows rejected:`);
    for (const message of report.rejected) console.log(`  ${message}`);
  }

  const skipped = Object.entries(report.skippedRefs);
  if (skipped.length > 0) {
    console.log('\nSource references skipped (no destination table yet):');
    for (const [table, count] of skipped.sort((a, b) => b[1] - a[1])) {
      console.log(`  ${table.padEnd(24)} ${count}`);
    }
  }

  if (report.unmatchedLgas.length > 0) {
    console.log('\nCouncil names that look like variants of each other.');
    console.log('These are loaded verbatim. Resolving them is a human decision:');
    console.log('add rows to facts.lga_aliases. The loader never guesses.');
    for (const lga of report.unmatchedLgas) console.log(`  ${lga}`);
  }

  console.log(`\nTables written: ${ALLOWED_TABLES.join(', ')}`);
  console.log('No editorial table is reachable from this loader.');

  if (dryRun) {
    console.log('\n--dry-run: nothing written.');
    return;
  }

  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, sql, 'utf8');
  console.log(`\nWrote ${outPath} (${sql.length} bytes). Review it, then apply it.`);
}

/**
 * Assertions that run inside the load transaction, so a violation rolls the
 * whole thing back rather than leaving a half-loaded database.
 */
const POST_LOAD_ASSERTIONS = `-- Invariants, checked inside the transaction.
do $$
declare
  uncited integer;
  live_set integer;
  published integer;
begin
  select count(*) into uncited
    from facts.sites s
   where s.pipeline_id is not null
     and not exists (
       select 1 from facts.citations c
        where c.record_type = 'sites' and c.record_id = s.id
     );
  if uncited > 0 then
    raise exception 'ROLLED BACK: % loaded sites have no citation', uncited;
  end if;

  select count(*) into live_set
    from facts.sites
   where pipeline_id is not null and live_capacity_mw is not null;
  if live_set > 0 then
    raise exception 'ROLLED BACK: % loaded sites have a fabricated live capacity', live_set;
  end if;

  select count(*) into published
    from facts.links
   where state = 'confirmed' and confirmed_by is null;
  if published > 0 then
    raise exception 'ROLLED BACK: % links confirmed without a named human', published;
  end if;
end;
$$;
`;

main();
