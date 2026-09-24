'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

// docs/SPEC.md's entry-point order, then the coverage view.
const NAV = [
  { href: '/', label: 'Overview' },
  { href: '/essays', label: 'Essays' },
  { href: '/map', label: 'Map' },
  { href: '/list', label: 'Sites and entities' },
  { href: '/coverage', label: 'Coverage' },
] as const;

/** A section is current on its own page and on the records beneath it. */
function isCurrent(href: string, pathname: string): boolean {
  if (href === '/') return pathname === '/';
  if (href === '/list') {
    return ['/list', '/sites', '/entities'].some(
      (p) => pathname === p || pathname.startsWith(`${p}/`),
    );
  }
  if (href === '/essays') {
    return ['/essays', '/case-studies'].some(
      (p) => pathname === p || pathname.startsWith(`${p}/`),
    );
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

/**
 * Primary navigation, marking where the reader is.
 *
 * `aria-current="page"` is set only on an exact match: on a site record the
 * index link is marked "location" instead, because the reader is inside that
 * section but not on its page.
 */
export function PrimaryNav() {
  const pathname = usePathname();

  return (
    <nav aria-label="Primary" className="mt-3">
      <ul className="flex flex-wrap gap-x-5 gap-y-1 text-sm">
        {NAV.map((item) => {
          const current = isCurrent(item.href, pathname);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={current ? (pathname === item.href ? 'page' : 'location') : undefined}
                className={
                  current
                    ? 'rounded font-semibold text-fact-ink underline decoration-2 underline-offset-4'
                    : 'rounded text-slate-700 underline-offset-4 hover:underline'
                }
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
