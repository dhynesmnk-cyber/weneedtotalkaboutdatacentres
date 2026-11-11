import { readdirSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { draftOf, essaysSql, parseEssayFile } from '@/lib/editorial/essayFile';
import { checkEssay, type CheckContext } from '@/lib/editorial/rules';
import { cited } from '@/lib/editorial/text';

const FILE = `---
id: ES-009
slug: a-test
kind: essay
title: A test
standfirst: What it argues, with a comma, and it's fine.
story_cards: [ST-011]
questions: [RG-070]
sources: [SRC_A]
data_as_of: 2026-10-22
named_parties: ["Secretary, Example Department (by role)"]
conflict: null
tags: [one, two]
youtube_id: null
proposal_no: null
status: draft
---

## Our view
Body text [SRC_A].
`;

const parse = (text: string, file = 'editorial/essays/ES-009-a-test.md') => parseEssayFile(file, text);

describe('parseEssayFile', () => {
  it('reads a draft into the row it loads as', () => {
    const { essay, problems } = parse(FILE);
    expect(problems).toEqual([]);
    expect(essay?.row).toMatchObject({
      title: 'A test',
      slug: 'a-test',
      kind: 'essay',
      standfirst: "What it argues, with a comma, and it's fine.",
      tags: ['one', 'two'],
      named_parties: ['Secretary, Example Department (by role)'],
      data_as_of_date: '2026-10-22',
      source_file: 'editorial/essays/ES-009-a-test.md',
    });
    expect(essay?.row.body).toBe('## Our view\nBody text [SRC_A].\n');
  });

  it('derives the same id for the same draft every time', () => {
    expect(parse(FILE).essay?.row.id).toBe(parse(FILE).essay?.row.id);
    expect(parse(FILE).essay?.row.id).toMatch(/^[0-9a-f-]{36}$/);
  });

  it('refuses a draft that claims an approval', () => {
    const { essay, problems } = parse(FILE.replace('status: draft', 'status: draft\napproved_by: an agent'));
    expect(essay).toBeNull();
    expect(problems.join('\n')).toMatch(/'approved_by' is set by the editor/);
  });

  it('refuses any status but draft', () => {
    expect(parse(FILE.replace('status: draft', 'status: approved')).problems.join('\n')).toMatch(/status must be 'draft'/);
  });

  it('needs the file name to match the id and slug', () => {
    expect(parse(FILE, 'editorial/essays/ES-009-other.md').problems.join('\n')).toMatch(/file name must be ES-009-a-test\.md/);
  });

  it('needs a proposal number on a proposal and nowhere else', () => {
    expect(parse(FILE.replace('kind: essay', 'kind: proposal')).problems.join('\n')).toMatch(/needs proposal_no/);
    expect(parse(FILE.replace('proposal_no: null', 'proposal_no: 2')).problems.join('\n')).toMatch(/only a proposal/);
  });
});

describe('essaysSql', () => {
  const { essay } = parse(FILE);
  const sql = essaysSql([essay!], { loaderVersion: 'test', generatedFrom: 'test' });

  it('loads drafts in one transaction', () => {
    expect(sql).toMatch(/^begin;$/m);
    expect(sql).toMatch(/^commit;$/m);
  });

  it('never writes an approval or a publish date', () => {
    const insert = /insert into editorial\.essays \(([^)]*)\)/.exec(sql)?.[1] ?? '';
    expect(insert).not.toMatch(/approved|publish_date/);
  });

  it('leaves a piece alone once the editor has approved or edited it', () => {
    expect(sql).toContain('where editorial.essays.approved_at is null');
    expect(sql).toContain('and editorial.essays.edited_in_admin_at is null');
  });

  it('escapes quotes in the text', () => {
    expect(sql).toContain("it''s fine");
  });

  it('emits text arrays as text arrays', () => {
    expect(sql).toContain("array['one', 'two']::text[]");
  });
});

// The real drafts, checked against the research database they cite, as the
// story cards are in tests/storyCards.test.ts.
describe('editorial/essays', () => {
  const dir = join(__dirname, '..', 'editorial', 'essays');
  const files = readdirSync(dir).filter((f) => /^ES-\d{3}-.*\.md$/.test(f)).sort();

  const { DatabaseSync } = createRequire(import.meta.url)('node:sqlite') as typeof import('node:sqlite');
  const db = new DatabaseSync(
    join(__dirname, '..', 'data-pipeline', 'exports', 'australian_data_centre_observatory.db'),
    { readOnly: true },
  );
  const ctx: CheckContext = {
    sourceIds: new Set((db.prepare('SELECT id FROM sources').all() as { id: string }[]).map((r) => r.id)),
    questionIds: new Set(
      (db.prepare('SELECT id FROM research_gaps').all() as { id: number }[]).map(
        (r) => `RG-${String(r.id).padStart(3, '0')}`,
      ),
    ),
    personalNames: (db.prepare('SELECT person FROM lobbying WHERE person IS NOT NULL').all() as { person: string }[])
      .map((r) => r.person.split(',')[0]!.trim())
      .filter((n) => /^[A-Z][a-z'’-]+(?: [A-Z][a-z'’-]+){1,2}$/.test(n)),
  };
  db.close();

  it.each(files)('%s passes the essay rules', (f) => {
    const { essay, problems } = parseEssayFile(`editorial/essays/${f}`, readFileSync(join(dir, f), 'utf8'));
    expect(problems).toEqual([]);
    const errors = checkEssay(draftOf(essay!), ctx).filter((i) => i.level === 'error');
    expect(errors).toEqual([]);
    expect(new Set(essay!.declaredSources)).toEqual(new Set(cited(essay!.row.body).sources));
  });

  it('the README index lists every draft', () => {
    const readme = readFileSync(join(dir, 'README.md'), 'utf8');
    for (const f of files) expect(readme).toContain(`(${f})`);
  });
});
