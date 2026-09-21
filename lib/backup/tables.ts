/**
 * What the backup covers, and what each table is worth.
 *
 * This project does not need to back up everything equally, and saying so
 * precisely is what makes a free backup defensible where point in time
 * recovery would cost $100 a month.
 *
 * Most of the fact layer is *derived*: `scripts/ingestion/load-pipeline.ts`
 * rebuilds it from `data-pipeline/`, which is SQLite committed to git, and the
 * load is idempotent. Losing those rows costs one command, not a research
 * programme. They are still exported — a backup that omits them cannot be used
 * to answer "what did the site say last Tuesday" — but they are not what the
 * backup exists for.
 *
 * The rest is *curated*: decisions a human made, in Postgres, that no
 * automated process can recreate. A confirmed link, a coordinate with a method
 * and a source, an approved council, a published essay. These have no upstream
 * copy anywhere. If they are lost they are gone, and re-deriving them is not
 * possible by definition — derivation is what they were created to override.
 *
 * The classification is per table, but two curated things live inside derived
 * tables and are called out in CURATED_COLUMNS below.
 */

/** Whether a table can be rebuilt from `data-pipeline/`, or only from this backup. */
export type Recoverability = 'derived' | 'curated';

export interface BackupTable {
  /** Schema-qualified name, as it appears in SQL. */
  readonly name: string;
  /** PostgREST needs the schema and the bare table separately. */
  readonly schema: 'facts' | 'editorial';
  readonly table: string;
  /** Primary key columns, used as the conflict target on restore. */
  readonly primaryKey: readonly string[];
  readonly recoverability: Recoverability;
  /** Why this table is classified the way it is. */
  readonly note: string;
}

/**
 * Every table in both schemas, in an order safe to restore in.
 *
 * Order is foreign key order, not alphabetical: sources before the citations
 * that reference them, sites and entities before the links that join them. A
 * restore applies these top to bottom in one transaction.
 *
 * This list is asserted against the live database by the export itself, so a
 * table added in a migration and forgotten here fails the backup loudly rather
 * than being silently omitted from every future backup.
 */
export const BACKUP_TABLES: readonly BackupTable[] = [
  {
    name: 'facts.sources',
    schema: 'facts',
    table: 'sources',
    primaryKey: ['id'],
    recoverability: 'derived',
    note: 'Rebuilt by the pipeline loader from data-pipeline/.',
  },
  {
    name: 'facts.entities',
    schema: 'facts',
    table: 'entities',
    primaryKey: ['id'],
    recoverability: 'derived',
    note: 'Rebuilt by the loader, except major_flag. See CURATED_COLUMNS.',
  },
  {
    name: 'facts.sites',
    schema: 'facts',
    table: 'sites',
    primaryKey: ['id'],
    recoverability: 'derived',
    note: 'Rebuilt by the loader, except coordinates. See CURATED_COLUMNS.',
  },
  {
    name: 'facts.events',
    schema: 'facts',
    table: 'events',
    primaryKey: ['id'],
    recoverability: 'curated',
    note: 'The loader does not write events. Every row here was entered by hand.',
  },
  {
    name: 'facts.citations',
    schema: 'facts',
    table: 'citations',
    primaryKey: ['id'],
    recoverability: 'derived',
    note: 'Rebuilt by the loader from the pipeline source references.',
  },
  {
    name: 'facts.data_gaps',
    schema: 'facts',
    table: 'data_gaps',
    primaryKey: ['id'],
    recoverability: 'derived',
    note: 'Rebuilt by the loader. Every derived gap reads "unknown".',
  },
  {
    name: 'facts.links',
    schema: 'facts',
    table: 'links',
    primaryKey: ['id'],
    recoverability: 'derived',
    note: 'Loaded as proposed. A confirmed link is curated. See CURATED_COLUMNS.',
  },
  {
    name: 'facts.lga_aliases',
    schema: 'facts',
    table: 'lga_aliases',
    primaryKey: ['alias'],
    recoverability: 'curated',
    note: 'Human-approved council equivalences. The loader never writes here.',
  },
  {
    name: 'facts.council_watchlist',
    schema: 'facts',
    table: 'council_watchlist',
    primaryKey: ['id'],
    recoverability: 'curated',
    note: 'The approved council list. Each row carries who approved it and when.',
  },
  {
    name: 'facts.research_agenda',
    schema: 'facts',
    table: 'research_agenda',
    primaryKey: ['id'],
    recoverability: 'curated',
    note: 'Open research questions and their resolutions. Edited in place by hand.',
  },
  {
    name: 'facts.ingest_runs',
    schema: 'facts',
    table: 'ingest_runs',
    primaryKey: ['id'],
    recoverability: 'curated',
    note: 'The audit trail of what was loaded when. A re-load appends, it does not restore history.',
  },
  {
    name: 'editorial.essays',
    schema: 'editorial',
    table: 'essays',
    primaryKey: ['id'],
    recoverability: 'curated',
    note: 'Published analysis. No loader can reach this schema at all.',
  },
  {
    name: 'editorial.case_studies',
    schema: 'editorial',
    table: 'case_studies',
    primaryKey: ['id'],
    recoverability: 'curated',
    note: 'Published analysis. No loader can reach this schema at all.',
  },
];

/**
 * Curated values that live inside otherwise derived tables.
 *
 * Re-running the loader over a restored database will not clobber these — the
 * loader's upsert lists the columns it owns and these are not among them — but
 * they are the reason a "just re-run the loader" recovery is not sufficient on
 * its own, and they are worth naming so that is not rediscovered during an
 * incident.
 */
export const CURATED_COLUMNS: readonly { table: string; columns: readonly string[]; why: string }[] = [
  {
    table: 'facts.sites',
    columns: ['lat', 'lng'],
    why: 'Geocoding is curation with a source per point. The importer may not invent one.',
  },
  {
    table: 'facts.entities',
    columns: ['major_flag'],
    why: 'Whether an entity is prominent enough to profile is a human judgement.',
  },
  {
    table: 'facts.links',
    columns: ['state', 'confirmed_by', 'confirmed_at'],
    why: 'Derivation proposes a link; only a named human confirms one.',
  },
];

export function curatedTables(): readonly BackupTable[] {
  return BACKUP_TABLES.filter((t) => t.recoverability === 'curated');
}

export function tableByName(name: string): BackupTable | undefined {
  return BACKUP_TABLES.find((t) => t.name === name);
}
