'use client';

import { useEffect, useMemo, useState } from 'react';
import { useFormState, useFormStatus } from 'react-dom';
import {
  approveAction,
  retractAction,
  saveAction,
  type ApprovalState,
} from '@/app/admin/actions';
import { EssayArticle } from '@/components/essay/EssayArticle';
import { checkEssay, hasErrors } from '@/lib/editorial/rules';
import type { SaveResult } from '@/lib/admin';
import type { EssayRow, SourceRow } from '@/lib/types';

type Fields = {
  title: string;
  slug: string;
  standfirst: string;
  body: string;
  tags: string;
  youtube_id: string;
  data_as_of_date: string;
  conflict: string;
  named_parties: string;
};

function fieldsOf(piece: EssayRow): Fields {
  return {
    title: piece.title,
    slug: piece.slug ?? '',
    standfirst: piece.standfirst ?? '',
    body: piece.body ?? '',
    tags: piece.tags.join(', '),
    youtube_id: piece.youtube_id ?? '',
    data_as_of_date: piece.data_as_of_date ?? '',
    conflict: piece.conflict ?? '',
    named_parties: piece.named_parties.join('\n'),
  };
}

const lines = (s: string) => s.split('\n').map((x) => x.trim()).filter(Boolean);

function Button({ children, disabled, tone = 'fact' }: { children: React.ReactNode; disabled?: boolean; tone?: 'fact' | 'editorial' | 'plain' }) {
  const { pending } = useFormStatus();
  const style =
    tone === 'fact'
      ? 'bg-fact-ink text-white'
      : tone === 'editorial'
        ? 'bg-editorial-ink text-white'
        : 'border border-slate-500 text-slate-900';
  return (
    <button
      type="submit"
      disabled={disabled || pending}
      className={`min-h-11 rounded px-4 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50 ${style}`}
    >
      {pending ? 'Working…' : children}
    </button>
  );
}

const input = 'mt-1 block w-full rounded border border-slate-500 bg-white px-2 py-1.5 text-slate-900';

/**
 * The editor: the text on the left, the page as readers will see it on the
 * right, and the checker underneath. Approval needs saved text, a clean
 * check, and the editor's word that they have read it. The database then
 * checks again, and records who approved which text.
 */
export function EssayEditor({
  piece,
  sources,
  questionIds,
  today,
}: {
  piece: EssayRow;
  sources: SourceRow[];
  questionIds: string[];
  today: string;
}) {
  const published = piece.approved_at !== null;
  const [fields, setFields] = useState<Fields>(() => fieldsOf(piece));
  const [saved, setSaved] = useState<Fields>(() => fieldsOf(piece));
  const [updatedAt, setUpdatedAt] = useState(piece.updated_at);
  const [view, setView] = useState<'edit' | 'preview'>('edit');

  const [saveState, save] = useFormState<SaveResult | null, FormData>(saveAction, null);
  const [approveState, approve] = useFormState<ApprovalState, FormData>(approveAction, {});
  const [retractState, retract] = useFormState<ApprovalState, FormData>(retractAction, {});

  useEffect(() => {
    if (saveState?.ok) {
      setUpdatedAt(saveState.updatedAt);
      setSaved(fields);
    }
    // Only when a save comes back; `fields` is read at that moment on purpose.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [saveState]);

  const dirty = JSON.stringify(fields) !== JSON.stringify(saved);

  useEffect(() => {
    if (!dirty) return;
    const warn = (e: BeforeUnloadEvent) => e.preventDefault();
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [dirty]);

  const ctx = useMemo(
    () => ({
      sourceIds: new Set(sources.map((s) => s.pipeline_id!).filter(Boolean)),
      questionIds: new Set(questionIds),
    }),
    [sources, questionIds],
  );

  const issues = useMemo(
    () =>
      checkEssay(
        {
          kind: piece.kind,
          title: fields.title,
          standfirst: fields.standfirst,
          body: fields.body,
          data_as_of_date: fields.data_as_of_date || null,
          conflict: fields.conflict || null,
          named_parties: lines(fields.named_parties),
          story_cards: piece.story_cards,
        },
        ctx,
      ),
    [fields, piece.kind, piece.story_cards, ctx],
  );
  const blocked = hasErrors(issues);
  const namesPeople = lines(fields.named_parties).length > 0;

  const set = (key: keyof Fields) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setFields((f) => ({ ...f, [key]: e.target.value }));

  const preview = (
    <EssayArticle
      piece={{
        title: fields.title,
        standfirst: fields.standfirst || null,
        kind: piece.kind,
        body: fields.body,
        publish_date: piece.publish_date,
        data_as_of_date: fields.data_as_of_date || null,
        conflict: fields.conflict || null,
        youtube_id: fields.youtube_id || null,
        proposal_no: piece.proposal_no,
      }}
      sources={sources}
      compact
    />
  );

  if (published) {
    return (
      <div className="space-y-8">
        <p className="rounded border border-fact-edge bg-fact-wash p-3 text-sm text-fact-ink">
          Approved by {piece.approved_by} and publishing {piece.publish_date}. A published piece
          cannot be edited in place: retract it, edit the draft, and approve it again.
        </p>
        <form action={retract} className="space-y-3 rounded-lg border border-slate-200 p-4">
          <input type="hidden" name="id" value={piece.id} />
          <label className="block text-sm">
            <span className="font-medium text-slate-900">Why is it being retracted? This is kept with the record.</span>
            <textarea name="reason" required rows={2} className={input} />
          </label>
          {retractState.message && <p role="alert" className="text-sm text-defect-ink">{retractState.message}</p>}
          <Button tone="plain">Retract to draft</Button>
        </form>
        <div className="rounded-lg border border-slate-200 p-4 md:p-8">{preview}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-2 xl:hidden" role="group" aria-label="Show">
        {(['edit', 'preview'] as const).map((v) => (
          <button
            key={v}
            type="button"
            aria-pressed={view === v}
            onClick={() => setView(v)}
            className={`min-h-11 rounded border px-3 text-sm capitalize ${view === v ? 'border-slate-900 font-semibold' : 'border-slate-300'}`}
          >
            {v}
          </button>
        ))}
      </div>

      <div className="grid gap-8 xl:grid-cols-2">
        <form action={save} className={`space-y-4 ${view === 'edit' ? '' : 'hidden xl:block'}`}>
          <input type="hidden" name="id" value={piece.id} />
          <input type="hidden" name="expected_updated_at" value={updatedAt} />

          <label className="block text-sm">
            <span className="font-medium text-slate-900">Title</span>
            <input name="title" value={fields.title} onChange={set('title')} required className={input} />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-900">Standfirst</span>
            <textarea name="standfirst" value={fields.standfirst} onChange={set('standfirst')} rows={2} className={input} />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm">
              <span className="font-medium text-slate-900">Data as at</span>
              <input name="data_as_of_date" type="date" value={fields.data_as_of_date} onChange={set('data_as_of_date')} className={input} />
            </label>
            <label className="block text-sm">
              <span className="font-medium text-slate-900">Web address (slug)</span>
              <input name="slug" value={fields.slug} onChange={set('slug')} pattern="[a-z0-9]+(-[a-z0-9]+)*" className={input} />
            </label>
            <label className="block text-sm">
              <span className="font-medium text-slate-900">YouTube video id</span>
              <input name="youtube_id" value={fields.youtube_id} onChange={set('youtube_id')} pattern="[A-Za-z0-9_\-]{11}" className={input} />
            </label>
            <label className="block text-sm">
              <span className="font-medium text-slate-900">Tags, comma separated</span>
              <input name="tags" value={fields.tags} onChange={set('tags')} className={input} />
            </label>
          </div>
          <label className="block text-sm">
            <span className="font-medium text-slate-900">Conflict of interest disclosure</span>
            <textarea name="conflict" value={fields.conflict} onChange={set('conflict')} rows={2} className={input} />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-900">People named, by role, one per line</span>
            <textarea name="named_parties" value={fields.named_parties} onChange={set('named_parties')} rows={2} className={input} />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-900">Text</span>
            <span className="block text-slate-600">
              Markdown. Cite a source as [SRC_ID] and an open question as [RG-070]. Opinion goes under
              &ldquo;## Our view&rdquo;, below the divider.
            </span>
            <textarea
              name="body"
              value={fields.body}
              onChange={set('body')}
              rows={32}
              spellCheck
              lang="en-AU"
              className={`${input} font-mono text-sm leading-relaxed`}
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <Button disabled={!dirty}>Save draft</Button>
            <span aria-live="polite" className="text-sm text-slate-600">
              {dirty ? 'Unsaved changes' : saveState?.ok ? 'Saved' : 'No changes'}
            </span>
          </div>
          {saveState && !saveState.ok && (
            <p role="alert" className="rounded border border-defect-edge bg-defect-wash p-3 text-sm text-defect-ink">
              {saveState.message}
            </p>
          )}
        </form>

        <div className={`${view === 'preview' ? '' : 'hidden xl:block'}`}>
          <p className="kicker text-slate-600">Preview: as readers will see it</p>
          <div className="mt-3 max-h-[80vh] overflow-y-auto rounded-lg border border-slate-200 p-4 md:p-6">{preview}</div>
        </div>
      </div>

      <section aria-labelledby="check-heading" className="rounded-lg border border-slate-200 p-4">
        <h2 id="check-heading" className="section-heading">
          Checks {blocked ? <span className="text-defect-ink">: not ready</span> : <span className="text-fact-ink">: ready</span>}
        </h2>
        {issues.length === 0 ? (
          <p className="mt-2 text-sm text-slate-700">Every check passes. The legal check and your reading are still yours to do.</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {issues.map((i, n) => (
              <li key={n} className={i.level === 'error' ? 'text-defect-ink' : 'text-slate-700'}>
                <strong className="font-semibold">{i.level === 'error' ? 'Fix' : 'Note'}:</strong> {i.message}
              </li>
            ))}
          </ul>
        )}
      </section>

      <form action={approve} className="space-y-3 rounded-lg border border-editorial-edge bg-editorial-wash/40 p-4">
        <h2 className="section-heading">Approve for publication</h2>
        <input type="hidden" name="id" value={piece.id} />
        <input type="hidden" name="expected_updated_at" value={updatedAt} />
        <label className="block text-sm">
          <span className="font-medium text-slate-900">Publish on</span>
          <input name="publish_date" type="date" defaultValue={today} required className={`${input} w-48`} />
        </label>
        <label className="flex items-start gap-2 text-sm text-slate-900">
          <input type="checkbox" name="read" className="mt-1 h-4 w-4" required />
          I have read this piece in full, as it appears in the preview, and checked the sources it leans on.
        </label>
        {namesPeople && (
          <label className="flex items-start gap-2 text-sm text-slate-900">
            <input type="checkbox" name="legal_ack" className="mt-1 h-4 w-4" required />
            It names people. The legal and defamation check in docs/REVIEW.md has been done.
          </label>
        )}
        {approveState.message && <p role="alert" className="text-sm text-defect-ink">{approveState.message}</p>}
        <div className="flex flex-wrap items-center gap-3">
          <Button tone="editorial" disabled={dirty || blocked}>
            Approve
          </Button>
          <span className="text-sm text-slate-700">
            {dirty ? 'Save your changes first.' : blocked ? 'Fix the checks above first.' : 'Approval is recorded under your name.'}
          </span>
        </div>
      </form>
    </div>
  );
}
