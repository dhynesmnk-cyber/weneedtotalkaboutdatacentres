import { csvFileName } from '@/lib/csv';
import { DATA_LICENCE, entitiesCsv, researchCsv, sitesCsv, sourcesCsv, type Dataset } from '@/lib/dataExport';
import { lastLoadedAt } from '@/lib/coverage';
import { listEntities } from '@/lib/entities';
import { citedSourcesByRecord, listGaps, listSources } from '@/lib/evidence';
import { listResearchAgenda } from '@/lib/researchAgenda';
import { listSites } from '@/lib/sites';
import { isConfigured } from '@/lib/supabase/server';

/**
 * The data downloads: /data/sites.csv, /data/entities.csv, /data/sources.csv
 * and /data/research.csv (lib/dataExport.ts). Read through the same anon
 * client and Row Level Security as every page, so a download can hold only
 * what the site already publishes.
 */

const FILES: Record<string, Dataset> = {
  'sites.csv': 'sites',
  'entities.csv': 'entities',
  'sources.csv': 'sources',
  'research.csv': 'research',
};

async function build(dataset: Dataset): Promise<string> {
  switch (dataset) {
    case 'sites': {
      const [sites, gaps, cited] = await Promise.all([listSites(), listGaps('sites'), citedSourcesByRecord('sites')]);
      return sitesCsv(sites, gaps, cited);
    }
    case 'entities': {
      const [entities, cited] = await Promise.all([listEntities(), citedSourcesByRecord('entities')]);
      return entitiesCsv(entities, cited);
    }
    case 'sources':
      return sourcesCsv(await listSources());
    case 'research': {
      const questions = await listResearchAgenda();
      const cited = new Map(
        questions.map((q) => [q.id, q.citations.map((c) => c.source?.pipeline_id).filter((s): s is string => !!s)]),
      );
      return researchCsv(questions, cited);
    }
  }
}

export async function GET(_request: Request, { params }: { params: { file: string } }): Promise<Response> {
  const dataset = FILES[params.file];
  if (!dataset) return new Response('Not found', { status: 404 });
  if (!isConfigured()) {
    return new Response('The record is temporarily unavailable.', { status: 503 });
  }

  const [csv, asOf] = await Promise.all([build(dataset), lastLoadedAt()]);
  return new Response(csv, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="${csvFileName(dataset, asOf)}"`,
      'X-Data-As-Of': asOf ?? 'unknown',
      'X-Licence': `${DATA_LICENCE.short} ${DATA_LICENCE.url}`,
      'Cache-Control': 'public, max-age=300',
    },
  });
}
