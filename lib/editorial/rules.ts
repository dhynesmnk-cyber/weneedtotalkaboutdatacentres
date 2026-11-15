/**
 * The rules an essay, position or proposal must pass before the editor may
 * approve it.
 *
 * One implementation, run in three places: the command-line checker over the
 * Markdown drafts in editorial/essays/, the loader that turns those drafts
 * into SQL, and the live checker beside the editor at /admin. The database
 * enforces the rules it can see for itself (five sources, an opinion
 * section, a data date; supabase/migrations/0017); these add the ones only
 * the text can show.
 *
 * Mechanical checks cannot tell a fact from a lead or judge an argument. That
 * is the editor's reading (docs/REVIEW.md). What they can do is make sure no
 * sentence that states a number goes uncited, no paragraph of the record
 * stands without a source, and opinion stays below the divider.
 */

import type { PieceKind } from '@/lib/types';
import {
  blocks,
  cited,
  QUESTION_CITE,
  sections,
  sentences,
  SOURCE_CITE,
  statesNumber,
  TECHNICAL,
} from '@/lib/editorial/text';

/** docs/UX.md "Content production process: essays", in order. */
export const ESSAY_SECTIONS = [
  'The common perception',
  'What the records show',
  'Where the data is too thin',
  'What to watch next',
  'Our view',
] as const;

/** A "What if…?" proposal: the rules now, elsewhere, the cost, the argument. */
export const PROPOSAL_SECTIONS = [
  'Australia’s rules now',
  'Elsewhere',
  'What it would take',
  'Our proposal',
] as const;

/** The headings after which opinion is allowed. The divider is drawn before them. */
export const OPINION_HEADINGS = ['Our view', 'Our proposal'] as const;

/** docs/UX.md: fewer than five cited records and it is commentary, not an essay. */
export const MIN_SOURCES = 5;

export type Issue = { level: 'error' | 'warning'; message: string };

export interface EssayDraft {
  kind: PieceKind;
  title: string;
  standfirst?: string | null;
  body: string;
  data_as_of_date?: string | null;
  conflict?: string | null;
  named_parties?: readonly string[];
  story_cards?: readonly string[];
}

export interface CheckContext {
  /** Source ids the database holds, as pipeline ids (SRC_...). */
  sourceIds: ReadonlySet<string>;
  /** Research question ids the agenda holds (RG-nnn). */
  questionIds: ReadonlySet<string>;
  /**
   * Personal names the research holds, from the pipeline's lobbying records.
   * Supplied at check time, never committed as a list. Until legal review is
   * arranged, essays refer to people by role (docs/DELIVERY-PLAN.md, decision 7).
   */
  personalNames?: readonly string[];
}

const OPINION_LINE = new RegExp(`^## (${OPINION_HEADINGS.join('|')})[ \\t]*$`, 'm');

/**
 * The text before the opinion heading (the record) and from it on (the
 * argument). A piece with no opinion heading is all record.
 */
export function splitAtOpinion(body: string): {
  record: string;
  opinion: string | null;
  heading: (typeof OPINION_HEADINGS)[number] | null;
} {
  const m = OPINION_LINE.exec(body);
  if (!m) return { record: body, opinion: null, heading: null };
  return {
    record: body.slice(0, m.index),
    opinion: body.slice(m.index + m[0].length),
    heading: m[1] as (typeof OPINION_HEADINGS)[number],
  };
}

/** Source ids in the order the text first cites them. This is the numbering readers see. */
export function sourcesInOrder(body: string): string[] {
  const seen: string[] = [];
  for (const m of body.matchAll(SOURCE_CITE)) {
    const id = m[1]!;
    if (!seen.includes(id)) seen.push(id);
  }
  return seen;
}

/** Whether a piece touches Anthropic, which makes the model that drafts these essays. */
export function touchesAnthropic(draft: EssayDraft): boolean {
  return (
    /\b(Anthropic|Claude)\b/.test(draft.body) ||
    (draft.story_cards ?? []).includes('ST-016') ||
    [...draft.body.matchAll(QUESTION_CITE)].some((m) => m[1] === 'RG-012')
  );
}

function expectedSections(kind: PieceKind): readonly string[] | null {
  if (kind === 'essay') return ESSAY_SECTIONS;
  if (kind === 'proposal') return PROPOSAL_SECTIONS;
  return null;
}

/** A block that is structure, not prose: a heading, a rule, an image. */
function isStructural(block: string): boolean {
  return /^#{1,6}\s/.test(block) || /^(-{3,}|\*{3,})$/.test(block) || /^!\[/.test(block);
}

/** Every rule a draft must pass. Errors block approval; warnings are for the editor. */
export function checkEssay(draft: EssayDraft, ctx: CheckContext): Issue[] {
  const issues: Issue[] = [];
  const error = (message: string) => issues.push({ level: 'error', message });
  const warn = (message: string) => issues.push({ level: 'warning', message });

  if (!draft.title.trim()) error('The piece has no title.');
  if (!draft.body.trim()) {
    error('The piece has no text.');
    return issues;
  }
  if (!draft.standfirst?.trim()) warn('There is no standfirst: one or two sentences saying what the piece argues.');
  if (!draft.data_as_of_date) error('Set the date the records were current to (data as at).');

  // Structure.
  const { preamble, sections: found } = sections(draft.body);
  if (preamble.trim()) error('There is text before the first section heading.');
  // A straight apostrophe is the same heading as a curly one.
  const headings = found.map((s) => s.heading.replace(/'/g, '’'));
  const expected = expectedSections(draft.kind);
  if (expected && headings.join('|') !== expected.join('|')) {
    error(`The sections must be, in order: ${expected.join('; ')}. Found: ${headings.join('; ') || 'none'}.`);
  }
  if (draft.kind === 'position' && headings[headings.length - 1] !== 'Our view') {
    error('A position piece ends with an "Our view" section.');
  }

  const { record, opinion, heading } = splitAtOpinion(draft.body);
  if (!heading) {
    error('There is no "Our view" (or "Our proposal") section, so there is nowhere below the divider for the argument.');
  } else if (!opinion?.trim()) {
    error(`The "${heading}" section is empty.`);
  }

  // Citations: every id must exist.
  const all = cited(draft.body);
  for (const id of new Set(all.sources)) {
    if (!ctx.sourceIds.has(id)) error(`Cites ${id}, which the database does not hold.`);
  }
  for (const id of new Set(all.questions)) {
    if (!ctx.questionIds.has(id)) error(`Cites ${id}, which is not in the research agenda.`);
  }

  const distinct = new Set(all.sources).size;
  if ((draft.kind === 'essay' || draft.kind === 'proposal') && distinct < MIN_SOURCES) {
    error(`Cites ${distinct} source record${distinct === 1 ? '' : 's'}. An essay cites at least ${MIN_SOURCES}; below that it is commentary.`);
  }

  // The record: every paragraph and list item cites a source or an open question.
  for (const section of sections(record).sections) {
    for (const block of blocks(section.body)) {
      if (isStructural(block)) continue;
      const c = cited(block);
      if (!c.sources.length && !c.questions.length) {
        error(`${section.heading}: a paragraph cites nothing: ${JSON.stringify(block.slice(0, 70))}`);
      }
    }
  }

  // Anywhere, opinion included: a sentence that states a number cites it.
  for (const section of found) {
    for (const block of blocks(section.body)) {
      for (const s of sentences(block)) {
        const c = cited(s);
        if (statesNumber(s) && !c.sources.length && !c.questions.length) {
          error(`${section.heading}: a sentence states a number without a citation: ${JSON.stringify(s.slice(0, 80))}`);
        }
      }
    }
  }

  // Plain English for a general reader.
  const prose = draft.body.replace(SOURCE_CITE, '').replace(QUESTION_CITE, '');
  for (const [pattern, what] of TECHNICAL) {
    if (pattern.test(prose)) warn(`Mentions ${what}. Keep the mechanics in the hunt log unless the reader needs them.`);
  }

  // A conflict of interest is disclosed, not discovered.
  if (touchesAnthropic(draft) && !draft.conflict?.trim()) {
    error('This piece touches Anthropic, which makes the model that drafted it. Disclose that in the conflict field.');
  }

  // People by role, until legal review is arranged.
  const lowered = draft.body.toLowerCase();
  for (const name of ctx.personalNames ?? []) {
    const n = name.trim();
    if (n.length < 5 || !/\s/.test(n)) continue;
    if (lowered.includes(n.toLowerCase())) {
      error(`Names a person (${n}). Refer to people by their public role until legal review is arranged.`);
    }
  }
  if ((draft.named_parties ?? []).some((p) => !/\brole\b|\bby role\b/i.test(p))) {
    warn('Every named party should be described by role, with "(by role)" or "(quoted in role, not named)".');
  }

  return issues;
}

/** Whether any issue blocks approval. */
export function hasErrors(issues: readonly Issue[]): boolean {
  return issues.some((i) => i.level === 'error');
}
