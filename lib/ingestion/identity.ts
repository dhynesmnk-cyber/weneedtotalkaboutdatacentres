/**
 * Deterministic identity for rows that originate in the curation pipeline.
 *
 * The pipeline keys records with readable natural keys; this database keys on
 * uuid. Deriving the uuid from the natural key rather than letting the database
 * assign one buys three things:
 *
 *   1. A load run twice produces identical output, so the emitted SQL is
 *      diffable and a golden test over it means something.
 *   2. Citations and gaps can reference a site by uuid literal, keeping the
 *      emitted SQL flat and readable instead of a thicket of subqueries.
 *   3. The local verification database and the eventual hosted one hold the
 *      same uuids, so a URL captured while checking locally still resolves.
 *
 * UUIDv5 (RFC 4122 s4.3): SHA-1 over namespace + name, with the version and
 * variant bits forced.
 */

import { createHash } from 'node:crypto';

/**
 * Namespace for this project's derived identifiers.
 *
 * Changing this value silently re-keys every record in the database. The golden
 * test in tests/ingestion/identity.test.ts exists to make that impossible to do
 * by accident.
 */
export const OBSERVATORY_NAMESPACE = '6f9619ff-8b86-d011-b42d-00c04fc964ff';

function uuidToBytes(uuid: string): Buffer {
  return Buffer.from(uuid.replace(/-/g, ''), 'hex');
}

/** UUIDv5 of `name` within `namespace`. */
export function uuidV5(name: string, namespace = OBSERVATORY_NAMESPACE): string {
  const hash = createHash('sha1')
    .update(uuidToBytes(namespace))
    .update(Buffer.from(name, 'utf8'))
    .digest();

  const bytes = Buffer.from(hash.subarray(0, 16));
  bytes[6] = ((bytes[6] as number) & 0x0f) | 0x50; // version 5
  bytes[8] = ((bytes[8] as number) & 0x3f) | 0x80; // RFC 4122 variant

  const hex = bytes.toString('hex');
  return [
    hex.slice(0, 8),
    hex.slice(8, 12),
    hex.slice(12, 16),
    hex.slice(16, 20),
    hex.slice(20, 32),
  ].join('-');
}

/**
 * The uuid for a pipeline record.
 *
 * The table name is part of the name, so a site and an entity that happened to
 * share a natural key would still get different uuids.
 */
export function pipelineUuid(table: string, pipelineId: string): string {
  if (!pipelineId) throw new Error(`Cannot derive a uuid from an empty ${table} id`);
  return uuidV5(`${table}:${pipelineId}`);
}
