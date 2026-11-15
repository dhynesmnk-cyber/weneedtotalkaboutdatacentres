/**
 * The site's navigation, grouped by layer.
 *
 * The record and the analysis are kept apart in the data and on the page
 * (CLAUDE.md), so they are kept apart in the navigation too: a reader always
 * knows which layer a link leads into. The masthead links to the overview,
 * which introduces both.
 */

export type NavItem = { href: string; label: string };
export type NavGroup = { id: 'record' | 'analysis'; label: string; items: readonly NavItem[] };

export const NAV_GROUPS: readonly NavGroup[] = [
  {
    id: 'record',
    label: 'The record',
    items: [
      { href: '/map', label: 'Map' },
      { href: '/list', label: 'Sites and entities' },
      { href: '/coverage', label: 'What’s known' },
      { href: '/research', label: 'Open questions' },
    ],
  },
  {
    id: 'analysis',
    label: 'Analysis',
    items: [{ href: '/essays', label: 'Essays' }],
  },
];

/** Paths that belong to a section without being its page. */
const SECTION_CHILDREN: Record<string, readonly string[]> = {
  '/list': ['/list', '/sites', '/entities'],
  '/essays': ['/essays', '/case-studies'],
};

function within(pathname: string, prefix: string): boolean {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

/** A section is current on its own page and on the records beneath it. */
export function isCurrent(href: string, pathname: string): boolean {
  if (href === '/') return pathname === '/';
  const prefixes = SECTION_CHILDREN[href] ?? [href];
  return prefixes.some((p) => within(pathname, p));
}

/**
 * `aria-current` for a link: "page" on an exact match, "location" when the
 * reader is inside the section but not on its page (a site record under the
 * index, for instance), and nothing otherwise.
 */
export function ariaCurrent(href: string, pathname: string): 'page' | 'location' | undefined {
  if (!isCurrent(href, pathname)) return undefined;
  return pathname === href ? 'page' : 'location';
}
