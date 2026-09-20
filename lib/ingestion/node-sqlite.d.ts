/**
 * Minimal declarations for node:sqlite.
 *
 * Node 22 ships the module but @types/node ^20 does not describe it. Only the
 * surface this loader uses is declared, so an unused corner of the API cannot
 * be called by accident on the strength of a type that was never checked.
 */
declare module 'node:sqlite' {
  export class DatabaseSync {
    constructor(path: string, options?: { readOnly?: boolean });
    prepare(sql: string): { all(...params: unknown[]): unknown[] };
    close(): void;
  }
}
