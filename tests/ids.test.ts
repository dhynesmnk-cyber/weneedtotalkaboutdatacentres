import { describe, expect, it } from 'vitest';
import { isRecordId } from '@/lib/ids';

describe('isRecordId', () => {
  it('accepts a uuid in either case', () => {
    expect(isRecordId('c778a841-b7ec-5724-9d5b-be47ffec6ebb')).toBe(true);
    expect(isRecordId('C778A841-B7EC-5724-9D5B-BE47FFEC6EBB')).toBe(true);
  });

  it('rejects what Postgres would reject as invalid uuid syntax', () => {
    // Each of these reached the database before the guard and came back as a
    // 500 rather than a 404.
    expect(isRecordId('x')).toBe(false);
    expect(isRecordId('')).toBe(false);
    expect(isRecordId('c778a841b7ec57249d5bbe47ffec6ebb')).toBe(false);
    expect(isRecordId('c778a841-b7ec-5724-9d5b-be47ffec6eb')).toBe(false);
    expect(isRecordId('c778a841-b7ec-5724-9d5b-be47ffec6ebbz')).toBe(false);
    expect(isRecordId(' c778a841-b7ec-5724-9d5b-be47ffec6ebb')).toBe(false);
  });

  it('does not let query syntax through', () => {
    expect(isRecordId('c778a841-b7ec-5724-9d5b-be47ffec6ebb,id.neq.x')).toBe(false);
  });
});
