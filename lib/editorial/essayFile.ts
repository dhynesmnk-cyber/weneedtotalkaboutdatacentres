/**
 * Essay drafts as files: editorial/essays/ES-nnn-slug.md.
 *
 * An agent writes a draft as Markdown with front matter, through a pull
 * request, like a story card. scripts/editorial/load-essays.ts turns the
 * drafts into a SQL artefact that a person reviews and applies; the drafts
 * then appear, unapproved, at /admin for the editor. See
 * editorial/essays/README.md.
 *
 * Pure: parsing, checking the front matter, and emitting SQL. The script does
 * the file and database reading.
 */

import { createHash } from 'node:crypto';
import { uuidV5 } from '@/lib/ingestion/identity';
import { literal } from '@/lib/ingestion/sql';
import { parseFrontMatter, type FrontValue } from '@/lib/editorial/text';
import type { EssayDraft } from '@/lib/editorial/rules';
import { PIECE_KINDS, type PieceKind } from '@/lib/types';

export const ESSAY_KEYS = [
  'id',
  'slug',
  'kind',
  'title',
  'standfirst',
  'story_cards',
  'questions',
  'sources',
  'data_as_of',
  'named_parties',
  'conflict',
  'tags',
  'youtube_id',
  'proposal_no',
  'status',
] as const;

/** Only the editor approves, in /admin. A file that claims approval is refused. */
const FORBIDDEN = ['approved_by', 'approved_at', 'publish_date'] as const;

export interface EssayFile {
  file: string;
  sha256: string;
  key: string;
  row: {
    id: string;
    title: string;
    slug: string;
    kind: PieceKind;
    standfirst: string | null;
    body: string;
    tags: string[];
    youtube_id: string | null;
    data_as_of_date: string | null;
    conflict: string | null;
    named_parties: string[];
    story_cards: string[];
    proposal_no: number | null;
    source_file: string;
    source_sha256: string;
  };
  declaredSources: string[];
  questions: string[];
}

const str = (v: FrontValue | undefined) => (typeof v === 'string' ? v : null);
const list = (v: FrontValue | undefined) => (Array.isArray(v) ? v : []);

/** The row a draft file loads as, and anything wrong with its front matter. */
export function parseEssayFile(file: string, text: string): { essay: EssayFile | null; problems: string[] } {
  const { front, body, problems: parseProblems } = parseFrontMatter(text);
  const problems = parseProblems.map((p) => `${file}: ${p}`);
  const at = (m: string) => problems.push(`${file}: ${m}`);

  for (const key of Object.keys(front)) {
    if ((FORBIDDEN as readonly string[]).includes(key)) {
      at(`'${key}' is set by the editor at /admin, never in a draft file`);
    } else if (!(ESSAY_KEYS as readonly string[]).includes(key)) {
      at(`unknown front matter key '${key}'`);
    }
  }

  const key = str(front['id']);
  if (!key || !/^ES-\d{3}$/.test(key)) at('id must look like ES-001');
  const slug = str(front['slug']);
  if (!slug || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) at('slug must be lowercase words joined by hyphens');
  if (key && slug && !file.endsWith(`${key}-${slug}.md`)) at(`file name must be ${key}-${slug}.md`);

  const kind = str(front['kind']) as PieceKind | null;
  if (!kind || !PIECE_KINDS.includes(kind)) at(`kind must be one of ${PIECE_KINDS.join(', ')}`);
  const title = str(front['title']);
  if (!title) at('title is empty');
  if (front['status'] !== 'draft') at("status must be 'draft'; the editor approves in /admin");

  const dataAsOf = str(front['data_as_of']);
  if (dataAsOf && !/^\d{4}-\d{2}-\d{2}$/.test(dataAsOf)) at('data_as_of must be a date');
  if (!Array.isArray(front['named_parties'])) at('named_parties must be a list, [] when nobody is named');

  const proposalRaw = str(front['proposal_no']);
  const proposalNo = proposalRaw ? Number(proposalRaw) : null;
  if (kind === 'proposal' && !(proposalNo && proposalNo >= 1 && proposalNo <= 9)) at('a proposal needs proposal_no 1 to 9');
  if (kind !== 'proposal' && proposalNo !== null) at('only a proposal has a proposal_no');

  if (problems.length || !key || !slug || !kind || !title) return { essay: null, problems };

  const sha256 = createHash('sha256').update(text).digest('hex');
  return {
    essay: {
      file,
      sha256,
      key,
      row: {
        id: uuidV5(`essay:${key}`),
        title,
        slug,
        kind,
        standfirst: str(front['standfirst']),
        body: `${body.trim()}\n`,
        tags: list(front['tags']),
        youtube_id: str(front['youtube_id']),
        data_as_of_date: dataAsOf,
        conflict: str(front['conflict']),
        named_parties: list(front['named_parties']),
        story_cards: list(front['story_cards']),
        proposal_no: proposalNo,
        source_file: file,
        source_sha256: sha256,
      },
      declaredSources: list(front['sources']),
      questions: list(front['questions']),
    },
    problems,
  };
}

/** The draft as the checker in lib/editorial/rules.ts reads it. */
export function draftOf(essay: EssayFile): EssayDraft {
  const { row } = essay;
  return {
    kind: row.kind,
    title: row.title,
    standfirst: row.standfirst,
    body: row.body,
    data_as_of_date: row.data_as_of_date,
    conflict: row.conflict,
    named_parties: row.named_parties,
    story_cards: row.story_cards,
  };
}

function textArray(values: readonly string[]): string {
  return values.length ? `array[${values.map(literal).join(', ')}]::text[]` : `'{}'::text[]`;
}

const COLUMNS = [
  'id',
  'title',
  'slug',
  'kind',
  'standfirst',
  'body',
  'tags',
  'youtube_id',
  'data_as_of_date',
  'conflict',
  'named_parties',
  'story_cards',
  'proposal_no',
  'source_file',
  'source_sha256',
] as const;

function values(essay: EssayFile): string {
  const r = essay.row;
  return [
    literal(r.id),
    literal(r.title),
    literal(r.slug),
    `${literal(r.kind)}::editorial.piece_kind`,
    literal(r.standfirst),
    literal(r.body),
    textArray(r.tags),
    literal(r.youtube_id),
    r.data_as_of_date ? `${literal(r.data_as_of_date)}::date` : 'null',
    literal(r.conflict),
    textArray(r.named_parties),
    textArray(r.story_cards),
    r.proposal_no === null ? 'null' : String(r.proposal_no),
    literal(r.source_file),
    literal(r.source_sha256),
  ].join(', ');
}

/**
 * The artefact: drafts in, never an approval.
 *
 * A row the editor has approved or edited in /admin is left alone. From then
 * on the database holds the text that matters, and a newer file is the
 * agent's proposal, reported rather than merged. The closing block checks
 * that every row either carries this artefact's text as an unapproved draft
 * or was left alone for that reason, and rolls everything back otherwise.
 */
export function essaysSql(essays: readonly EssayFile[], meta: { loaderVersion: string; generatedFrom: string }): string {
  const out: string[] = [
    `-- Generated by ${meta.loaderVersion}. Do not edit by hand.`,
    `--`,
    `-- Essay drafts from ${meta.generatedFrom}: ${essays.length} file(s).`,
    `-- Drafts only. Nothing here approves or publishes; the editor does that at`,
    `-- /admin. A piece the editor has approved or edited is left untouched.`,
    `--`,
    `-- Apply after the research pipeline load: the citation trigger refuses any`,
    `-- [SRC_...] id the database does not hold, and the whole file rolls back.`,
    ``,
    `begin;`,
    ``,
  ];

  if (essays.length) {
    const update = COLUMNS.filter((c) => c !== 'id')
      .map((c) => `${c} = excluded.${c}`)
      .join(',\n      ');
    out.push(
      `insert into editorial.essays (${COLUMNS.join(', ')})`,
      `values`,
      essays.map((e) => `  (${values(e)})`).join(',\n'),
      `on conflict (id) do update`,
      `  set ${update}`,
      `  where editorial.essays.approved_at is null`,
      `    and editorial.essays.edited_in_admin_at is null;`,
      ``,
      `do $$`,
      `declare`,
      `  piece record;`,
      `begin`,
      `  for piece in`,
      `    select e.id, e.source_file, e.source_sha256, e.approved_at, e.edited_in_admin_at, f.sha`,
      `      from (values`,
      essays.map((e) => `        (${literal(e.row.id)}::uuid, ${literal(e.sha256)})`).join(',\n'),
      `      ) as f(id, sha)`,
      `      join editorial.essays e on e.id = f.id`,
      `  loop`,
      `    if piece.approved_at is not null or piece.edited_in_admin_at is not null then`,
      `      if piece.source_sha256 is distinct from piece.sha then`,
      `        raise notice 'Left alone, the editor has it: % (the file has changed since)', piece.source_file;`,
      `      end if;`,
      `    elsif piece.source_sha256 is distinct from piece.sha then`,
      `      raise exception 'ROLLED BACK: % did not load as this file''s draft', piece.source_file;`,
      `    end if;`,
      `  end loop;`,
      `end;`,
      `$$;`,
      ``,
    );
  }

  out.push(`commit;`, ``);
  return out.join('\n');
}
