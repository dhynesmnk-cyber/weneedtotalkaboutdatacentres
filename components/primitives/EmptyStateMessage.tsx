// components/primitives/EmptyStateMessage.tsx — gap-aware empty states. A
// sparse dataset must look intentional: say what we track, what we know, and
// how we'd know if something appeared here.

export default function EmptyStateMessage({
  title,
  explanation,
  actionHref,
  actionLabel,
}: {
  title: string;
  explanation: string;
  actionHref?: string;
  actionLabel?: string;
}) {
  return (
    <div
      role="status"
      className="rounded-lg border border-dashed p-6 text-center"
      style={{ borderColor: "var(--line)", background: "var(--card)" }}
    >
      <p className="text-base font-semibold" style={{ color: "var(--ink-900)" }}>
        {title}
      </p>
      <p className="mx-auto mt-1 max-w-prose text-sm" style={{ color: "var(--ink-700)" }}>
        {explanation}
      </p>
      {actionHref && actionLabel ? (
        <a
          href={actionHref}
          className="mt-3 inline-block rounded-md px-3 py-1.5 text-sm font-medium text-white"
          style={{ background: "var(--fact-accent)" }}
        >
          {actionLabel}
        </a>
      ) : null}
    </div>
  );
}
