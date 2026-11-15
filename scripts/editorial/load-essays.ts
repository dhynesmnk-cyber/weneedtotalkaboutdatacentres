/**
 * Checks the essay drafts in editorial/essays/ and emits the SQL that loads
 * them, unapproved, for the editor.
 *
 *   npm run check:essays              check every draft; exit 1 on any error
 *   npm run load:essays               check, then write .artifacts/load-essays.sql
 *   npx tsx scripts/editorial/load-essays.ts --out <file>
 *
 * The artefact is reviewed and applied by a person, after the research
 * pipeline load (docs/SUPABASE_SETUP.md). It loads drafts only: approval is
 * the editor's, at /admin, and no file, script or agent can set it.
 *
 * Ids are checked against the research database the drafts cite, as the story
 * cards are. The personal-name screen reads names from that database at run
 * time; no list of names is kept in the repository.
 */

import { mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { draftOf, essaysSql, parseEssayFile, type EssayFile } from '@/lib/editorial/essayFile';
import { checkEssay, type CheckContext } from '@/lib/editorial/rules';
import { cited } from '@/lib/editorial/text';

const LOADER_VERSION = 'load-essays 1.0.0';
const REPO_ROOT = join(__dirname, '..', '..');
const DIR = join(REPO_ROOT, 'editorial', 'essays');
const DB = join(REPO_ROOT, 'data-pipeline', 'exports', 'australian_data_centre_observatory.db');

/**
 * Personal names in the research, from the lobbying records ("Name, role").
 * Only the part before the comma, and only where it reads as a name of two or
 * three capitalised words, so a role such as "Minister for Planning" is not
 * mistaken for one.
 */
function personalNames(db: DatabaseSync): string[] {
  const rows = db.prepare('SELECT person FROM lobbying WHERE person IS NOT NULL').all() as { person: string }[];
  return rows
    .map((r) => r.person.split(',')[0]!.trim())
    .filter((n) => /^[A-Z][a-z'’-]+(?: [A-Z][a-z'’-]+){1,2}$/.test(n));
}

function context(): CheckContext {
  const db = new DatabaseSync(DB, { readOnly: true });
  try {
    return {
      sourceIds: new Set((db.prepare('SELECT id FROM sources').all() as { id: string }[]).map((r) => r.id)),
      questionIds: new Set(
        (db.prepare('SELECT id FROM research_gaps').all() as { id: number }[]).map(
          (r) => `RG-${String(r.id).padStart(3, '0')}`,
        ),
      ),
      personalNames: personalNames(db),
    };
  } finally {
    db.close();
  }
}

function main() {
  const args = process.argv.slice(2);
  const checkOnly = args.includes('--check');
  const outIndex = args.indexOf('--out');
  const outPath = outIndex >= 0 ? args[outIndex + 1]! : join(REPO_ROOT, '.artifacts', 'load-essays.sql');

  const files = readdirSync(DIR)
    .filter((f) => /^ES-\d{3}-.*\.md$/.test(f))
    .sort();
  const ctx = context();
  const essays: EssayFile[] = [];
  const errors: string[] = [];
  const warnings: string[] = [];
  const seen = new Map<string, string>();

  for (const f of files) {
    const rel = `editorial/essays/${f}`;
    const { essay, problems } = parseEssayFile(rel, readFileSync(join(DIR, f), 'utf8'));
    errors.push(...problems);
    if (!essay) continue;

    for (const unique of [essay.key, essay.row.slug]) {
      if (seen.has(unique)) errors.push(`${rel}: ${unique} is also used by ${seen.get(unique)}`);
      seen.set(unique, rel);
    }

    for (const issue of checkEssay(draftOf(essay), ctx)) {
      (issue.level === 'error' ? errors : warnings).push(`${rel}: ${issue.message}`);
    }

    const c = cited(essay.row.body);
    const citedSources = new Set(c.sources);
    const declared = new Set(essay.declaredSources);
    for (const s of citedSources) if (!declared.has(s)) errors.push(`${rel}: cites ${s} but does not list it in sources`);
    for (const s of declared) if (!citedSources.has(s)) errors.push(`${rel}: lists ${s} in sources but never cites it`);
    for (const q of new Set(c.questions)) {
      if (!essay.questions.includes(q)) errors.push(`${rel}: cites ${q} but does not list it in questions`);
    }
    essays.push(essay);
  }

  for (const w of warnings) console.warn(`note: ${w}`);
  if (errors.length) {
    for (const e of errors) console.error(`error: ${e}`);
    console.error(`\n${errors.length} error(s) in ${files.length} draft(s). Nothing written.`);
    process.exit(1);
  }

  console.log(`${files.length} draft(s) pass the essay rules.`);
  if (checkOnly) return;

  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, essaysSql(essays, { loaderVersion: LOADER_VERSION, generatedFrom: 'editorial/essays/' }), 'utf8');
  console.log(`Wrote ${outPath}. Review it, then apply it after the pipeline load.`);
}

main();
