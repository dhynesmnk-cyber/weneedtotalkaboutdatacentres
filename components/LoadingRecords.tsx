/**
 * Shown while a page's records load. Pages read the database on every request,
 * so without this a slow query looked like a page that had stopped.
 *
 * Plain text in a live region rather than a skeleton: a grey block shaped like
 * a figure is too close to showing a figure that does not exist yet.
 *
 * Used only by routes that never answer 404. A loading boundary starts the
 * response streaming with status 200, so a record page under one could no
 * longer return 404 for a record that does not exist.
 */
export function LoadingRecords() {
  return (
    <div role="status" aria-live="polite" aria-busy="true" className="py-16">
      <p className="kicker text-slate-600">Loading</p>
      <p className="mt-2 text-slate-700">Fetching the records for this page&hellip;</p>
    </div>
  );
}
