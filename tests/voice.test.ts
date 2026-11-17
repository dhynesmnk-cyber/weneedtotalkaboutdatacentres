import { describe, expect, it } from 'vitest';
import { checkEssay, type CheckContext, type EssayDraft } from '@/lib/editorial/rules';
import { ownVoice, voiceProblems } from '@/lib/editorial/text';

// The house voice (editorial/WRITING.md, section 9).
describe('voiceProblems', () => {
  it('passes plain prose', () => {
    expect(voiceProblems('The consent was signed in July. Nobody has said why.')).toEqual([]);
  });

  it('catches an em dash and an exclamation mark', () => {
    expect(voiceProblems('The approval came late — very late.')).toEqual(['an em dash']);
    expect(voiceProblems('It was approved anyway! Nobody said why.')).toEqual(['an exclamation mark']);
  });

  it('catches banned words in our own voice', () => {
    expect(voiceProblems('This deal could unlock the region.')).toEqual(['"unlock"']);
    expect(voiceProblems('The policy landscape is shifting.')).toEqual(['"landscape"']);
    expect(voiceProblems('A robust regime, they say.')).toEqual(['"robust"']);
    expect(voiceProblems('It will transform western Sydney.')).toEqual(['"transform"']);
    expect(voiceProblems('An AI-powered future.')).toEqual(['"AI-powered"']);
  });

  it('catches an "imagine" opening', () => {
    expect(voiceProblems('Imagine a campus the size of a suburb.')).toEqual([
      'an "imagine" or "picture this" opening',
    ]);
  });

  it('lets their language through when it is quoted', () => {
    expect(voiceProblems('The release promises to "transform western Sydney" [SRC_A].')).toEqual([]);
    expect(voiceProblems('Its page calls it “a seamless, world-class campus” [SRC_A].')).toEqual([]);
    expect(voiceProblems('> "Make no mistake, this will unlock jobs."\n\nThe minister said so [SRC_A].')).toEqual([]);
  });

  it('lets a proper noun through', () => {
    // ST-001 names the Digital Transformation Agency.
    expect(voiceProblems('The scheme was once run by the Digital Transformation Agency [SRC_A].')).toEqual([]);
  });

  it('does not mistake callouts or images for exclamation marks', () => {
    expect(voiceProblems('> [!FIGURE] 6 in 7\n> Phantom demand [SRC_A]\n\n![Map](map.png)')).toEqual([]);
  });

  it('drops citations, block quotes and quoted passages from our own voice', () => {
    expect(ownVoice('We read it [SRC_A] and "they said this".\n> A pull quote.')).toBe('We read it  and "".');
  });
});

describe('checkEssay and the house voice', () => {
  const ctx: CheckContext = {
    sourceIds: new Set(['SRC_A', 'SRC_B', 'SRC_C', 'SRC_D', 'SRC_E']),
    questionIds: new Set(['RG-070']),
  };
  const body = `## The common perception
The guidelines say six in seven requests are phantom [SRC_A].

## What the records show
The briefing was commissioned by a cloud company [SRC_B]. The peak body cited it [SRC_C] [SRC_D] [SRC_E].

## Where the data is too thin
Who met whom is not yet public [RG-070].

## What to watch next
The next diary release [RG-070].

## Our view
A rulebook should say who paid for its numbers.
`;
  const draft = (overrides: Partial<EssayDraft>): EssayDraft => ({
    kind: 'essay',
    title: 'Six in seven',
    standfirst: 'How a commissioned number became policy.',
    body,
    data_as_of_date: '2026-11-17',
    conflict: null,
    named_parties: [],
    story_cards: [],
    ...overrides,
  });
  const errors = (d: EssayDraft) =>
    checkEssay(d, ctx)
      .filter((i) => i.level === 'error')
      .map((i) => i.message);

  it('passes the clean draft', () => {
    expect(errors(draft({}))).toEqual([]);
  });

  it('refuses a banned word in the opinion', () => {
    const bad = body.replace('who paid for its numbers.', 'who paid for its numbers. Make no mistake.');
    expect(errors(draft({ body: bad })).join('\n')).toMatch(/"make no mistake"/);
  });

  it('checks the title and standfirst too', () => {
    expect(errors(draft({ title: 'The phantom landscape' })).join('\n')).toMatch(/"landscape"/);
    expect(errors(draft({ standfirst: 'A number — and who paid.' })).join('\n')).toMatch(/an em dash/);
  });
});
