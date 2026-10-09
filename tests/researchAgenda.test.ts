import { describe, expect, it } from 'vitest';
import { groupResearchAgenda, researchPillars } from '@/lib/researchAgenda';
import {
  formatPillar,
  formatPriority,
  formatResearchStatus,
  formatRetrievalMethod,
} from '@/lib/format';
import { RESEARCH_STATUSES, type ResearchStatus } from '@/lib/types';

function q(pipeline_id: string, status: ResearchStatus, priority: number | null, pillar = 'A') {
  return { pipeline_id, status, priority, pillar };
}

describe('groupResearchAgenda', () => {
  it('orders statuses by lifecycle and leaves out empty ones', () => {
    const groups = groupResearchAgenda([
      q('RG-003', 'resolved', 3),
      q('RG-001', 'open', 3),
      q('RG-002', 'in_progress', 3),
    ]);
    expect(groups.map((g) => g.status)).toEqual(['in_progress', 'open', 'resolved']);
  });

  it('puts the most urgent first, 5 being most urgent, then orders by label', () => {
    const [open] = groupResearchAgenda([
      q('RG-010', 'open', 2),
      q('RG-002', 'open', 5),
      q('RG-001', 'open', 5),
      q('RG-004', 'open', null),
    ]);
    expect(open?.questions.map((x) => x.pipeline_id)).toEqual([
      'RG-001',
      'RG-002',
      'RG-010',
      'RG-004',
    ]);
  });

  it('drops no question', () => {
    const questions = RESEARCH_STATUSES.map((s, i) => q(`RG-00${i}`, s, i));
    const total = groupResearchAgenda(questions).reduce((n, g) => n + g.questions.length, 0);
    expect(total).toBe(questions.length);
  });
});

describe('researchPillars', () => {
  it('lists each pillar once, in letter order', () => {
    expect(researchPillars([{ pillar: 'C' }, { pillar: 'A' }, { pillar: 'C' }, { pillar: null }]))
      .toEqual(['A', 'C']);
  });
});

describe('research labels', () => {
  it('names every status in words', () => {
    for (const status of RESEARCH_STATUSES) {
      expect(formatResearchStatus(status)).toMatch(/^[A-Z][a-z ]+$/);
    }
    expect(formatResearchStatus('wont_fix')).toBe('Closed without an answer');
  });

  it('names the five pillars, and shows an unknown one as recorded', () => {
    expect(formatPillar('B')).toBe('Capital and control');
    expect(formatPillar('Z')).toBe('Z');
    expect(formatPillar(null)).toBeNull();
  });

  it('says how a question is answered in words, and keeps an unknown method visible', () => {
    expect(formatRetrievalMethod('foi_request')).toBe('Freedom of information request');
    expect(formatRetrievalMethod('carrier_pigeon')).toBe('carrier_pigeon');
  });

  it('reads priority 5 as the most urgent', () => {
    expect(formatPriority(5)).toBe('Most urgent');
    expect(formatPriority(1)).toBe('Lowest priority');
    expect(formatPriority(7)).toBeNull();
    expect(formatPriority(null)).toBeNull();
  });
});
