import { describe, expect, it } from 'vitest';
import { peopleFromPipeline, rolesNamedIn, withholdNames, type Person } from '@/lib/ingestion/people';

// Fictional people only: no real name belongs in a test.
const entityNames = new Map([
  ['ENT_ACME', 'Acme Data'],
  ['ENT_PEAK', 'Peak Body of Australia'],
]);

const people: Person[] = peopleFromPipeline({
  people: [
    { name: 'Avery Quill', aliases: 'Avery Quill MP', role: 'the State Energy Minister' },
    { name: 'Rowan Sterne', aliases: null, role: 'a former Defence Materiel Minister' },
    { name: 'Moss', aliases: 'Chairman Moss', role: "Acme's chairman" },
  ],
  lobbying: [
    { person: 'Jordan Vale, Founder and CEO', actor_id: 'ENT_ACME' },
    { person: 'Casey Black, Executive Director Policy', actor_id: 'ENT_PEAK' },
    { person: 'Morgan Black, Chief Executive', actor_id: 'ENT_PEAK' },
    // The register wins over the lobbying record's long role.
    { person: 'Rowan Sterne, former Minister for Defence Materiel (2013); later a vendor executive', actor_id: 'ENT_ACME' },
    // Recorded by role, no name: nothing to withhold.
    { person: 'Director and Chief Executive Officer, Acme Data (named in a disclosure)', actor_id: 'ENT_ACME' },
  ],
  caseHandling: [
    { officer_name: 'Taylor Penn', officer_role: 'case_planner' },
    { officer_name: 'Sam Orrell', officer_role: 'case_planner' },
    { officer_name: 'Taylor Penn', officer_role: 'delegate_signatory' },
    { officer_name: '[Name of Commissioner]', officer_role: 'determination_authority' },
  ],
  entityNames,
});

const w = (s: string) => withholdNames(s, people);

describe('peopleFromPipeline', () => {
  it('reads the register, the lobbying records and the officers, once each', () => {
    const names = people.map((p) => p.name).sort();
    expect(names).toEqual(
      ['Avery Quill', 'Casey Black', 'Jordan Vale', 'Morgan Black', 'Moss', 'Rowan Sterne', 'Sam Orrell', 'Taylor Penn'].sort(),
    );
  });

  it('labels a lobbying person by role and organisation', () => {
    expect(people.find((p) => p.name === 'Jordan Vale')!.role).toBe('Founder and CEO, Acme Data');
  });

  it('lets the register override a lobbying role', () => {
    expect(people.find((p) => p.name === 'Rowan Sterne')!.role).toBe('a former Defence Materiel Minister');
  });
});

describe('withholdNames', () => {
  it('replaces a name with its role', () => {
    expect(w('Jordan Vale appointed to the board')).toBe('[Founder and CEO, Acme Data] appointed to the board');
  });

  it('withholds the name where the text already states the role', () => {
    expect(w('Acme Founder and CEO Jordan Vale joins the board')).toBe(
      'Acme Founder and CEO [name withheld] joins the board',
    );
    expect(w('Application: Rowan Sterne, former Director General, Defence')).toBe(
      'Application: [name withheld], former Director General, Defence',
    );
  });

  it('takes postnominals and aliases with the name', () => {
    expect(w('Ministry / Avery Quill MP')).toBe('Ministry / [the State Energy Minister]');
    expect(w('The release says Chairman Moss is quoted')).toBe("The release says [Acme's chairman] is quoted");
  });

  it('keeps a possessive readable', () => {
    expect(w("what Rowan Sterne's remit involved")).toBe("what [a former Defence Materiel Minister]'s remit involved");
  });

  it('numbers officers, and follows a surname used alone', () => {
    expect(w("Taylor Penn: n=9. Sam Orrell: n=6. Penn' 9 consents carry more than Orrell's.")).toBe(
      "[NSW planning officer 1]: n=9. [NSW planning officer 2]: n=6. [NSW planning officer 1]'s 9 consents carry more than [NSW planning officer 2]'s.",
    );
  });

  it('does not follow a surname two people in the field share', () => {
    expect(w('Casey Black and Morgan Black both spoke; Black said more')).toBe(
      '[Executive Director Policy, Peak Body of Australia] and [Chief Executive, Peak Body of Australia] both spoke; Black said more',
    );
  });

  it('leaves a surname alone where the full name is not in the field', () => {
    expect(w('24 Penn Circuit, Huntingwood')).toBe('24 Penn Circuit, Huntingwood');
  });

  it('passes text with nobody in it, and null', () => {
    expect(w('The consent was signed in July.')).toBe('The consent was signed in July.');
    expect(withholdNames(null, people)).toBeNull();
  });
});

describe('rolesNamedIn', () => {
  it('finds a listed person by role, never by name', () => {
    expect(rolesNamedIn('Jordan Vale spoke', people)).toEqual(['Founder and CEO, Acme Data']);
  });

  it('finds nobody once the names are withheld', () => {
    const all = 'Jordan Vale, Avery Quill MP, Chairman Moss, Taylor Penn and Rowan Sterne';
    expect(rolesNamedIn(w(all), people)).toEqual([]);
  });
});

describe('officer numbers', () => {
  it('are fixed for the load, by caseload, so a number means the same officer in every field', () => {
    // Taylor Penn has two case records, Sam Orrell one.
    expect(w('Sam Orrell signed it.')).toBe('[NSW planning officer 2] signed it.');
    expect(w('Sam Orrell and Taylor Penn both did')).toBe('[NSW planning officer 2] and [NSW planning officer 1] both did');
  });
});
