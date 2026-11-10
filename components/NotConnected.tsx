/**
 * Shown when no Supabase project is configured.
 *
 * The alternative — seeding the scaffold with invented sites so the pages look
 * populated — would put fabricated figures in front of a reader, which is the
 * one thing this project may not do. An empty observatory that says it is empty
 * is the honest state.
 *
 * Readers are told the record is unavailable. The setup steps are for whoever
 * is running the site locally, so they appear only in development.
 */
export function NotConnected({ what }: { what: string }) {
  const developing = process.env.NODE_ENV === 'development';

  return (
    <div role="status" className="rounded-lg border border-slate-200 bg-slate-50 p-6">
      <h2 className="font-semibold text-slate-900">The record is unavailable right now</h2>
      <p className="mt-2 text-sm text-slate-700">
        The database behind this page could not be reached, so there are no {what}{' '}
        to show. Nothing has been put in their place: this site never shows sample
        or estimated figures. Please try again later.
      </p>
      {developing && (
        <p className="mt-3 border-t border-slate-200 pt-3 text-sm text-slate-700">
          <strong className="font-semibold">For developers:</strong> no Supabase
          project is configured. Copy{' '}
          <code className="rounded bg-white px-1">.env.example</code> to{' '}
          <code className="rounded bg-white px-1">.env.local</code>, point it at a
          project with <code className="rounded bg-white px-1">supabase/migrations</code>{' '}
          applied, and expose the <code className="rounded bg-white px-1">facts</code>{' '}
          and <code className="rounded bg-white px-1">editorial</code> schemas in the
          project&rsquo;s API settings.
        </p>
      )}
    </div>
  );
}

/** Shown when the database is connected but a table is genuinely empty. */
export function NothingRecorded({ what }: { what: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 p-6">
      <p className="text-sm text-slate-700">
        No {what} recorded yet. An empty list here is a finding about the record,
        not a fault in the page.
      </p>
    </div>
  );
}
