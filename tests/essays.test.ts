import { describe, expect, it } from 'vitest';
import {
  checkEssay,
  hasErrors,
  sourcesInOrder,
  splitAtOpinion,
  type CheckContext,
  type EssayDraft,
} from '@/lib/editorial/rules';

const ctx: CheckContext = {
  sourceIds: new Set(['SRC_A', 'SRC_B', 'SRC_C', 'SRC_D', 'SRC_E', 'SRC_F']),
  questionIds: new Set(['RG-070', 'RG-012']),
  personalNames: ['Jane Example Citizen'],
};

const GOOD = `## The common perception
The guidelines say six in seven requests are phantom [SRC_A].

## What the records show
The briefing was commissioned by a cloud company [SRC_B]. The peak body cited it [SRC_C].

- The guidelines name the firm by its other work [SRC_D].
- The members include the company [SRC_E].

## Where the data is too thin
Who met whom is not yet public [RG-070].

## What to watch next
The next diary release [SRC_F].

## Our view
A government rulebook should say who paid for the numbers it relies on.
`;

function draft(overrides: Partial<EssayDraft> = {}): EssayDraft {
  return {
    kind: 'essay',
    title: 'Six in seven',
    standfirst: 'How a commissioned number became policy.',
    body: GOOD,
    data_as_of_date: '2026-10-22',
    conflict: null,
    named_parties: [],
    story_cards: ['ST-011'],
    ...overrides,
  };
}

const messages = (d: EssayDraft) => checkEssay(d, ctx).map((i) => `${i.level}: ${i.message}`);

describe('checkEssay', () => {
  it('passes a well-formed essay', () => {
    expect(messages(draft())).toEqual([]);
  });

  it('requires the four record sections and the opinion section, in order', () => {
    const body = GOOD.replace('## Where the data is too thin', '## Gaps');
    expect(messages(draft({ body })).join('\n')).toMatch(/sections must be, in order/);
  });

  it('refuses a record paragraph that cites nothing', () => {
    const body = GOOD.replace('The peak body cited it [SRC_C].', 'The peak body cited it [SRC_C].\n\nEveryone knows this.');
    expect(messages(draft({ body })).join('\n')).toMatch(/What the records show: a paragraph cites nothing/);
  });

  it('accepts an open question in place of a source for what is not known', () => {
    expect(messages(draft()).join('\n')).not.toMatch(/Where the data is too thin/);
  });

  it('refuses a number without a citation, even in the opinion section', () => {
    const body = GOOD.replace('A government rulebook', 'About 40 per cent of rulebooks');
    expect(messages(draft({ body })).join('\n')).toMatch(/Our view: a sentence states a number without a citation/);
  });

  it('does not count ids such as S7 or RG-070 as numbers', () => {
    const body = GOOD.replace('A government rulebook', 'S7 and the RG-070 search show a rulebook');
    expect(hasErrors(checkEssay(draft({ body }), ctx))).toBe(false);
  });

  it('needs at least five distinct sources for an essay', () => {
    const body = GOOD.replace(/\[SRC_[DEF]\]/g, '[SRC_A]');
    expect(messages(draft({ body })).join('\n')).toMatch(/Cites 3 source records\. An essay cites at least 5/);
  });

  it('refuses a source the database does not hold', () => {
    const body = GOOD.replace('[SRC_F]', '[SRC_MISSING]');
    expect(messages(draft({ body })).join('\n')).toMatch(/Cites SRC_MISSING, which the database does not hold/);
  });

  it('needs an opinion section with something in it', () => {
    const body = GOOD.replace(/## Our view[\s\S]*$/, '## Our view\n');
    expect(messages(draft({ body })).join('\n')).toMatch(/"Our view" section is empty/);
  });

  it('requires a conflict disclosure on a piece touching Anthropic', () => {
    const body = GOOD.replace('the company [SRC_E]', 'Anthropic [SRC_E]');
    expect(messages(draft({ body })).join('\n')).toMatch(/touches Anthropic/);
    expect(hasErrors(checkEssay(draft({ body, conflict: 'Drafted with Claude, made by Anthropic.' }), ctx))).toBe(false);
  });

  it('counts story card ST-016 and question RG-012 as touching Anthropic', () => {
    expect(messages(draft({ story_cards: ['ST-016'] })).join('\n')).toMatch(/touches Anthropic/);
  });

  it('refuses a personal name the research holds', () => {
    const body = GOOD.replace('The peak body cited it', 'Jane Example Citizen cited it');
    expect(messages(draft({ body })).join('\n')).toMatch(/Names a person \(Jane Example Citizen\)/);
  });

  it('warns about technical mechanics but does not block on them', () => {
    const body = GOOD.replace('The next diary release [SRC_F].', 'The next diary release, a PDF [SRC_F].');
    const issues = checkEssay(draft({ body }), ctx);
    expect(issues.some((i) => i.level === 'warning' && /file format/.test(i.message))).toBe(true);
    expect(hasErrors(issues)).toBe(false);
  });

  it('needs a data date', () => {
    expect(messages(draft({ data_as_of_date: null })).join('\n')).toMatch(/data as at/);
  });

  it('lets a position piece run on fewer sources, ending in Our view', () => {
    const body = '## What it rests on\nData centres are planned on a large scale [SRC_A].\n\n## Our view\nWe should dream louder.\n';
    expect(messages(draft({ kind: 'position', body }))).toEqual([]);
    expect(messages(draft({ kind: 'position', body: '## Our view\nOnly opinion.\n\n## Coda\nMore.\n' })).join('\n')).toMatch(
      /ends with an "Our view" section/,
    );
  });
});

describe('proposals', () => {
  it('accepts the proposal sections with a straight or curly apostrophe', () => {
    const body = `## Australia's rules now\nOne [SRC_A] [SRC_B].\n\n## Elsewhere\nTwo [SRC_C] [SRC_D].\n\n## What it would take\nThree [SRC_E].\n\n## Our proposal\nDo it.\n`;
    expect(messages(draft({ kind: 'proposal', body }))).toEqual([]);
  });
});

describe('splitAtOpinion and sourcesInOrder', () => {
  it('splits the record from the argument at the opinion heading', () => {
    const { record, opinion, heading } = splitAtOpinion(GOOD);
    expect(heading).toBe('Our view');
    expect(record).toContain('What to watch next');
    expect(record).not.toContain('A government rulebook');
    expect(opinion).toContain('A government rulebook');
  });

  it('numbers sources by first citation', () => {
    expect(sourcesInOrder('x [SRC_B] y [SRC_A] z [SRC_B]')).toEqual(['SRC_B', 'SRC_A']);
  });
});
