/**
 * Text helpers shared by every editorial checker: the story cards
 * (scripts/editorial/story-cards.ts), the essay checker (lib/editorial/rules.ts)
 * and the editor's live checker at /admin.
 *
 * Pure functions over Markdown text. Nothing here reads a database; callers
 * supply the ids a citation may name.
 */

/** A source citation as written in the text: [SRC_NSWGUIDE26]. */
export const SOURCE_CITE = /\[(SRC_[A-Za-z0-9_]+)\]/g;

/** A research question cited as written in the text: [RG-070]. */
export const QUESTION_CITE = /\[(RG-\d{3})\]/g;

// Identifiers carry digits without stating a quantity: citations, question and
// planning references, and facility codes such as S7, M4, SYD3 or IC3e.
export const IDENTIFIERS = /\[(?:SRC_[A-Za-z0-9_]+|RG-\d{3})\]|\b(?:RG|ST|SSD|ES)-\d+\b|\b[A-Z]{1,4}\d{1,3}[a-z]?\b/g;

/**
 * Mechanics that belong in the hunt log and the database, not in prose for a
 * general reader (the author's direction, 2026-10-21).
 */
export const TECHNICAL: readonly [RegExp, string][] = [
  // Not inside an amount: $7,500, 2,403 or 500,000 are money, not error codes.
  [/(?<![\d,.])\b(?:401|403|404|500)\b(?![,.]\d)/, 'an HTTP error code'],
  [/robots\.txt/i, 'robots.txt'],
  [/\bSHA-?256\b|\bchecksum\b/i, 'a checksum'],
  [/\b(?:pages?|pp?\.)\s?\d+/i, 'a page reference'],
  [/\.(?:pdf|json|html?|csv)\b|\b(?:PDF|JSON|CSV|HTML)\b/, 'a file format'],
  [/\bMVA\b|\bkV\b|\bPUE\b|\bWUE\b/, 'an engineering unit'],
];

export type FrontValue = string | string[] | null;

function unquote(s: string): string {
  return /^(['"]).*\1$/.test(s) ? s.slice(1, -1) : s;
}

function parseValue(raw: string): FrontValue {
  const v = raw.trim();
  if (v === 'null' || v === '~' || v === '') return null;
  if (v.startsWith('[') && v.endsWith(']')) {
    return splitList(v.slice(1, -1));
  }
  return unquote(v);
}

/** Split a flow list on commas that are not inside quotes. */
function splitList(inner: string): string[] {
  const out: string[] = [];
  let current = '';
  let quote: string | null = null;
  for (const ch of inner) {
    if (quote) {
      if (ch === quote) quote = null;
      current += ch;
    } else if (ch === '"' || ch === "'") {
      quote = ch;
      current += ch;
    } else if (ch === ',') {
      out.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  out.push(current);
  return out.map((s) => unquote(s.trim())).filter((s) => s.length > 0);
}

/**
 * Front matter between --- lines, as flat keys with string, list or null
 * values. The subset of YAML the cards and essays use, and no more, so a typo
 * fails loudly instead of being read as something else.
 */
export function parseFrontMatter(text: string): {
  front: Record<string, FrontValue>;
  body: string;
  problems: string[];
} {
  const problems: string[] = [];
  const m = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(text.replace(/\r\n/g, '\n'));
  if (!m) return { front: {}, body: text, problems: ['no front matter between --- lines'] };
  const [, head = '', body = ''] = m;

  const front: Record<string, FrontValue> = {};
  for (const line of head.split('\n')) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const kv = /^([a-z_]+):(.*)$/.exec(line.replace(/\s+#[^"']*$/, ''));
    if (!kv) {
      problems.push(`cannot read front matter line ${JSON.stringify(line)}`);
      continue;
    }
    front[kv[1]!] = parseValue(kv[2]!);
  }
  return { front, body, problems };
}

/** Level-two sections, in order, and any text before the first. */
export function sections(body: string): { preamble: string; sections: { heading: string; body: string }[] } {
  const parts = body.split(/^## (.+)$/m);
  const out: { heading: string; body: string }[] = [];
  for (let i = 1; i < parts.length; i += 2) {
    out.push({ heading: (parts[i] ?? '').trim(), body: parts[i + 1] ?? '' });
  }
  return { preamble: parts[0] ?? '', sections: out };
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

/** The source and question ids a piece of text cites. */
export function cited(text: string): { sources: string[]; questions: string[] } {
  return {
    sources: [...text.matchAll(SOURCE_CITE)].map((x) => x[1]!),
    questions: [...text.matchAll(QUESTION_CITE)].map((x) => x[1]!),
  };
}

/** Whether a sentence states a quantity, ignoring ids that merely contain digits. */
export function statesNumber(sentence: string): boolean {
  return /\d/.test(sentence.replace(IDENTIFIERS, ''));
}
