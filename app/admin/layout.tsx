import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: { default: 'Editor', template: '%s · Editor' },
  robots: { index: false, follow: false },
};

/**
 * The editor's desk. Private: middleware turns away anyone not signed in, each
 * page asks the database whether the signed-in person may edit, and row level
 * security refuses every write that is not the editor's.
 */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-8">
      <p className="rounded border border-editorial-edge bg-editorial-wash px-3 py-2 text-sm text-editorial-ink">
        <strong className="font-semibold">Editor&rsquo;s desk.</strong> Private. Nothing here is
        public until you approve it, and nothing is approved by anyone but you.
      </p>
      {children}
    </div>
  );
}
