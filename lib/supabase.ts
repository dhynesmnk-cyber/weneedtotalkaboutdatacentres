// lib/supabase.ts
// Single typed data-access entry point (CLAUDE.md convention: all database
// access through /lib; no raw SQL in components). Public reads only — Row
// Level Security enforces that. If Supabase env vars are absent the client is
// null and callers fall back to the curated sample dataset, so the site runs
// locally with zero infrastructure.

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let cached: SupabaseClient | null | undefined;

export function getSupabase(): SupabaseClient | null {
  if (cached !== undefined) return cached;
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  cached = url && anonKey ? createClient(url, anonKey) : null;
  return cached;
}

export const isDatabaseConfigured = (): boolean => getSupabase() !== null;
