import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getPosition, sourcesByPipelineId } from '@/lib/editorial';
import { sourcesInOrder } from '@/lib/editorial/rules';
import { pageCitation } from '@/lib/cite';
import { isConfigured } from '@/lib/supabase/server';
import { EssayArticle } from '@/components/essay/EssayArticle';
import { CiteThisPage } from '@/components/CiteThisPage';
import { NotConnected } from '@/components/NotConnected';

export const dynamic = 'force-dynamic';
export const metadata: Metadata = {
  title: 'Where we stand',
  description: 'The position behind the essays, stated plainly and kept apart from the record.',
};

/**
 * The publication's position, in its own words.
 *
 * Editorial, like an essay, and approved the same way: it is a row in
 * editorial.essays with kind 'position', and this page shows it only once the
 * editor has approved it. Until then the page does not exist.
 */
export default async function WhereWeStandPage() {
  if (!isConfigured()) return <NotConnected what="pages" />;

  const position = await getPosition();
  if (!position) notFound();

  const sources = await sourcesByPipelineId(sourcesInOrder(position.body ?? ''));

  return (
    <EssayArticle
      piece={position}
      sources={sources}
      footer={
        <CiteThisPage
          citation={pageCitation({
            title: position.title,
            path: '/where-we-stand',
            publishDate: position.publish_date,
            dataAsOfDate: position.data_as_of_date,
          })}
        />
      }
    />
  );
}
