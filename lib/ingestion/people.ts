/**
 * People by role, in the published record.
 *
 * The site names people by public role only until legal review is arranged
 * (CLAUDE.md). The research database may hold names; the site may not. This
 * module builds, at load time, the list of people the research names and the
 * role each is published under. It then replaces every name in a text field
 * with that role, or with "[name withheld]" where the text already states the
 * role beside it.
 *
 * Three pipeline tables supply the people, and no list of names is ever
 * committed outside the pipeline:
 *   - people (schema/03_people.sql): the register. It is authoritative where it
 *     lists someone.
 *   - lobbying.person: "Name, role", with the organisation from the actor.
 *   - case_handling.officer_name: NSW planning officers, published as numbered
 *     planning officers so an analysis of their caseloads stays readable.
 *
 * Journalists' bylines in a source's publisher field are not listed, by the
 * author's decision of 2026-11-17: a byline is a citation's authorship.
 *
 * Pure functions: the caller supplies the rows.
 */

import type { PipelineRow } from '@/lib/ingestion/transform';

export interface Person {
  /** The name as the documents spell it. */
  name: string;
  /** Other spellings the record uses, matched exactly. */
  aliases: string[];
  /** The role published instead, without brackets. */
  role: string;
  /**
   * Officers share one role, so each carries a number, fixed for the whole
   * load (by caseload, then name), so "planning officer 2" is the same person
   * on every page. Null for everyone else.
   */
  number: number | null;
}

const OFFICER_ROLE = 'NSW planning officer';

// Postnominals that may follow a name and go with it.
const POSTNOMINALS = '(?:\\s(?:AC|AO|AM|OAM|CBE|OBE|MBE|KC|SC|QC|MP|MLC|MLA))*';
// A possessive after a name or surname: 's, ’s, or a bare apostrophe after s.
const POSSESSIVE = "(?:['’]s\\b|['’](?=\\s))?";

// Words that, just before a name or just after its comma or dash, already say
// what the person is. Then the role need not be repeated: the name is withheld.
const TITLE_WORDS =
  /\b(?:CEO|Chief Executive(?: Officer)?|Founder|Chair(?:man|woman|person)?|President|Commissioner|Secretary|Minister|Director(?: General)?|delegate|Premier|Treasurer|MP|Senator|Counsellor|Executive Director)\b/i;

function text(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  const s = String(value).trim();
  return s ? s : null;
}

/** A personal name: two or three capitalised words, optionally with postnominals. */
const NAME_SHAPE = /^[A-Z][a-z'’-]+(?: [A-Z][a-z'’-]+){1,2}$/;

function stripPostnominals(name: string): string {
  return name.replace(new RegExp(`${POSTNOMINALS}$`), '').trim();
}

/**
 * Everyone the published record must not name, from the three pipeline
 * tables. The register wins where it lists a name.
 */
export function peopleFromPipeline(input: {
  people: PipelineRow[];
  lobbying: PipelineRow[];
  caseHandling: PipelineRow[];
  entityNames: ReadonlyMap<string, string>;
}): Person[] {
  const byName = new Map<string, Person>();

  for (const row of input.people) {
    const name = text(row.name);
    const role = text(row.role);
    if (!name || !role) continue;
    const aliases = (text(row.aliases) ?? '')
      .split('|')
      .map((a) => a.trim())
      .filter(Boolean);
    byName.set(name, { name, aliases, role, number: null });
  }

  for (const row of input.lobbying) {
    const person = text(row.person);
    if (!person) continue;
    const comma = person.indexOf(',');
    const name = stripPostnominals((comma >= 0 ? person.slice(0, comma) : person).trim());
    if (!NAME_SHAPE.test(name) || byName.has(name)) continue;
    // The first clause of the recorded role, and the organisation if it is not already in it.
    const role = (comma >= 0 ? person.slice(comma + 1) : '').split(';')[0]!.trim();
    const organisation = input.entityNames.get(text(row.actor_id) ?? '') ?? null;
    const label =
      role && organisation && !role.includes(organisation) ? `${role}, ${organisation}` : role || organisation;
    if (label) byName.set(name, { name, aliases: [], role: label, number: null });
  }

  const caseload = new Map<string, number>();
  for (const row of input.caseHandling) {
    const name = text(row.officer_name);
    if (!name || !NAME_SHAPE.test(name) || byName.has(name)) continue;
    caseload.set(name, (caseload.get(name) ?? 0) + 1);
  }
  [...caseload.entries()]
    .sort(([a, x], [b, y]) => y - x || a.localeCompare(b))
    .forEach(([name], i) => byName.set(name, { name, aliases: [], role: OFFICER_ROLE, number: i + 1 }));

  return [...byName.values()];
}

function escape(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function surname(name: string): string {
  return name.split(' ').pop()!;
}

interface Hit {
  start: number;
  end: number;
  person: Person;
  /** The possessive that followed, kept so the sentence still reads. */
  possessive: string;
  /** Matched on the surname alone. */
  surnameOnly: boolean;
}

/** Whether the words around a match already say what the person is. */
function roleAlreadyStated(textValue: string, start: number, end: number): boolean {
  const before = textValue.slice(Math.max(0, start - 40), start);
  // The last few words before the name, within the same clause.
  const clause = before.split(/[.;:(\n]/).pop() ?? '';
  const lastWords = clause.trim().split(/\s+/).slice(-4).join(' ');
  if (TITLE_WORDS.test(lastWords)) return true;
  const after = textValue.slice(end, end + 50);
  return /^\s*(?:,|\s-|\s–)\s*/.test(after) && TITLE_WORDS.test(after.split(/[.;(\n]/)[0] ?? '');
}

/**
 * The text with every listed person replaced by their role, in square
 * brackets, or by "[name withheld]" where the role is stated beside the name.
 *
 * A surname used alone is replaced too, but only in a field that also holds
 * the full name, and only where no other listed person in that field shares
 * the surname.
 */
export function withholdNames(value: string | null, people: readonly Person[]): string | null {
  if (!value) return value;

  // Full names and aliases, longest first, so "Damian Parmenter CBE" wins over "Damian Parmenter".
  const spellings = people
    .flatMap((p) => [p.name, ...p.aliases].map((s) => ({ s, p })))
    .sort((a, b) => b.s.length - a.s.length);

  const hits: Hit[] = [];
  const taken = (start: number, end: number) => hits.some((h) => start < h.end && end > h.start);
  for (const { s, p } of spellings) {
    const re = new RegExp(`(?<![\\w'’])${escape(s)}${POSTNOMINALS}(${POSSESSIVE})`, 'g');
    for (const m of value.matchAll(re)) {
      const start = m.index!;
      const end = start + m[0].length;
      if (taken(start, end)) continue;
      hits.push({ start, end, person: p, possessive: m[1] ?? '', surnameOnly: false });
    }
  }

  // Surnames alone, for people whose full name is in this field.
  const present = [...new Set(hits.map((h) => h.person))];
  const surnameCount = new Map<string, number>();
  for (const p of present) surnameCount.set(surname(p.name), (surnameCount.get(surname(p.name)) ?? 0) + 1);
  for (const p of present) {
    const last = surname(p.name);
    if (last.length < 4 || surnameCount.get(last)! > 1) continue;
    const re = new RegExp(`(?<![\\w'’])${escape(last)}(?![\\w-])(${POSSESSIVE})`, 'g');
    for (const m of value.matchAll(re)) {
      const start = m.index!;
      const end = start + m[0].length;
      if (taken(start, end)) continue;
      hits.push({ start, end, person: p, possessive: m[1] ?? '', surnameOnly: true });
    }
  }
  if (!hits.length) return value;

  // Officers carry their load-wide number. Anyone else who shares a role with
  // another person in the same field is numbered in the order they appear.
  hits.sort((a, b) => a.start - b.start);
  const labels = new Map<Person, string>();
  const shared = new Map<string, Person[]>();
  for (const h of hits) {
    if (h.person.number !== null) continue;
    const group = shared.get(h.person.role) ?? [];
    if (!group.includes(h.person)) group.push(h.person);
    shared.set(h.person.role, group);
  }
  for (const h of hits) {
    if (h.person.number !== null) labels.set(h.person, `${h.person.role} ${h.person.number}`);
  }
  for (const [role, group] of shared) {
    group.forEach((p, i) => labels.set(p, group.length > 1 ? `${role} ${i + 1}` : role));
  }

  let out = '';
  let cursor = 0;
  for (const h of hits) {
    out += value.slice(cursor, h.start);
    const withheld = !h.surnameOnly && roleAlreadyStated(value, h.start, h.end);
    const label = withheld ? 'name withheld' : labels.get(h.person)!;
    const possessive = h.possessive ? (h.possessive.length === 1 ? `${h.possessive}s` : h.possessive) : '';
    out += `[${label}]${possessive}`;
    cursor = h.end;
  }
  return out + value.slice(cursor);
}

/** The listed people still named in a text, by role (never by name). */
export function rolesNamedIn(value: string | null, people: readonly Person[]): string[] {
  if (!value) return [];
  return people
    .filter((p) =>
      [p.name, ...p.aliases].some((s) => new RegExp(`(?<![\\w'’])${escape(s)}(?![\\w])`).test(value)),
    )
    .map((p) => p.role);
}
