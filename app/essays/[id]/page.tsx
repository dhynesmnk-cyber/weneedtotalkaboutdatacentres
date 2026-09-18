import { notFound } from 'next/navigation';
import { getEssay, youtubeEmbedUrl } from '@/lib/editorial';
import { citationsFor } from '@/lib/evidence';
import { isConfigured } from '@/lib/supabase/server';
import { SourcePanel } from '@/components/SourcePanel';
import { DateStamp } from '@/components/DateStamp';
import {
  EditorialBlock,
  FactOpinionDivider,
} from '@/components/FactOpinionDivider';
import { NotConnected } from '@/components/NotConnected';

export const dynamic = 'force-dynamic';

/**
 * Essay page: embed, body, sources.
 *
 * An essay is editorial from the first word, so the divider sits above the body
 * rather than partway through it. The source panel is still present: analysis
 * that rests on facts should show which.
 */
export default async function EssayPage({ params }: { params: { id: string } }) {
  if (!isConfigured()) {
    return <NotConnected what="essays" />;
  }

  const essay = await getEssay(params.id);
  if (!essay) notFound();

  const citations = await citationsFor('essays', essay.id);
  const embedUrl = youtubeEmbedUrl(essay.youtube_id);

  return (
    <article className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">{essay.title}</h1>
        <DateStamp publishDate={essay.publish_date} className="mt-2" />
      </header>

      {embedUrl && (
        <div className="aspect-video w-full overflow-hidden rounded-lg border border-slate-200">
          <iframe
            src={embedUrl}
            title={`Video essay: ${essay.title}`}
            className="h-full w-full"
            allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      <FactOpinionDivider />

      {essay.body && (
        <EditorialBlock>
          <div className="prose-slate max-w-none whitespace-pre-line text-slate-800">
            {essay.body}
          </div>
        </EditorialBlock>
      )}

      <SourcePanel
        citations={citations}
        title="Sources referenced in this essay"
      />
    </article>
  );
}
