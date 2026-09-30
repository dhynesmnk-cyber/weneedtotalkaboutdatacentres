// components/primitives/FieldValue.tsx — renders a Field<T>: either the value
// or a GapBadge. This is the single render path for nullable data, so no page
// can accidentally draw a blank cell (Gap-flag discipline metric).

import type { Field } from "@/lib/types";
import GapBadge from "./GapBadge";

export default function FieldValue<T>({
  field,
  render,
}: {
  field: Field<T>;
  render?: (v: T) => React.ReactNode;
}) {
  if (field.kind === "gap") return <GapBadge gap={field.gap} />;
  return <>{render ? render(field.value) : String(field.value)}</>;
}
