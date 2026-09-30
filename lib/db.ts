// lib/db.ts
// Typed data-access functions — the ONLY path components use to read data
// (CLAUDE.md convention). When Supabase is configured, reads go through RLS
// public views; otherwise we serve the clearly-marked demo fixtures so the
// UX build can proceed before the production database exists.

import { getSupabase, isDatabaseConfigured } from "./supabase";
import {
  SAMPLE_CLAIM_VS_RECORD,
  SAMPLE_ENTITIES,
  SAMPLE_ESSAYS,
  SAMPLE_EVENTS,
  SAMPLE_LOCALITIES,
  SAMPLE_SOURCES,
  SAMPLE_SITES,
} from "./sample-data";
import type {
  ClaimVsRecordPair,
  Entity,
  Essay,
  Locality,
  ObservatoryEvent,
  Site,
  SourceRecord,
} from "./types";

export const dataSourceLabel = (): string =>
  isDatabaseConfigured() ? "database" : "demo fixtures";

export async function getSites(): Promise<Site[]> {
  const sb = getSupabase();
  if (!sb) return [...SAMPLE_SITES];
  const { data, error } = await sb.from("v_sites_public").select("*").order("name");
  if (error) throw error;
  return data as Site[];
}

export async function getSiteBySlug(slug: string): Promise<Site | undefined> {
  const sb = getSupabase();
  if (!sb) return SAMPLE_SITES.find((s) => s.slug === slug);
  const { data, error } = await sb.from("v_sites_public").select("*").eq("slug", slug).maybeSingle();
  if (error) throw error;
  return (data ?? undefined) as Site | undefined;
}

export async function getEntities(): Promise<Entity[]> {
  const sb = getSupabase();
  if (!sb) return [...SAMPLE_ENTITIES];
  const { data, error } = await sb.from("entities").select("*").order("name");
  if (error) throw error;
  return data as Entity[];
}

export async function getEvents(): Promise<ObservatoryEvent[]> {
  const sb = getSupabase();
  if (!sb) return [...SAMPLE_EVENTS];
  const { data, error } = await sb.from("v_events_public").select("*").order("date", { ascending: false });
  if (error) throw error;
  return data as ObservatoryEvent[];
}

export async function getEssays(): Promise<Essay[]> {
  const sb = getSupabase();
  if (!sb) return [...SAMPLE_ESSAYS];
  const { data, error } = await sb.from("essays").select("*").order("publish_date", { ascending: false });
  if (error) throw error;
  return data as Essay[];
}

export async function getEssayBySlug(slug: string): Promise<Essay | undefined> {
  const essays = await getEssays();
  return essays.find((e) => e.slug === slug);
}

export async function getSources(): Promise<SourceRecord[]> {
  const sb = getSupabase();
  if (!sb) return [...SAMPLE_SOURCES];
  const { data, error } = await sb.from("sources").select("*");
  if (error) throw error;
  return data as SourceRecord[];
}

export async function getLocalities(): Promise<Locality[]> {
  const sb = getSupabase();
  if (!sb) return [...SAMPLE_LOCALITIES];
  const { data, error } = await sb.from("localities").select("*");
  if (error) throw error;
  return data as Locality[];
}

/** Essays citing a given record — powers the reverse-citation link (D1). */
export async function getEssaysCiting(
  table: "sites" | "entities" | "events",
  id: number,
): Promise<Essay[]> {
  // Demo mode: scan fixture citations. Production: SQL over citations join.
  const essays = await getEssays();
  return essays.filter((e) =>
    e.relatedRecordIds.some((c) => c.recordTable === table && c.recordId === id),
  );
}

export async function getClaimVsRecordPairs(): Promise<ClaimVsRecordPair[]> {
  return [...SAMPLE_CLAIM_VS_RECORD];
}

/** Sites within an LGA (area results view B2, per-LGA pages B4). */
export async function getSitesInLga(lgaCode: string): Promise<Site[]> {
  const sites = await getSites();
  return sites.filter((s) => s.lgaCode === lgaCode);
}
