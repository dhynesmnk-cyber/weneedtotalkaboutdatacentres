/**
 * A headline count, optionally out of a total with a meter beneath it.
 *
 * The number is the content; the meter only restates it. It is hidden from
 * assistive technology because the text already says "5 of 93", and a
 * progressbar role would announce the same fact twice. Track and fill are
 * steps of the fact ramp, so the tile reads as record, not as a warning:
 * a low count here is a finding about the research, not an alert.
 */
export function StatTile({
  label,
  value,
  total,
  note,
}: {
  label: string;
  value: number;
  /** When given, the value is shown as "value of total" with a meter. */
  total?: number;
  note?: string;
}) {
  const share = total ? Math.min(1, value / total) : null;

  return (
    <div className="rounded-lg border border-fact-edge bg-white p-4">
      <p className="text-sm font-medium text-slate-600">{label}</p>
      <p className="mt-1 text-slate-900">
        <span className="text-3xl font-semibold text-fact-ink">
          {value.toLocaleString('en-AU')}
        </span>
        {total !== undefined && (
          <span className="ml-1 text-sm text-slate-600">
            of {total.toLocaleString('en-AU')}
          </span>
        )}
      </p>
      {share !== null && (
        <div aria-hidden="true" className="mt-3 h-2 w-full rounded-full bg-fact-edge/60">
          {share > 0 && (
            <div
              className="h-2 rounded-full bg-fact-ink"
              // Never narrower than its own rounding, so a small non-zero
              // count still shows as a mark rather than vanishing.
              style={{ width: `max(${(share * 100).toFixed(1)}%, 0.5rem)` }}
            />
          )}
        </div>
      )}
      {note && <p className="mt-2 text-xs text-slate-600">{note}</p>}
    </div>
  );
}
