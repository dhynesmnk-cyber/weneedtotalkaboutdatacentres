'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useId, useState } from 'react';
import { ariaCurrent, NAV_GROUPS } from '@/lib/nav';

const GROUP_INK = {
  record: 'text-fact-ink',
  analysis: 'text-editorial-ink',
} as const;

/**
 * Primary navigation, in two labelled groups: the record and the analysis.
 *
 * On narrow screens the links fold behind a Menu button. The fold happens only
 * once the page is interactive, so without JavaScript every link is still
 * shown, wrapped, rather than hidden behind a button that cannot open.
 */
export function PrimaryNav() {
  const pathname = usePathname();
  const listId = useId();
  const [enhanced, setEnhanced] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => setEnhanced(true), []);
  // Following a link closes the menu.
  useEffect(() => setOpen(false), [pathname]);

  const folded = enhanced && !open;

  return (
    <nav aria-label="Primary" className="md:mt-0">
      {enhanced && (
        <button
          type="button"
          aria-expanded={open}
          aria-controls={listId}
          onClick={() => setOpen((o) => !o)}
          className="inline-flex min-h-11 items-center gap-2 rounded border border-slate-500 px-3
                     text-sm font-medium text-slate-900 md:hidden"
        >
          <span aria-hidden="true" className="text-base leading-none">
            {open ? '×' : '≡'}
          </span>
          Menu
        </button>
      )}

      <div
        id={listId}
        className={`${folded ? 'hidden' : 'flex'} mt-3 flex-col gap-4 md:mt-0 md:flex md:flex-row md:items-baseline md:gap-8`}
      >
        {NAV_GROUPS.map((group) => (
          <div key={group.id} className="md:flex md:items-baseline md:gap-4">
            <p
              id={`${listId}-${group.id}`}
              className={`kicker ${GROUP_INK[group.id]} mb-1 md:mb-0`}
            >
              {group.label}
            </p>
            <ul
              aria-labelledby={`${listId}-${group.id}`}
              className="flex flex-col md:flex-row md:flex-wrap md:gap-x-4"
            >
              {group.items.map((item) => {
                const current = ariaCurrent(item.href, pathname);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={current}
                      className={`flex min-h-11 items-center rounded text-sm md:min-h-0 md:py-1 ${
                        current
                          ? 'font-semibold text-slate-900 underline decoration-2 underline-offset-[6px]'
                          : 'text-slate-700 underline-offset-[6px] hover:text-slate-900 hover:underline'
                      }`}
                    >
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </nav>
  );
}
