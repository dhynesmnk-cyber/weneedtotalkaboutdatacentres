// lib/sample-data.ts
// DEV / DEMO FIXTURES ONLY — clearly marked, never presented as fact.
// This dataset exists so the UX plan (Phase 0/1) can be built and tested
// before the production database is populated. In production every value here
// comes from Supabase via lib/db.ts, and every row carries a source record.
// The mix of values and gap flags is intentional: it exercises the
// "sparse data must look intentional" rule (UX-PLAN Epic G3).

import type {
  ClaimVsRecordPair,
  Entity,
  Essay,
  Locality,
  ObservatoryEvent,
  Site,
  SourceRecord,
} from "./types";
import { gap, value } from "./gap";

export const SAMPLE_SOURCES: readonly SourceRecord[] = [
  {
    id: 1,
    type: "council",
    title: "Development application assessment report (illustrative)",
    url: "https://example.gov.au/da/illustrative",
    retrievedDate: "2026-08-14",
    publisher: "Illustrative council record",
  },
  {
    id: 2,
    type: "company",
    title: "Company announcement re data centre investment (illustrative)",
    url: "https://example.com/announcement",
    retrievedDate: "2026-07-02",
    publisher: "Illustrative ASX release",
  },
  {
    id: 3,
    type: "aemo",
    title: "Generation information extract (illustrative)",
    url: "https://example.aemo/quarterly",
    retrievedDate: "2026-07-31",
    publisher: "Illustrative AEMO quarterly parse",
  },
];

export const SAMPLE_SITES: readonly Site[] = [
  {
    id: 1,
    slug: "illustra-west-datagrid",
    name: "Illustra West Data Grid",
    operator: value("Illustrative Cloud Pty Ltd"),
    lat: -33.78,
    lng: 150.7,
    lgaCode: "NSW220",
    lgaName: "Illustrative Hills LGA",
    status: value("under_construction"),
    totalCapacityMW: value(480),
    liveCapacityMW: gap("not_published"),
    coolingType: gap("pending_verification", "operator announced two options; not confirmed"),
    rackDensityKW: gap("not_published"),
    gridConnection: value("Illustrative Substation T-11 (220 kV)"),
    waterUsage: gap("not_tracked", "water reporting begins at commissioning in our scope"),
    notes: "DEMO ROW — structure example only.",
  },
  {
    id: 2,
    slug: "port-illustration-terminal-hall",
    name: "Port Illustration Terminal Hall",
    operator: gap("conflicting_sources", "two operators named across different reports"),
    lat: -32.93,
    lng: 151.78,
    lgaCode: "NSW180",
    lgaName: "Illustrative Coastal City",
    status: value("proposed"),
    totalCapacityMW: value(1200),
    liveCapacityMW: gap("not_tracked", "pre-construction site"),
    coolingType: value("Seawater heat exchange (claimed)"),
    rackDensityKW: gap("not_published"),
    gridConnection: gap("pending_verification"),
    waterUsage: gap("not_published"),
    notes: "DEMO ROW — exercises conflicting-source gap handling.",
  },
  {
    id: 3,
    slug: "grassroots-commons-node",
    name: "Grassroots Commons Node",
    operator: value("Illustrative Territory Power"),
    lat: -35.28,
    lng: 149.13,
    lgaCode: "ACTGN",
    lgaName: "Illustrative Territory",
    status: value("live"),
    totalCapacityMW: value(65),
    liveCapacityMW: value(65),
    coolingType: value("Air-side economisers"),
    rackDensityKW: value(40),
    gridConnection: value("Illustrative Feeders F1/F2"),
    waterUsage: gap("not_published"),
    notes: "DEMO ROW — a fully-known small site for comparison view testing.",
  },
  {
    id: 4,
    slug: "dry-plains-stalled-campus",
    name: "Dry Plains Campus (paused)",
    operator: value("Illustrative Hyperscale Inc"),
    lat: -33.45,
    lng: 146.5,
    lgaCode: "NSW430",
    lgaName: "Illustrative Plains Shire",
    status: value("stalled"),
    totalCapacityMW: value(900),
    liveCapacityMW: gap("not_tracked", "never energised"),
    coolingType: gap("not_published"),
    rackDensityKW: gap("not_published"),
    gridConnection: value("Grid offer issued 2025, not exercised"),
    waterUsage: gap("not_tracked"),
    notes: "DEMO ROW — stalled-project naming requires citations (SPEC.md policy).",
  },
];

export const SAMPLE_ENTITIES: readonly Entity[] = [
  {
    id: 1,
    slug: "illustrative-cloud-pty-ltd",
    name: "Illustrative Cloud Pty Ltd",
    type: "operator",
    role: "Hyperscale operator and anchor tenant",
    majorFlag: true,
    publicActionsSummary:
      "Announced construction start; published an employment impact statement (demo text).",
  },
  {
    id: 2,
    slug: "illustrative-hyperscale-inc",
    name: "Illustrative Hyperscale Inc",
    type: "developer",
    role: "Developer of paused campus projects",
    majorFlag: true,
    publicActionsSummary: "Confirmed pause pending grid timelines (demo text).",
  },
  {
    id: 3,
    slug: "locals-against-land-use-change",
    name: "Illustrative Locals Alliance",
    type: "community_group",
    role: "Community submission group",
    majorFlag: false,
    publicActionsSummary:
      "Lodged planning objections via council submissions process (the only channel we track).",
  },
];

export const SAMPLE_EVENTS: readonly ObservatoryEvent[] = [
  {
    id: 1,
    slug: "iw-dg-da-approved",
    category: "planning",
    date: "2026-02-18",
    title: "DA approved with conditions (Illustra West)",
    summary: "Council approved the Stage 1 development application (demo event).",
    siteId: 1,
    entityIds: [1],
    sourceIds: [1],
    significance: "major",
  },
  {
    id: 2,
    slug: "iw-dg-construction-start",
    category: "construction",
    date: "2026-05-06",
    title: "Construction commencement announced",
    summary: "Operator confirmed shovels in the ground for Stage 1 (demo event).",
    siteId: 1,
    entityIds: [1],
    sourceIds: [2],
    significance: "major",
  },
  {
    id: 3,
    slug: "dp-campus-pause",
    category: "financial",
    date: "2026-06-30",
    title: "Dry Plains campus paused citing grid timelines",
    summary: "Developer announcement recorded as a dated financial event (demo).",
    siteId: 4,
    entityIds: [2],
    sourceIds: [2],
    significance: "major",
  },
  {
    id: 4,
    slug: "pi-objector-submissions",
    category: "community",
    date: "2026-07-15",
    title: "Objection submissions close (Port Illustration)",
    summary: "Council reported submission counts for the exhibition period (demo).",
    siteId: 2,
    entityIds: [3],
    sourceIds: [1],
    significance: "notable",
  },
  {
    id: 5,
    slug: "media-national-story",
    category: "media",
    date: "2026-08-02",
    title: "National coverage of AI infrastructure demand",
    summary: "Example perception event used by the essay pipeline (demo).",
    entityIds: [],
    sourceIds: [2],
    significance: "routine",
  },
  {
    id: 6,
    slug: "political-question-time",
    category: "political",
    date: "2026-08-20",
    title: "Parliamentary question on data centre water use",
    summary: "Hansard record cited; answer referenced our tracked fields (demo).",
    entityIds: [],
    sourceIds: [3],
    significance: "notable",
  },
];

export const SAMPLE_ESSAYS: readonly Essay[] = [
  {
    id: 1,
    slug: "what-the-numbers-say-about-water",
    title: "What the numbers actually say about data centre water use",
    publishDate: "2026-09-10",
    youtubeId: undefined, // demo: no video attached
    body:
      "DEMO ESSAY. Perception: 'data centres are draining the grid and the dam'. " +
      "The records: live capacity versus proposed capacity, cooling types we can verify, " +
      "and the fields where sources simply have not published numbers yet. " +
      "Every figure in a real essay links to a database record via the citation panel.",
    tags: ["water", "energy", "perception-vs-data"],
    relatedRecordIds: [
      { recordTable: "sites", recordId: 1, sourceId: 1, claimSummary: "Stage 1 approval date" },
      { recordTable: "events", recordId: 6, sourceId: 3, claimSummary: "water-use question" },
      { recordTable: "sites", recordId: 3, sourceId: 3, claimSummary: "cooling type verified" },
      { recordTable: "events", recordId: 3, sourceId: 2, claimSummary: "pause announcement" },
      { recordTable: "entities", recordId: 1, sourceId: 2, claimSummary: "operator actions" },
    ],
    layer: "editorial",
  },
];

export const SAMPLE_CLAIM_VS_RECORD: readonly ClaimVsRecordPair[] = [
  {
    claim: "\u201cEvery AI data centre in Australia is already using a city's worth of power.\u201d",
    claimSourceId: 2,
    recordSummary:
      "Across tracked sites, live capacity totals far less than proposed capacity; most MW are still on paper.",
    recordTable: "sites",
    recordId: 1,
    recordDate: "2026-09-01",
  },
  {
    claim: "\u201cNobody knows how much water these places use.\u201d",
    claimSourceId: 3,
    recordSummary:
      "Partly true — and we say so: water usage shows a gap flag on three of four demo sites because sources have not published figures.",
    recordTable: "events",
    recordId: 6,
    recordDate: "2026-08-20",
  },
];

export const SAMPLE_LOCALITIES: readonly Locality[] = [
  { name: "Illustra West", postcode: "2150", lgaCode: "NSW220", lgaName: "Illustrative Hills LGA", lat: -33.78, lng: 150.7, sourceId: 1, asOfDate: "2026-01-01" },
  { name: "Rooty Hill", postcode: "2150", lgaCode: "NSW220", lgaName: "Illustrative Hills LGA", lat: -33.79, lng: 150.71, sourceId: 1, asOfDate: "2026-01-01" },
  { name: "Port Illustration", postcode: "2300", lgaCode: "NSW180", lgaName: "Illustrative Coastal City", lat: -32.93, lng: 151.78, sourceId: 1, asOfDate: "2026-01-01" },
  { name: "Garden Suburb", postcode: "2900", lgaCode: "ACTGN", lgaName: "Illustrative Territory", lat: -35.28, lng: 149.13, sourceId: 1, asOfDate: "2026-01-01" },
  { name: "Dry Plains", postcode: "2678", lgaCode: "NSW430", lgaName: "Illustrative Plains Shire", lat: -33.45, lng: 146.5, sourceId: 1, asOfDate: "2026-01-01" },
];

export const SITE_BY_ID = new Map(SAMPLE_SITES.map((s) => [s.id, s]));
export const ENTITY_BY_ID = new Map(SAMPLE_ENTITIES.map((e) => [e.id, e]));
export const SOURCE_BY_ID = new Map(SAMPLE_SOURCES.map((s) => [s.id, s]));
export const EVENT_BY_ID = new Map(SAMPLE_EVENTS.map((e) => [e.id, e]));
