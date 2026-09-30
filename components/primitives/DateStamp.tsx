// components/primitives/DateStamp.tsx — everything is dated. Shows publish and
// data-as-of dates together, machine-readable via <time datetime>.

import { formatDateAu } from "@/lib/dates";

export default function DateStamp({
  publishDate,
  dataAsOf,
}: {
  publishDate: string;
  dataAsOf?: string;
}) {
  return (
    <p className="text-xs" style={{ color: "var(--ink-500)" }}>
      Published <time dateTime={publishDate}>{formatDateAu(publishDate)}</time>
      {dataAsOf ? (
        <>
          {" · data as of "}
          <time dateTime={dataAsOf}>{formatDateAu(dataAsOf)}</time>
        </>
      ) : null}
    </p>
  );
}
