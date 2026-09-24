import { isRecordId } from '@/lib/ids';
import { editorial, isConfigured } from '@/lib/supabase/server';
import type { CaseStudyRow, EssayRow } from '@/lib/types';

/**
 * Typed access to the editorial schema.
 *
 * Nothing here filters on approval. RLS refuses to serve an unapproved record
 * to the anon key, so a draft cannot leak through a forgotten `.eq()`. See
 * supabase/migrations/0004_rls.sql.
 */

export async function listEssays(options?: { limit?: number }): Promise<EssayRow[]> {
  if (!isConfigured()) return [];

  let query = editorial()
    .from('essays')
    .select('*')
    .order('publish_date', { ascending: false });

  if (options?.limit) query = query.limit(options.limit);

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load essays: ${error.message}`);
  return data ?? [];
}

export async function getEssay(id: string): Promise<EssayRow | null> {
  if (!isConfigured()) return null;
  if (!isRecordId(id)) return null;

  const { data, error } = await editorial()
    .from('essays')
    .select('*')
    .eq('id', id)
    .maybeSingle();

  if (error) throw new Error(`Failed to load essay: ${error.message}`);
  return data ?? null;
}

export async function listCaseStudies(options?: {
  siteId?: string;
}): Promise<CaseStudyRow[]> {
  if (!isConfigured()) return [];

  let query = editorial()
    .from('case_studies')
    .select('*')
    .order('publish_date', { ascending: false });

  if (options?.siteId) query = query.eq('site_id', options.siteId);

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load case studies: ${error.message}`);
  return data ?? [];
}

export async function getCaseStudy(id: string): Promise<CaseStudyRow | null> {
  if (!isConfigured()) return null;
  if (!isRecordId(id)) return null;

  const { data, error } = await editorial()
    .from('case_studies')
    .select('*')
    .eq('id', id)
    .maybeSingle();

  if (error) throw new Error(`Failed to load case study: ${error.message}`);
  return data ?? null;
}

/**
 * Extract a YouTube embed URL from a stored video id.
 *
 * Accepts an id only, not a full URL, so that a pasted tracking-laden link
 * cannot end up in an iframe src. Returns null for anything that is not a
 * plausible id.
 */
export function youtubeEmbedUrl(youtubeId: string | null): string | null {
  if (!youtubeId) return null;
  if (!/^[A-Za-z0-9_-]{11}$/.test(youtubeId)) return null;
  return `https://www.youtube-nocookie.com/embed/${youtubeId}`;
}
