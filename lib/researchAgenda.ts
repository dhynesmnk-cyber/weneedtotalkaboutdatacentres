import { facts, isConfigured } from '@/lib/supabase/server';
import {
  RESEARCH_STATUSES,
  type CitationWithSource,
  type ResearchAgendaRow,
  type ResearchStatus,
} from '@/lib/types';

/**
 * Typed access to facts.research_agenda: the questions the record has not yet
 * answered, and the sources that show each one is a real question.
 *
 * Not the same as a gap. A gap is one missing field on one record; a question
 * is a line of enquiry that may span many records or none (0009).
 */

export interface ResearchQuestion extends ResearchAgendaRow {
  citations: CitationWithSource[];
}

export async function listResearchAgenda(): Promise<ResearchQuestion[]> {
  if (!isConfigured()) return [];

  // Two reads rather than one per question: there are about eighty questions,
  // and the page shows all of them.
  const [questions, citations] = await Promise.all([
    facts().from('research_agenda').select('*').order('pipeline_id'),
    facts()
      .from('citations')
      .select('*, source:sources(*)')
      .eq('record_type', 'research_agenda'),
  ]);

  if (questions.error) {
    throw new Error(`Failed to load the research agenda: ${questions.error.message}`);
  }
  if (citations.error) {
    throw new Error(`Failed to load research agenda citations: ${citations.error.message}`);
  }

  const byQuestion = new Map<string, CitationWithSource[]>();
  for (const citation of (citations.data ?? []) as unknown as CitationWithSource[]) {
    const list = byQuestion.get(citation.record_id) ?? [];
    list.push(citation);
    byQuestion.set(citation.record_id, list);
  }

  return (questions.data ?? []).map((q) => ({ ...q, citations: byQuestion.get(q.id) ?? [] }));
}

export interface ResearchStatusGroup<T> {
  status: ResearchStatus;
  questions: T[];
}

/**
 * Questions grouped by status, in lifecycle order: what is being worked on
 * first, what is closed last. Within a status, the most urgent come first, then
 * by label so the order is stable. Statuses with no questions are left out.
 */
export function groupResearchAgenda<
  T extends Pick<ResearchAgendaRow, 'status' | 'priority' | 'pipeline_id'>,
>(questions: readonly T[]): ResearchStatusGroup<T>[] {
  return RESEARCH_STATUSES.map((status) => ({
    status,
    questions: questions
      .filter((q) => q.status === status)
      .sort(
        (a, b) =>
          (b.priority ?? 0) - (a.priority ?? 0) ||
          (a.pipeline_id ?? '').localeCompare(b.pipeline_id ?? ''),
      ),
  })).filter((group) => group.questions.length > 0);
}

/** The pillars present, in letter order, for the page's filter. */
export function researchPillars(
  questions: readonly Pick<ResearchAgendaRow, 'pillar'>[],
): string[] {
  return [...new Set(questions.map((q) => q.pillar).filter((p): p is string => !!p))].sort();
}
