/**
 * Typed access for the editor's pages at /admin.
 *
 * Everything here runs as the signed-in editor, through row level security.
 * The database decides what the editor may see and change (migrations 0014 to
 * 0017); these functions only shape the calls. Nothing here can approve a
 * piece except approvePiece(), which calls the database's own approval
 * function and passes it no approver: the database takes that from the
 * session.
 */

import { editorClient, isAuthConfigured } from '@/lib/supabase/editor';
import { siteUrl } from '@/lib/site';
import type {
  ApprovalRow,
  EssayRevisionRow,
  EssayRow,
  PieceKind,
  SourceRow,
} from '@/lib/types';

export { isAuthConfigured };

/** The signed-in editor, or null if nobody is signed in or they may not edit. */
export async function currentEditor(): Promise<{ email: string } | null> {
  if (!isAuthConfigured()) return null;
  const supabase = editorClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user?.email) return null;
  const { data: allowed, error } = await supabase.rpc('is_editor');
  if (error || allowed !== true) return null;
  return { email: data.user.email };
}

/**
 * Send a one-time sign-in link back to the host the editor asked from, so a
 * deploy preview signs in on the preview. Says nothing about whether the
 * address may edit.
 */
export async function sendSignInLink(email: string, origin: string = siteUrl().origin): Promise<void> {
  if (!isAuthConfigured()) return;
  await editorClient().auth.signInWithOtp({
    email,
    options: {
      // Only an existing user can sign in: nobody can create an account here.
      shouldCreateUser: false,
      emailRedirectTo: new URL('/admin/auth/callback', origin).toString(),
    },
  });
}

/** Complete a sign-in from the emailed link. */
export async function completeSignIn(code: string): Promise<boolean> {
  const { error } = await editorClient().auth.exchangeCodeForSession(code);
  return !error;
}

export async function signOut(): Promise<void> {
  await editorClient().auth.signOut();
}

/** Every piece, drafts included, newest change first. */
export async function listPieces(): Promise<EssayRow[]> {
  const { data, error } = await editorClient()
    .from('essays')
    .select('*')
    .order('updated_at', { ascending: false });
  if (error) throw new Error(`Failed to load pieces: ${error.message}`);
  return data ?? [];
}

export async function getPiece(id: string): Promise<EssayRow | null> {
  const { data, error } = await editorClient().from('essays').select('*').eq('id', id).maybeSingle();
  if (error) throw new Error(`Failed to load the piece: ${error.message}`);
  return data ?? null;
}

export async function listRevisions(id: string): Promise<EssayRevisionRow[]> {
  const { data, error } = await editorClient()
    .from('essay_revisions')
    .select('*')
    .eq('essay_id', id)
    .order('saved_at', { ascending: false })
    .limit(20);
  if (error) throw new Error(`Failed to load revisions: ${error.message}`);
  return data ?? [];
}

export async function listApprovals(id: string): Promise<ApprovalRow[]> {
  const { data, error } = await editorClient()
    .from('approvals')
    .select('*')
    .eq('record_type', 'essays')
    .eq('record_id', id)
    .order('at', { ascending: false });
  if (error) throw new Error(`Failed to load the approval history: ${error.message}`);
  return data ?? [];
}

/** Every source the record holds, for the preview's citations and the checker. */
export async function allSources(): Promise<SourceRow[]> {
  const out: SourceRow[] = [];
  const facts = editorClient().schema('facts');
  // PostgREST caps a page at the project's max rows; read until a short page.
  for (let from = 0; ; from += 1000) {
    const { data, error } = await facts
      .from('sources')
      .select('*')
      .not('pipeline_id', 'is', null)
      .order('pipeline_id')
      .range(from, from + 999);
    if (error) throw new Error(`Failed to load sources: ${error.message}`);
    out.push(...((data ?? []) as SourceRow[]));
    if (!data || data.length < 1000) break;
  }
  return out;
}

/** The research question ids the agenda holds, as RG-nnn. */
export async function questionIds(): Promise<string[]> {
  const { data, error } = await editorClient()
    .schema('facts')
    .from('research_agenda')
    .select('pipeline_id')
    .not('pipeline_id', 'is', null);
  if (error) throw new Error(`Failed to load research questions: ${error.message}`);
  return ((data ?? []) as { pipeline_id: string }[]).map((r) => r.pipeline_id);
}

export type DraftFields = Pick<
  EssayRow,
  | 'title'
  | 'slug'
  | 'standfirst'
  | 'body'
  | 'tags'
  | 'youtube_id'
  | 'data_as_of_date'
  | 'conflict'
  | 'named_parties'
>;

export type SaveResult =
  | { ok: true; updatedAt: string }
  | { ok: false; reason: 'conflict' | 'error'; message: string };

/**
 * Save a draft, but only if nobody changed it since the editor loaded it. A
 * save that would overwrite someone else's change is refused, never merged.
 */
export async function saveDraft(id: string, fields: DraftFields, expectedUpdatedAt: string): Promise<SaveResult> {
  const { data, error } = await editorClient()
    .from('essays')
    .update(fields)
    .eq('id', id)
    .eq('updated_at', expectedUpdatedAt)
    .select('updated_at')
    .maybeSingle();

  if (error) return { ok: false, reason: 'error', message: error.message };
  if (!data) {
    return {
      ok: false,
      reason: 'conflict',
      message:
        'This piece changed after you opened it, or it has been approved. Nothing was saved. Copy your text, reload, and apply it again.',
    };
  }
  return { ok: true, updatedAt: data.updated_at };
}

export async function createDraft(title: string, kind: PieceKind): Promise<string> {
  const { data, error } = await editorClient()
    .from('essays')
    .insert({ title, kind, body: '', ...(kind === 'proposal' ? { proposal_no: 1 } : {}) })
    .select('id')
    .single();
  if (error) throw new Error(`Failed to create the draft: ${error.message}`);
  return data.id;
}

export type ActionResult = { ok: true } | { ok: false; message: string };

/** Approve a piece for publication. The database records who, from the session. */
export async function approvePiece(input: {
  id: string;
  publishDate: string;
  expectedUpdatedAt: string;
  legalAck: boolean;
}): Promise<ActionResult> {
  const { error } = await editorClient().rpc('approve_essay', {
    p_id: input.id,
    p_publish_date: input.publishDate,
    p_expected_updated_at: input.expectedUpdatedAt,
    p_legal_ack: input.legalAck,
  });
  return error ? { ok: false, message: error.message } : { ok: true };
}

export async function retractPiece(id: string, reason: string): Promise<ActionResult> {
  const { error } = await editorClient().rpc('retract_essay', { p_id: id, p_reason: reason });
  return error ? { ok: false, message: error.message } : { ok: true };
}
