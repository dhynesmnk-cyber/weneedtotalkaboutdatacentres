import { describe, expect, it } from 'vitest';
import {
  DEFAULT_RECORD_CACHE_SECONDS,
  recordCacheSeconds,
  recordFetchPolicy,
  RECORD_CACHE_TAG,
} from '@/lib/supabase/cachePolicy';

describe('recordCacheSeconds', () => {
  it('defaults to five minutes when unset or blank', () => {
    expect(DEFAULT_RECORD_CACHE_SECONDS).toBe(300);
    expect(recordCacheSeconds(undefined)).toBe(300);
    expect(recordCacheSeconds(' ')).toBe(300);
  });

  it('reads a whole number of seconds, including zero', () => {
    expect(recordCacheSeconds('60')).toBe(60);
    expect(recordCacheSeconds('0')).toBe(0);
  });

  it('falls back to the default rather than to "forever" or "never"', () => {
    expect(recordCacheSeconds('-1')).toBe(300);
    expect(recordCacheSeconds('1.5')).toBe(300);
    expect(recordCacheSeconds('ten')).toBe(300);
  });
});

describe('recordFetchPolicy', () => {
  it('always states a lifetime, so the framework default never applies', () => {
    expect(recordFetchPolicy(300)).toEqual({
      next: { revalidate: 300, tags: [RECORD_CACHE_TAG] },
    });
  });

  it('turns caching off at zero', () => {
    expect(recordFetchPolicy(0)).toEqual({ cache: 'no-store' });
  });
});
