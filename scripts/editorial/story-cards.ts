/**
 * Checks story cards (editorial/stories/ST-nnn-*.md) against the rules in
 * editorial/stories/README.md.
 *
 * A card is editorial, but every fact in it is a record in the research
 * database. These checks make that mechanical where it can be: every cited id
 * must exist, every paragraph that tells the record must cite it, every
 * sentence that states a number must carry its citation, and a draft must not
 * carry an approval. They cannot tell a fact from a lead or judge a sentence
 * without a number; that is the author's review (docs/REVIEW.md).
 *
 * Pure functions: the caller supplies the card text and the ids the research
 * database holds.
 */

export const SECTIONS = [
  'What you heard',
  'The hunt',
  'What the record shows',
  'Still unknown',
  'Essay hooks',
] as const;

const THREADS = ['money', 'communities-sovereignty'] as const;
const STATUSES = ['draft', 'approved', 'withdrawn'] as const;
const LINES: Record<(typeof THREADS)[number], RegExp> = {
  money: /^M[1-5]$/,
  'communities-sovereignty': /^C[1-3]$/,
};
const KEYS = [
  'id',
  'title',
  'thread',
  'story_line',
  'questions',
  'sources',
  'data_as_of',
  'named_parties',
  'conflict',
  'status',
  'approved_by',
  'approved_at',
] as const;

const HUNT_MAX_WORDS = 300;
// The author's direction (2026-10-21): brush over the mechanics, give the drama.
// These belong in the hunt log and the database, not in a card for a general reader.
const TECHNICAL: [RegExp, string][] = [
  // Not inside an amount: $7,500, 2,403 or 500,000 are money, not error codes.
  [/(?<![\d,.])\b(?:401|403|404|500)\b(?![,.]\d)/, 'an HTTP error code'],
  [/robots\.txt/i, 'robots.txt'],
  [/\bSHA-?256\b|\bchecksum\b/i, 'a checksum'],
  [/\b(?:pages?|pp?\.)\s?\d+/i, 'a page reference'],
  [/\.(?:pdf|json|html?|csv)\b|\b(?:PDF|JSON|CSV|HTML)\b/, 'a file format'],
  [/\bMVA\b|\bkV\b|\bPUE\b|\bWUE\b/, 'an engineering unit'],
];
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const DATE_OR_TIME = /^\d{4}-\d{2}-\d{2}([T ][\d:.]+(Z|[+-]\d{2}:?\d{2})?)?$/;
const SOURCE_CITE = /\[(SRC_[A-Za-z0-9_]+)\]/g;
const QUESTION_CITE = /\[(RG-\d{3})\]/g;
// Identifiers carry digits without stating a quantity: citations, question and
// planning references, and facility codes such as S7, M4, SYD3 or IC3e.
const IDENTIFIERS = /\[(?:SRC_[A-Za-z0-9_]+|RG-\d{3})\]|\b(?:RG|ST|SSD)-\d+\b|\b[A-Z]{1,4}\d{1,3}[a-z]?\b/g;

export type FrontValue = string | string[] | null;

export interface StoryCard {
  file: string;
  front: Record<string, FrontValue>;
  sections: { heading: string; body: string }[];
}

export interface KnownIds {
  sourceIds: ReadonlySet<string>;
  questionIds: ReadonlySet<string>;
}

function parseValue(raw: string): FrontValue {
  const v = raw.trim();
  if (v === 'null' || v === '~' || v === '') return null;
  if (v.startsWith('[') && v.endsWith(']')) {
    return v
      .slice(1, -1)
      .split(',')
      .map((s) => unquote(s.trim()))
      .filter((s) => s.length > 0);
  }
  return unquote(v);
}

function unquote(s: string): string {
  return /^(['"]).*\1$/.test(s) ? s.slice(1, -1) : s;
}

/** Split a card into its front matter and its level-two sections. */
export function parseCard(file: string, text: string): { card: StoryCard | null; problems: string[] } {
  const problems: string[] = [];
  const m = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(text.replace(/\r\n/g, '\n'));
  if (!m) return { card: null, problems: [`${file}: no front matter between --- lines`] };
  const [, head = '', rest = ''] = m;

  const front: Record<string, FrontValue> = {};
  for (const line of head.split('\n')) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const kv = /^([a-z_]+):(.*)$/.exec(line.replace(/\s+#.*$/, ''));
    if (!kv) {
      problems.push(`${file}: cannot read front matter line ${JSON.stringify(line)}`);
      continue;
    }
    front[kv[1]!] = parseValue(kv[2]!);
  }

  const sections: { heading: string; body: string }[] = [];
  const parts = rest.split(/^## (.+)$/m);
  if ((parts[0] ?? '').trim()) problems.push(`${file}: text before the first section`);
  for (let i = 1; i < parts.length; i += 2) {
    sections.push({ heading: (parts[i] ?? '').trim(), body: parts[i + 1] ?? '' });
  }
  return { card: { file, front, sections }, problems };
}

/** Paragraphs and list items, each as one block of text. */
export function blocks(body: string): string[] {
  const out: string[] = [];
  let current: string[] = [];
  const flush = () => {
    if (current.length) out.push(current.join(' ').trim());
    current = [];
  };
  for (const line of body.split('\n')) {
    if (!line.trim()) {
      flush();
    } else if (/^\s*(?:[-*]|\d+\.)\s+/.test(line)) {
      flush();
      current.push(line.replace(/^\s*(?:[-*]|\d+\.)\s+/, ''));
    } else {
      current.push(line.trim());
    }
  }
  flush();
  return out.filter((b) => b.length > 0);
}

/** Sentences, split after terminal punctuation and any closing quote or bracket. */
export function sentences(block: string): string[] {
  return block
    .split(/(?<=[.!?]["'”’)\]]*)\s+(?=["'“‘(*]?[A-Z0-9])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function cited(text: string): { sources: string[]; questions: string[] } {
  return {
    sources: [...text.matchAll(SOURCE_CITE)].map((x) => x[1]!),
    questions: [...text.matchAll(QUESTION_CITE)].map((x) => x[1]!),
  };
}

function statesNumber(sentence: string): boolean {
  return /\d/.test(sentence.replace(IDENTIFIERS, ''));
}

function list(front: Record<string, FrontValue>, key: string): string[] {
  const v = front[key];
  return Array.isArray(v) ? v : [];
}

/** Every rule a card must pass. An empty list means it passes. */
export function checkCard(card: StoryCard, known: KnownIds): string[] {
  const p: string[] = [];
  const f = card.front;
  const at = (msg: string) => p.push(`${card.file}: ${msg}`);

  for (const key of Object.keys(f)) {
    if (!(KEYS as readonly string[]).includes(key)) at(`unknown front matter key '${key}'`);
  }
  for (const key of KEYS) {
    if (!(key in f)) at(`front matter is missing '${key}'`);
  }

  const id = f['id'];
  if (typeof id !== 'string' || !/^ST-\d{3}$/.test(id)) at(`id must look like ST-001`);
  else if (!new RegExp(`^${id}-[a-z0-9-]+\\.md$`).test(card.file.split('/').pop() ?? '')) {
    at(`file name must be ${id}-short-slug.md`);
  }
  if (typeof f['title'] !== 'string' || !f['title']) at('title is empty');

  const thread = f['thread'];
  if (typeof thread !== 'string' || !(THREADS as readonly string[]).includes(thread)) {
    at(`thread must be one of ${THREADS.join(', ')}`);
  } else if (typeof f['story_line'] !== 'string' || !LINES[thread as (typeof THREADS)[number]].test(f['story_line'])) {
    at(`story_line does not belong to thread '${thread}'`);
  }

  const questions = list(f, 'questions');
  if (!questions.length) at('questions lists no research question');
  for (const q of questions) {
    if (!known.questionIds.has(q)) at(`question ${q} is not in the research agenda`);
  }

  if (typeof f['data_as_of'] !== 'string' || !DATE.test(f['data_as_of'])) at('data_as_of must be a date');
  if (!Array.isArray(f['named_parties'])) at('named_parties must be a list, [] when nobody is named');

  const status = f['status'];
  const approver = f['approved_by'];
  const approvedAt = f['approved_at'];
  if (typeof status !== 'string' || !(STATUSES as readonly string[]).includes(status)) {
    at(`status must be one of ${STATUSES.join(', ')}`);
  }
  const approved = approver !== null && approver !== undefined && approvedAt !== null && approvedAt !== undefined;
  const unapproved = (approver === null || approver === undefined) && (approvedAt === null || approvedAt === undefined);
  if (!approved && !unapproved) at('approved_by and approved_at are set together or not at all');
  if (status === 'draft' && !unapproved) at('a draft carries no approval; only the author sets one');
  if (status === 'approved' && !approved) at('an approved card names who approved it and when');
  if (typeof approvedAt === 'string' && !DATE_OR_TIME.test(approvedAt)) at('approved_at must be a date or time');

  const headings = card.sections.map((s) => s.heading);
  if (headings.join('|') !== SECTIONS.join('|')) {
    at(`sections must be, in order: ${SECTIONS.join('; ')} (found: ${headings.join('; ') || 'none'})`);
  }

  const citedSources = new Set<string>();
  for (const { heading, body } of card.sections) {
    const c = cited(body);
    c.sources.forEach((s) => citedSources.add(s));
    for (const s of c.sources) if (!known.sourceIds.has(s)) at(`cites ${s}, which the research database does not hold`);
    for (const q of c.questions) if (!known.questionIds.has(q)) at(`cites ${q}, which is not in the research agenda`);

    for (const [pattern, what] of TECHNICAL) {
      if (pattern.test(body.replace(SOURCE_CITE, '').replace(QUESTION_CITE, ''))) {
        at(`${heading} mentions ${what}; keep the mechanics in the hunt log`);
      }
    }

    if (heading === 'Essay hooks') {
      if (c.sources.length) at('Essay hooks cite sources; facts belong in the sections above');
      if (statesNumber(body)) at('Essay hooks state a number; hooks suggest angles and state no facts');
      continue;
    }

    for (const block of blocks(body)) {
      const b = cited(block);
      const short = JSON.stringify(block.slice(0, 60));
      if (heading === 'What you heard' && !b.sources.length && !block.endsWith('?')) {
        at(`What you heard: ${short} quotes no source; if nobody said it, ask the question instead`);
      }
      if (heading === 'What the record shows' && !b.sources.length) {
        at(`What the record shows: ${short} cites no source`);
      }
      if (heading === 'The hunt' && !b.sources.length && !b.questions.length) {
        at(`The hunt: ${short} cites neither a source nor a research question`);
      }
      for (const s of sentences(block)) {
        const sc = cited(s);
        if (statesNumber(s) && !sc.sources.length && !sc.questions.length) {
          at(`${heading}: a sentence states a number without a citation: ${JSON.stringify(s.slice(0, 80))}`);
        }
      }
    }

    if (heading === 'The hunt') {
      const words = body.replace(IDENTIFIERS, '').split(/\s+/).filter(Boolean).length;
      if (words > HUNT_MAX_WORDS) at(`The hunt runs to ${words} words; keep it to ${HUNT_MAX_WORDS}`);
    }
  }

  const declared = new Set(list(f, 'sources'));
  for (const s of citedSources) if (!declared.has(s)) at(`cites ${s} but does not list it in sources`);
  for (const s of declared) if (!citedSources.has(s)) at(`lists ${s} in sources but never cites it`);

  return p;
}

/** The index table in editorial/stories/README.md must list every card, with its status. */
export function checkIndex(readme: string, cards: StoryCard[]): string[] {
  const p: string[] = [];
  const index = readme.split(/^## Index$/m)[1] ?? '';
  const rows = new Map<string, string>();
  for (const line of index.split('\n')) {
    const cells = line.split('|').map((c) => c.trim());
    const id = /ST-\d{3}/.exec(cells[1] ?? '')?.[0];
    if (id) rows.set(id, cells[5] ?? '');
  }
  for (const card of cards) {
    const id = card.front['id'];
    if (typeof id !== 'string') continue;
    const status = rows.get(id);
    if (status === undefined) p.push(`README index does not list ${id}`);
    else if (status.toLowerCase() !== String(card.front['status'])) {
      p.push(`README index gives ${id} status '${status}', the card says '${String(card.front['status'])}'`);
    }
    rows.delete(id);
  }
  for (const id of rows.keys()) p.push(`README index lists ${id}, which has no card`);
  return p;
}
