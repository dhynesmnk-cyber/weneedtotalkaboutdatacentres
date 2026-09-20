import { describe, expect, it } from 'vitest';
import { OBSERVATORY_NAMESPACE, pipelineUuid, uuidV5 } from '@/lib/ingestion/identity';

describe('uuidV5', () => {
  it('matches the RFC 4122 worked example', () => {
    // The DNS namespace and "www.example.org" from the spec's own test vector,
    // so a bug in the bit-twiddling is caught against an external authority
    // rather than against our own output.
    expect(uuidV5('www.example.org', '6ba7b810-9dad-11d1-80b4-00c04fd430c8')).toBe(
      '74738ff5-5367-5958-9aee-98fffdcd1876',
    );
  });

  it('sets the version and variant bits', () => {
    const uuid = uuidV5('anything');
    expect(uuid[14]).toBe('5');
    expect(['8', '9', 'a', 'b']).toContain(uuid[19]);
  });

  it('is stable across calls', () => {
    expect(uuidV5('x')).toBe(uuidV5('x'));
  });
});

describe('pipelineUuid', () => {
  // Golden values. These pin the namespace constant: changing it silently
  // re-keys every record in the database, and this is what makes that
  // impossible to do by accident.
  it('derives the pinned uuid for a known site', () => {
    expect(pipelineUuid('sites', 'SITE_MSFT_KEMPS')).toBe(
      'e3246d0c-0e80-54fd-b176-4c315e2906af',
    );
  });

  it('derives the pinned uuid for a known entity and source', () => {
    expect(pipelineUuid('entities', 'ENT_ACME')).toBe('2579b6cd-f7d7-5468-a2f2-d7f404cc75f5');
    expect(pipelineUuid('sources', 'SRC_TEST')).toBe('cb865c9d-4177-5919-90d8-e188925d8983');
  });

  it('pins the namespace itself', () => {
    expect(OBSERVATORY_NAMESPACE).toBe('6f9619ff-8b86-d011-b42d-00c04fc964ff');
  });

  it('separates the tables, so a shared natural key is not a collision', () => {
    expect(pipelineUuid('sites', 'X')).not.toBe(pipelineUuid('entities', 'X'));
  });

  it('refuses an empty id rather than returning a constant uuid', () => {
    expect(() => pipelineUuid('sites', '')).toThrow();
  });
});
