import { isRecordId } from '@/lib/ids';
import { editorial, facts, isConfigured } from '@/lib/supabase/server';
import type { CaseStudyRow, EssayRow, PieceKind, SourceRow } from '@/lib/types';

// Pure, so the editor's preview can use it in the browser without this module.
export { youtubeEmbedUrl } from '@/lib/editorial/youtube';

const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;

/**
 * Typed access to the editorial schema.
 *
 * Nothing here filters on approval. RLS refuses to serve an unapproved record
 * to the anon key, so a draft cannot leak through a forgotten `.eq()`. See
 * supabase/migrations/0004_rls.sql.
 */

export async function listEssays(options?: { limit?: number; kind?: PieceKind }): Promise<EssayRow[]> {
  if (!isConfigured()) return [];

  let query = editorial()
    .from('essays')
    .select('*')
    .order('publish_date', { ascending: false });

  if (options?.kind) query = query.eq('kind', options.kind);
  if (options?.limit) query = query.limit(options.limit);

  const { data, error } = await query;
  if (error) throw new Error(`Failed to load essays: ${error.message}`);
  return data ?? [];
}

/** One published piece, by its id or its slug. */
export async function getEssay(idOrSlug: string): Promise<EssayRow | null> {
  if (!isConfigured()) return null;
  const column = isRecordId(idOrSlug) ? 'id' : SLUG.test(idOrSlug) ? 'slug' : null;
  if (!column) return null;

  const { data, error } = await editorial()
    .from('essays')
    .select('*')
    .eq(column, idOrSlug)
    .maybeSingle();

  if (error) throw new Error(`Failed to load essay: ${error.message}`);
  return data ?? null;
}

/** The published "Where we stand" piece, if there is one. The newest wins. */
export async function getPosition(): Promise<EssayRow | null> {
  if (!isConfigured()) return null;

  const { data, error } = await editorial()
    .from('essays')
    .select('*')
    .eq('kind', 'position')
    .order('publish_date', { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) throw new Error(`Failed to load the position: ${error.message}`);
  return data ?? null;
}

/** The source records an essay cites, by their pipeline ids. */
export async function sourcesByPipelineId(ids: readonly string[]): Promise<SourceRow[]> {
  if (!isConfigured() || ids.length === 0) return [];

  const { data, error } = await facts()
    .from('sources')
    .select('*')
    .in('pipeline_id', [...ids]);

  if (error) throw new Error(`Failed to load sources: ${error.message}`);
  return data ?? [];
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
