// components/blocks/DownloadCsv.tsx
// Journalist toolkit download (Epic E2). Renders a data-URI download link so
// exports work without a server route; the CSV content is generated from the
// same typed records that render the table, row-for-row.

type Props = {
  filename: string;
  csv: string;
  label?: string;
};

export default function DownloadCsv({
  filename,
  csv,
  label = "Download CSV",
}: Props) {
  const href = `data:text/csv;charset=utf-8,${encodeURIComponent(csv)}`;
  return (
    <a
      href={href}
      download={filename}
      className="inline-flex items-center gap-2 rounded border border-neutral-300 px-3 py-1.5 text-sm font-medium text-neutral-800 hover:bg-neutral-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
    >
      <svg
        aria-hidden="true"
        width="14"
        height="14"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <path d="M8 2v8m0 0L5 7m3 3l3-3M3 13h10" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      {label}
    </a>
  );
}
