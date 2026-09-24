/**
 * Record identifiers.
 *
 * Every record's id is a Postgres uuid. An id taken from a URL is untrusted
 * input: passed to Postgres as-is, a malformed one is rejected as invalid
 * syntax, the query errors, and the reader gets a 500 for what is really a
 * page that does not exist. Getters check the shape first and answer "no such
 * record" instead.
 */

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isRecordId(value: string): boolean {
  return UUID.test(value);
}
