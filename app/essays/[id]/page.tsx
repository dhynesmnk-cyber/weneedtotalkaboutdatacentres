import { cache } from 'react';
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getEssay, sourcesByPipelineId } from '@/lib/editorial';
import { sourcesInOrder } from '@/lib/editorial/rules';
import { pageCitation } from '@/lib/cite';
import { isConfigured } from '@/lib/supabase/server';
import { EssayArticle } from '@/components/essay/EssayArticle';
import { CiteThisPage } from '@/components/CiteThisPage';
import { NotConnected } from '@/components/NotConnected';

export const dynamic = 'force-dynamic';

// One fetch per request, shared by the page and its metadata.
const loadEssay = cache(getEssay);

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  if (!isConfigured()) return {};
  const essay = await loadEssay(params.id);
  if (!essay) return {};
  const path = `/essays/${essay.slug ?? essay.id}`;
  return {
    title: essay.title,
    description: essay.standfirst ?? undefined,
    alternates: { canonical: path },
    openGraph: {
      type: 'article',
      title: essay.title,
      description: essay.standfirst ?? undefined,
      publishedTime: essay.publish_date ?? undefined,
    },
  };
}

/**
 * An essay: the record it rests on, the divider, the argument, and every
 * source it cites, numbered in the order the text meets them.
 *
 * Reachable by id or by slug. Drafts are invisible here by construction: row
 * level security serves the anon key approved, dated pieces only.
 */
export default async function EssayPage({ params }: { params: { id: string } }) {
  if (!isConfigured()) {
    return <NotConnected what="essays" />;
  }

  const essay = await loadEssay(params.id);
  if (!essay) notFound();

  const sources = await sourcesByPipelineId(sourcesInOrder(essay.body ?? ''));
  const path = `/essays/${essay.slug ?? essay.id}`;

  return (
    <EssayArticle
      piece={essay}
      sources={sources}
      footer={
        <CiteThisPage
          citation={pageCitation({
            title: essay.title,
            path,
            publishDate: essay.publish_date,
            dataAsOfDate: essay.data_as_of_date,
          })}
        />
      }
    />
  );
}
