'use client';

import { useState } from 'react';

/**
 * A ready-made reference for the page, with its dates and address (UX-PLAN's
 * "cite this record"). The text is always visible and selectable; the button
 * is a convenience that appears once JavaScript has run.
 */
export function CiteThisPage({ citation }: { citation: string }) {
  const [state, setState] = useState<'idle' | 'copied' | 'failed'>('idle');

  async function copy() {
    try {
      await navigator.clipboard.writeText(citation);
      setState('copied');
    } catch {
      setState('failed');
    }
  }

  return (
    <section aria-labelledby="cite-heading" className="rounded-lg border border-slate-200 p-4" data-print-hidden>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="cite-heading" className="text-sm font-semibold uppercase tracking-wide text-slate-700">
          Cite this page
        </h2>
        <button
          type="button"
          onClick={copy}
          className="min-h-9 rounded border border-slate-500 px-3 text-sm font-medium text-slate-900"
        >
          {state === 'copied' ? 'Copied' : 'Copy'}
        </button>
      </div>
      <p className="mt-2 break-words font-mono text-xs text-slate-700">{citation}</p>
      <p aria-live="polite" className="sr-only">
        {state === 'copied' ? 'Reference copied' : state === 'failed' ? 'Could not copy; select the text instead' : ''}
      </p>
    </section>
  );
}
