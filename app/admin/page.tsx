import Link from 'next/link';
import { redirect } from 'next/navigation';
import { createDraftAction, signOutAction } from '@/app/admin/actions';
import { currentEditor, listPieces } from '@/lib/admin';
import { formatDate } from '@/lib/format';
import type { EssayRow } from '@/lib/types';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Pieces' };

const KIND: Record<EssayRow['kind'], string> = {
  essay: 'Essay',
  position: 'Where we stand',
  proposal: 'What if…?',
};

function stage(piece: EssayRow, today: string): 'draft' | 'scheduled' | 'published' {
  if (!piece.approved_at) return 'draft';
  return piece.publish_date && piece.publish_date > today ? 'scheduled' : 'published';
}

function origin(piece: EssayRow): string {
  if (piece.edited_in_admin_at) return `edited here by ${piece.last_edited_by ?? 'the editor'}`;
  if (piece.source_file) return `agent draft from ${piece.source_file}`;
  return 'created here';
}

export default async function AdminPage({ searchParams }: { searchParams: { approved?: string } }) {
  const editor = await currentEditor();
  if (!editor) redirect('/admin/sign-in');

  const pieces = await listPieces();
  const today = new Date().toISOString().slice(0, 10);
  const groups = (['draft', 'scheduled', 'published'] as const).map((s) => ({
    stage: s,
    pieces: pieces.filter((p) => stage(p, today) === s),
  }));
  const approved = searchParams.approved ? pieces.find((p) => p.id === searchParams.approved) : undefined;

  return (
    <div className="space-y-10">
      <div className="flex flex-wrap items-baseline justify-between gap-4">
        <div>
          <h1 className="page-title">Pieces</h1>
          <p className="mt-1 text-sm text-slate-600">Signed in as {editor.email}</p>
        </div>
        <form action={signOutAction}>
          <button type="submit" className="min-h-11 rounded border border-slate-500 px-3 text-sm">
            Sign out
          </button>
        </form>
      </div>

      {approved && (
        <p role="status" className="rounded border border-fact-edge bg-fact-wash p-3 text-sm text-fact-ink">
          Approved: &ldquo;{approved.title}&rdquo;, publishing {formatDate(approved.publish_date)}.
        </p>
      )}

      {groups.map(({ stage: s, pieces: list }) => (
        <section key={s} aria-labelledby={`${s}-heading`}>
          <h2 id={`${s}-heading`} className="section-heading capitalize">
            {s} <span className="font-normal text-slate-600">({list.length})</span>
          </h2>
          {list.length === 0 ? (
            <p className="mt-2 text-sm text-slate-600">None.</p>
          ) : (
            <ul className="mt-3 divide-y divide-slate-200 border-y border-slate-200">
              {list.map((piece) => (
                <li key={piece.id} className="py-3">
                  <Link href={`/admin/essays/${piece.id}`} className="link font-medium">
                    {piece.title}
                  </Link>
                  <p className="mt-1 text-sm text-slate-600">
                    {KIND[piece.kind]} · {origin(piece)} · changed {formatDate(piece.updated_at.slice(0, 10))}
                    {piece.publish_date && s !== 'draft' && <> · publishes {formatDate(piece.publish_date)}</>}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>
      ))}

      <section aria-labelledby="new-heading" className="rounded-lg border border-slate-200 p-4">
        <h2 id="new-heading" className="section-heading">
          Start a draft
        </h2>
        <form action={createDraftAction} className="mt-3 flex flex-wrap items-end gap-3">
          <label className="text-sm">
            <span className="block font-medium text-slate-900">Title</span>
            <input name="title" required className="mt-1 w-72 rounded border border-slate-500 bg-white px-2 py-1.5" />
          </label>
          <label className="text-sm">
            <span className="block font-medium text-slate-900">Kind</span>
            <select name="kind" className="mt-1 rounded border border-slate-500 bg-white px-2 py-1.5">
              <option value="essay">Essay</option>
              <option value="position">Where we stand</option>
              <option value="proposal">What if…? proposal</option>
            </select>
          </label>
          <button type="submit" className="min-h-11 rounded bg-fact-ink px-4 text-sm font-medium text-white">
            Create draft
          </button>
        </form>
      </section>
    </div>
  );
}
