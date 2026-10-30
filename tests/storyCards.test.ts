import { readdirSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import {
  blocks,
  checkCard,
  checkIndex,
  parseCard,
  sentences,
  type KnownIds,
} from '@/scripts/editorial/story-cards';

const KNOWN: KnownIds = {
  sourceIds: new Set(['SRC_A', 'SRC_B']),
  questionIds: new Set(['RG-001', 'RG-002']),
};

const FRONT = `---
id: ST-001
title: A test card
thread: money                 # money | communities-sovereignty
story_line: M1
questions: [RG-001]
sources: [SRC_A, SRC_B]
data_as_of: 2026-10-21
named_parties: []
conflict: null
status: draft
approved_by: null
approved_at: null
---
`;

const BODY = `
## What you heard
"It is all above board," the company said [SRC_A].

## The hunt
We asked who owns the land. The title names a company registered 4 days before lodgement [SRC_B].
The portal refused the next file [RG-001].

## What the record shows
- The company was registered in 2025 [SRC_B].

## Still unknown
Who stands behind it (RG-002). An ASIC extract would say [RG-002].

## Essay hooks
- What a reader assumes a company name tells them.
`;

function check(text: string, file = 'editorial/stories/ST-001-test-card.md') {
  const { card, problems } = parseCard(file, text);
  if (!card) return problems;
  return [...problems, ...checkCard(card, KNOWN)];
}

describe('story card rules', () => {
  it('passes a card that follows every rule', () => {
    expect(check(FRONT + BODY)).toEqual([]);
  });

  it('refuses a source the research database does not hold', () => {
    const out = check(FRONT.replace('SRC_B]', 'SRC_Z]') + BODY.replaceAll('SRC_B', 'SRC_Z'));
    expect(out.some((p) => p.includes('SRC_Z, which the research database does not hold'))).toBe(true);
  });

  it('refuses a number stated without a citation', () => {
    const out = check(FRONT + BODY.replace('The portal refused the next file [RG-001].', 'It cost $7 billion.'));
    expect(out.some((p) => p.includes('states a number without a citation'))).toBe(true);
  });

  it('refuses a record paragraph with no source', () => {
    const out = check(FRONT + BODY.replace('- The company was registered in 2025 [SRC_B].', '- The company is new.'));
    expect(out.some((p) => p.includes('What the record shows'))).toBe(true);
  });

  it('accepts an opening question when nobody public made the claim', () => {
    const body = BODY.replace('"It is all above board," the company said [SRC_A].', 'Who is behind the application?');
    const front = FRONT.replace('sources: [SRC_A, SRC_B]', 'sources: [SRC_B]');
    expect(check(front + body)).toEqual([]);
  });

  it('refuses an approval on a draft', () => {
    const out = check(FRONT.replace('approved_by: null', 'approved_by: someone').replace('approved_at: null', 'approved_at: 2026-10-21') + BODY);
    expect(out.some((p) => p.includes('a draft carries no approval'))).toBe(true);
  });

  it('refuses an approved card without who and when', () => {
    const out = check(FRONT.replace('status: draft', 'status: approved') + BODY);
    expect(out.some((p) => p.includes('names who approved it and when'))).toBe(true);
  });

  it('keeps the declared sources and the cited sources the same', () => {
    const out = check(FRONT.replace('sources: [SRC_A, SRC_B]', 'sources: [SRC_A]') + BODY);
    expect(out.some((p) => p.includes('does not list it in sources'))).toBe(true);
  });

  it('refuses facts in the essay hooks', () => {
    const out = check(FRONT + BODY.replace('- What a reader assumes', '- 61 generators show what a reader assumes'));
    expect(out.some((p) => p.includes('Essay hooks state a number'))).toBe(true);
  });

  it('refuses sections out of order or missing', () => {
    const out = check(FRONT + BODY.replace('## Still unknown', '## Next steps'));
    expect(out.some((p) => p.includes('sections must be, in order'))).toBe(true);
  });

  it('refuses a story line from the other thread', () => {
    const out = check(FRONT.replace('story_line: M1', 'story_line: C2') + BODY);
    expect(out.some((p) => p.includes("does not belong to thread 'money'"))).toBe(true);
  });

  it('refuses a file name that does not match the id', () => {
    const out = check(FRONT + BODY, 'editorial/stories/ST-002-test-card.md');
    expect(out.some((p) => p.includes('file name must be ST-001'))).toBe(true);
  });

  it('does not count identifiers as numbers', () => {
    expect(check(FRONT + BODY.replace('Who stands behind it (RG-002).', 'Who stands behind SSD-113934740 (RG-002).'))).toEqual([]);
    expect(check(FRONT + BODY.replace('Who stands behind it (RG-002).', 'Who stands behind S7, M4 and IC3e?'))).toEqual([]);
  });

  it('keeps the mechanics out of a card', () => {
    const out = check(FRONT + BODY.replace('The portal refused the next file [RG-001].', 'The portal answered 401 on page 27 [RG-001].'));
    expect(out.some((p) => p.includes('mentions an HTTP error code'))).toBe(true);
    expect(out.some((p) => p.includes('mentions a page reference'))).toBe(true);
  });

  it('does not mistake an amount of money for an error code', () => {
    const out = check(FRONT + BODY.replace('The portal refused the next file [RG-001].', 'It declared $7,500, then $1,500 of 500,000 [RG-001].'));
    expect(out.some((p) => p.includes('mentions an HTTP error code'))).toBe(false);
  });

  it('still counts a quantity written against its unit', () => {
    const out = check(FRONT + BODY.replace('Who stands behind it (RG-002).', 'It draws 612MW.'));
    expect(out.some((p) => p.includes('states a number without a citation'))).toBe(true);
  });
});

describe('blocks and sentences', () => {
  it('treats each list item as its own block', () => {
    expect(blocks('- one\n- two\n\nthree\nfour')).toEqual(['one', 'two', 'three four']);
  });

  it('splits after a closing quote', () => {
    expect(sentences('It said "no." Then it said yes [SRC_A].')).toEqual(['It said "no."', 'Then it said yes [SRC_A].']);
  });
});

describe('the index', () => {
  it('requires every card, with its status', () => {
    const { card } = parseCard('editorial/stories/ST-001-test-card.md', FRONT + BODY);
    expect(checkIndex('## Index\n\n| Card | Title | Line | Questions | Status |\n', [card!])).toEqual([
      'README index does not list ST-001',
    ]);
    expect(
      checkIndex('## Index\n\n| [ST-001](ST-001-test-card.md) | A test card | M1 | RG-001 | draft |\n', [card!]),
    ).toEqual([]);
  });
});

// The real cards, checked against the research database they cite.
describe('editorial/stories', () => {
  const dir = join(__dirname, '..', 'editorial', 'stories');
  const files = readdirSync(dir).filter((f) => /^ST-\d{3}-.*\.md$/.test(f)).sort();

  // Required at run time: the test bundler does not resolve node:sqlite as an import.
  const { DatabaseSync } = createRequire(import.meta.url)('node:sqlite') as typeof import('node:sqlite');
  const db = new DatabaseSync(
    join(__dirname, '..', 'data-pipeline', 'exports', 'australian_data_centre_observatory.db'),
    { readOnly: true },
  );
  const known: KnownIds = {
    sourceIds: new Set((db.prepare('SELECT id FROM sources').all() as { id: string }[]).map((r) => r.id)),
    questionIds: new Set(
      (db.prepare('SELECT id FROM research_gaps').all() as { id: number }[]).map(
        (r) => `RG-${String(r.id).padStart(3, '0')}`,
      ),
    ),
  };
  db.close();

  const cards = files.map((f) => parseCard(`editorial/stories/${f}`, readFileSync(join(dir, f), 'utf8')));

  it.each(files.map((f, i) => [f, i] as const))('%s follows the card rules', (_f, i) => {
    const { card, problems } = cards[i]!;
    expect([...problems, ...(card ? checkCard(card, known) : [])]).toEqual([]);
  });

  it('the README index lists every card with its status', () => {
    const readme = readFileSync(join(dir, 'README.md'), 'utf8');
    expect(checkIndex(readme, cards.flatMap((c) => (c.card ? [c.card] : [])))).toEqual([]);
  });
});
