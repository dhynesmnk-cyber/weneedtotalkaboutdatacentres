'use client';

/**
 * Shown when a page fails to load, most often because the database could not
 * be reached.
 *
 * The error's message is never rendered: in production it is redacted anyway,
 * and in development it can carry query details that are not for readers. The
 * digest is shown instead, because it matches the server log entry and is
 * what a reader can usefully quote when reporting the fault.
 */
export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="space-y-4" role="alert">
      <h1 className="text-2xl font-bold text-slate-900">This page could not be loaded</h1>
      <p className="max-w-2xl text-slate-700">
        Something went wrong while fetching the records for this page. Nothing
        has been shown in their place. Try again, and if the fault persists,
        please report it.
      </p>
      {error.digest && (
        <p className="text-sm text-slate-600">
          Reference: <code className="rounded bg-slate-100 px-1">{error.digest}</code>
        </p>
      )}
      <button
        type="button"
        onClick={reset}
        className="rounded border border-fact-edge bg-white px-3 py-1 text-sm text-fact-ink"
      >
        Try again
      </button>
    </div>
  );
}
