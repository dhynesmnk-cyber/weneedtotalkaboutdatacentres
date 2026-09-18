/**
 * Shown when no Supabase project is configured.
 *
 * The alternative — seeding the scaffold with invented sites so the pages look
 * populated — would put fabricated figures in front of a reader, which is the
 * one thing this project may not do. An empty observatory that says it is empty
 * is the honest state.
 */
export function NotConnected({ what }: { what: string }) {
  return (
    <div className="rounded-lg border border-slate-300 bg-slate-50 p-6">
      <h2 className="font-semibold text-slate-900">No database connected</h2>
      <p className="mt-2 text-sm text-slate-700">
        There is no Supabase project configured, so there are no {what} to show.
        This is the scaffold&rsquo;s empty state, not an error, and no sample data
        has been substituted.
      </p>
      <p className="mt-2 text-sm text-slate-700">
        Copy <code className="rounded bg-white px-1">.env.example</code> to{' '}
        <code className="rounded bg-white px-1">.env.local</code>, point it at a
        project with <code className="rounded bg-white px-1">supabase/migrations</code>{' '}
        applied, and expose the{' '}
        <code className="rounded bg-white px-1">facts</code> and{' '}
        <code className="rounded bg-white px-1">editorial</code> schemas in the
        project&rsquo;s API settings.
      </p>
    </div>
  );
}

/** Shown when the database is connected but a table is genuinely empty. */
export function NothingRecorded({ what }: { what: string }) {
  return (
    <div className="rounded-lg border border-slate-300 bg-slate-50 p-6">
      <p className="text-sm text-slate-700">
        No {what} recorded yet.
      </p>
    </div>
  );
}
