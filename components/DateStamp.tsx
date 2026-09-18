import { formatDate } from '@/lib/format';

/**
 * Publish date and data-as-of date.
 *
 * docs/UI.md: everything is dated, and both dates are shown. They answer
 * different questions — when this was written, and when the numbers in it were
 * current — and a piece published this month from data a year old is a
 * different claim from a fresh one.
 */
export function DateStamp({
  publishDate,
  dataAsOfDate,
  className = '',
}: {
  publishDate?: string | null;
  dataAsOfDate?: string | null;
  className?: string;
}) {
  const published = formatDate(publishDate);
  const asOf = formatDate(dataAsOfDate);

  if (!published && !asOf) return null;

  return (
    <p className={`text-sm text-slate-600 ${className}`}>
      {published && (
        <>
          Published{' '}
          <time dateTime={publishDate ?? undefined} className="font-medium">
            {published}
          </time>
        </>
      )}
      {published && asOf && <span aria-hidden="true"> · </span>}
      {asOf && (
        <>
          Data as at{' '}
          <time dateTime={dataAsOfDate ?? undefined} className="font-medium">
            {asOf}
          </time>
        </>
      )}
    </p>
  );
}
