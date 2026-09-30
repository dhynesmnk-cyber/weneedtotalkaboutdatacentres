// lib/csv.ts
// Journalist toolkit CSV export (Epic E2). Exported rows must match the DB
// query row-for-row — enforced by tests. Gap fields export as the literal
// "GAP: <reason>" so downstream users never mistake a blank for zero.

import type { Field } from "./types";
import { gapLabel } from "./gap";

const escapeCell = (s: string): string => {
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
};

export function fieldToCell(f: Field<unknown>): string {
  if (f.kind === "gap") return `GAP: ${gapLabel(f.gap)}`;
  return String(f.value);
}

export function toCsv(
  headers: readonly string[],
  rows: readonly (readonly string[])[],
): string {
  const lines = [headers.map(escapeCell).join(",")];
  for (const r of rows) lines.push(r.map(escapeCell).join(","));
  return `${lines.join("\r\n")}\r\n`;
}

/** Convenience: build an export from typed records and column selectors. */
export function exportTable<T>(
  columns: readonly { header: string; cell: (row: T) => string }[],
  data: readonly T[],
): string {
  return toCsv(
    columns.map((c) => c.header),
    data.map((row) => columns.map((c) => c.cell(row))),
  );
}
