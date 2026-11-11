import Link from 'next/link';
import { notFound, redirect } from 'next/navigation';
import { EssayEditor } from '@/components/admin/EssayEditor';
import {
  allSources,
  currentEditor,
  getPiece,
  listApprovals,
  listRevisions,
  questionIds,
} from '@/lib/admin';
import { isRecordId } from '@/lib/ids';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Edit' };

export default async function EditPiecePage({
  params,
  searchParams,
}: {
  params: { id: string };
  searchParams: { retracted?: string };
}) {
  const editor = await currentEditor();
  if (!editor) redirect('/admin/sign-in');
  if (!isRecordId(params.id)) notFound();

  const piece = await getPiece(params.id);
  if (!piece) notFound();

  const [sources, questions, revisions, approvals] = await Promise.all([
    allSources(),
    questionIds(),
    listRevisions(piece.id),
    listApprovals(piece.id),
  ]);

  // The editor's calendar day in Australia, not the server's in UTC.
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'Australia/Sydney' }).format(new Date());

  return (
    <div className="space-y-8">
      <p className="text-sm">
        <Link href="/admin" className="link">
          All pieces
        </Link>
      </p>
      {searchParams.retracted && (
        <p role="status" className="rounded border border-slate-300 p-3 text-sm text-slate-800">
          Retracted. The piece is a draft again and no longer public.
        </p>
      )}

      <EssayEditor piece={piece} sources={sources} questionIds={questions} today={today} />

      <details className="rounded-lg border border-slate-200 p-4">
        <summary className="cursor-pointer font-medium text-slate-900">
          History ({revisions.length} earlier version{revisions.length === 1 ? '' : 's'}, {approvals.length} approval event{approvals.length === 1 ? '' : 's'})
        </summary>
        <div className="mt-4 grid gap-6 md:grid-cols-2">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-700">Approvals</h2>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {approvals.length === 0 && <li>None yet.</li>}
              {approvals.map((a) => (
                <li key={a.id}>
                  {a.at.slice(0, 16).replace('T', ' ')}: {a.action === 'approve' ? 'approved' : 'retracted'} by {a.actor_email}
                  {a.reason && <> (&ldquo;{a.reason}&rdquo;)</>}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-700">Earlier versions</h2>
            <ul className="mt-2 space-y-3 text-sm text-slate-700">
              {revisions.length === 0 && <li>None yet. The first save keeps the agent&rsquo;s draft here.</li>}
              {revisions.map((r) => (
                <li key={r.id}>
                  <details>
                    <summary className="cursor-pointer">
                      {r.edited_at.slice(0, 16).replace('T', ' ')} by {r.edited_by ?? 'the loader'}
                    </summary>
                    <pre className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap rounded bg-slate-50 p-3 font-mono text-xs">
                      {r.body}
                    </pre>
                  </details>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </details>
    </div>
  );
}
