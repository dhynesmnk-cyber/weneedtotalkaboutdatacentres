'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { requestOrigin } from '@/lib/origin';
import { siteUrl } from '@/lib/site';
import {
  approvePiece,
  createDraft,
  currentEditor,
  retractPiece,
  saveDraft,
  sendSignInLink,
  signOut,
  type DraftFields,
  type SaveResult,
} from '@/lib/admin';
import { RECORD_CACHE_TAG } from '@/lib/supabase/cachePolicy';
import { PIECE_KINDS, type PieceKind } from '@/lib/types';

/**
 * The editor's actions. Each one checks the editor first, then asks the
 * database, which checks again: these functions are a convenience, row level
 * security and the approval function are the rule.
 */

async function requireEditor() {
  const editor = await currentEditor();
  if (!editor) redirect('/admin/sign-in');
  return editor;
}

const text = (form: FormData, key: string) => String(form.get(key) ?? '');
const optional = (form: FormData, key: string) => {
  const v = text(form, key).trim();
  return v === '' ? null : v;
};

export type SignInState = { sent: boolean; message?: string };

export async function signInAction(_prev: SignInState, form: FormData): Promise<SignInState> {
  const email = text(form, 'email').trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { sent: false, message: 'That does not look like an email address.' };
  }
  await sendSignInLink(email, requestOrigin(headers(), siteUrl().origin));
  // The same reply whatever happened, so the page cannot be used to learn who
  // may edit.
  return { sent: true };
}

export async function signOutAction() {
  await signOut();
  redirect('/admin/sign-in');
}

export async function createDraftAction(form: FormData) {
  await requireEditor();
  const title = text(form, 'title').trim() || 'Untitled draft';
  const kind = text(form, 'kind') as PieceKind;
  const id = await createDraft(title, PIECE_KINDS.includes(kind) ? kind : 'essay');
  redirect(`/admin/essays/${id}`);
}

function draftFields(form: FormData): DraftFields {
  return {
    title: text(form, 'title').trim(),
    slug: optional(form, 'slug'),
    standfirst: optional(form, 'standfirst'),
    body: text(form, 'body').replace(/\r\n/g, '\n'),
    tags: text(form, 'tags')
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean),
    youtube_id: optional(form, 'youtube_id'),
    data_as_of_date: optional(form, 'data_as_of_date'),
    conflict: optional(form, 'conflict'),
    named_parties: text(form, 'named_parties')
      .split('\n')
      .map((p) => p.trim())
      .filter(Boolean),
  };
}

export async function saveAction(_prev: SaveResult | null, form: FormData): Promise<SaveResult> {
  await requireEditor();
  const id = text(form, 'id');
  const result = await saveDraft(id, draftFields(form), text(form, 'expected_updated_at'));
  if (result.ok) revalidatePath(`/admin/essays/${id}`);
  return result;
}

export type ApprovalState = { message?: string };

export async function approveAction(_prev: ApprovalState, form: FormData): Promise<ApprovalState> {
  await requireEditor();
  const id = text(form, 'id');
  if (form.get('read') !== 'on') {
    return { message: 'Confirm that you have read the piece and checked the sources it leans on.' };
  }
  const result = await approvePiece({
    id,
    publishDate: text(form, 'publish_date'),
    expectedUpdatedAt: text(form, 'expected_updated_at'),
    legalAck: form.get('legal_ack') === 'on',
  });
  if (!result.ok) return { message: result.message };
  // The public pages cache records for minutes; publication shows at once.
  revalidateTag(RECORD_CACHE_TAG);
  redirect(`/admin?approved=${id}`);
}

export async function retractAction(_prev: ApprovalState, form: FormData): Promise<ApprovalState> {
  await requireEditor();
  const id = text(form, 'id');
  const result = await retractPiece(id, text(form, 'reason'));
  if (!result.ok) return { message: result.message };
  revalidateTag(RECORD_CACHE_TAG);
  redirect(`/admin/essays/${id}?retracted=1`);
}
