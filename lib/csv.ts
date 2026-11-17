/**
 * CSV for the data downloads (/data).
 *
 * RFC 4180: comma-separated, every field that needs it quoted, quotes doubled,
 * CRLF line endings. A UTF-8 byte order mark leads the file so spreadsheet
 * programs read "Kurri Kurri – Hart Road" or "IFM Real Estate Fiduciary’s"
 * correctly.
 *
 * The formula-injection guard: a text cell that a spreadsheet would run as a
 * formula (starting =, +, -, @, a tab or a carriage return) is prefixed with an
 * apostrophe, so it is shown as text and never evaluated. Numbers are written
 * as numbers and are not prefixed, so a negative latitude stays a number.
 *
 * Pure functions. Nothing here reads a database.
 */

export type Cell = string | number | boolean | null | undefined;

const FORMULA_START = /^[=+\-@\t\r]/;

/** A text value as a spreadsheet may safely display it. */
export function guardFormula(value: string): string {
  return FORMULA_START.test(value) ? `'${value}` : value;
}

/** One field, guarded and quoted as needed. A null is an empty field. */
export function csvCell(value: Cell): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : '';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  const text = guardFormula(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

/** A whole file: the header row, then one row per record. */
export function toCsv(header: readonly string[], rows: readonly (readonly Cell[])[]): string {
  const lines = [header.map(csvCell).join(','), ...rows.map((row) => row.map(csvCell).join(','))];
  return `﻿${lines.join('\r\n')}\r\n`;
}

/** The download's file name: the dataset and the date the record was loaded. */
export function csvFileName(dataset: string, asOf: string | null): string {
  const date = asOf ? asOf.slice(0, 10) : 'undated';
  return `datacentres-${dataset}-${date}.csv`;
}
