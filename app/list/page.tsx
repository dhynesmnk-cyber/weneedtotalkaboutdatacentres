import Link from 'next/link';
import { aliasMap, listLgaAliases, resolveLga } from '@/lib/councils';
import { listSites } from '@/lib/sites';
import { listEntities } from '@/lib/entities';
import { isConfigured } from '@/lib/supabase/server';
import { NotConnected, NothingRecorded } from '@/components/NotConnected';
import { formatMw, formatSiteStatus } from '@/lib/format';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Sites and entities' };

/** Sortable index of sites and entities. Fourth entry point in docs/SPEC.md. */
export default async function ListPage() {
  const [sites, entities, aliases] = await Promise.all([
    listSites(),
    listEntities({ majorOnly: true }),
    listLgaAliases(),
  ]);
  // Council names are shown in the spelling a human approved, so one council
  // reads as one council. The stored value is untouched; the site record page
  // shows it, and facts.lga_aliases is published so a reader can check every
  // equivalence and who approved it.
  const councils = aliasMap(aliases);

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Sites and entities</h1>
        <p className="mt-2 max-w-2xl text-slate-700">
          The full index. Entity profiles are published only for entities flagged
          as major by public prominence.
        </p>
      </div>

      {!isConfigured() ? (
        <NotConnected what="sites or entities" />
      ) : (
        <>
          <section aria-labelledby="sites-heading">
            <h2 id="sites-heading" className="text-lg font-semibold text-slate-900">
              Sites
            </h2>

            {sites.length === 0 ? (
              <div className="mt-3">
                <NothingRecorded what="sites" />
              </div>
            ) : (
              <div className="mt-3 overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <caption className="sr-only">
                    Data centre sites with operator, status, capacity and council.
                    Council names are shown in their approved spelling; each
                    site&rsquo;s record page shows the spelling as recorded.
                  </caption>
                  <thead>
                    <tr className="border-b border-slate-300 text-left">
                      <th scope="col" className="py-2 pr-4 font-semibold">Name</th>
                      <th scope="col" className="py-2 pr-4 font-semibold">Operator</th>
                      <th scope="col" className="py-2 pr-4 font-semibold">Status</th>
                      <th scope="col" className="py-2 pr-4 font-semibold">Capacity</th>
                      <th scope="col" className="py-2 font-semibold">Council</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sites.map((site) => (
                      <tr key={site.id} className="border-b border-slate-200">
                        <th scope="row" className="py-2 pr-4 text-left font-medium">
                          <Link
                            href={`/sites/${site.id}`}
                            className="text-fact-ink underline underline-offset-2"
                          >
                            {site.name}
                          </Link>
                        </th>
                        <Cell value={site.operator} />
                        <Cell value={formatSiteStatus(site.status)} />
                        <Cell value={formatMw(site.total_capacity_mw)} />
                        <Cell value={resolveLga(site.lga, councils)?.display ?? null} last />
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section aria-labelledby="entities-heading">
            <h2 id="entities-heading" className="text-lg font-semibold text-slate-900">
              Major entities
            </h2>

            {entities.length === 0 ? (
              <div className="mt-3">
                <NothingRecorded what="major entities" />
              </div>
            ) : (
              <ul className="mt-3 divide-y divide-slate-200 rounded-lg border border-slate-200">
                {entities.map((entity) => (
                  <li key={entity.id} className="px-4 py-3">
                    <Link
                      href={`/entities/${entity.id}`}
                      className="font-medium text-fact-ink underline underline-offset-2"
                    >
                      {entity.name}
                    </Link>
                    <p className="text-sm text-slate-700">
                      {[entity.type, entity.role].filter(Boolean).join(' · ') ||
                        'No type or role recorded'}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function Cell({ value, last = false }: { value: string | null; last?: boolean }) {
  return (
    <td className={last ? 'py-2' : 'py-2 pr-4'}>
      {value ?? <span className="italic text-slate-500">Not recorded</span>}
    </td>
  );
}
