import { SignInForm } from '@/components/admin/SignInForm';
import { isAuthConfigured } from '@/lib/admin';

export const dynamic = 'force-dynamic';
export const metadata = { title: 'Sign in' };

export default function SignInPage({ searchParams }: { searchParams: { failed?: string } }) {
  return (
    <div className="space-y-4">
      <h1 className="page-title">Sign in</h1>
      <p className="max-w-xl text-slate-700">
        Sign-in is by emailed link, for the site&rsquo;s editor only. There is no
        public account and no password.
      </p>
      {searchParams.failed && (
        <p role="alert" className="max-w-xl text-sm text-defect-ink">
          That link did not work. It may have expired or been used already. Ask for a new one.
        </p>
      )}
      {isAuthConfigured() ? (
        <SignInForm />
      ) : (
        <p className="text-slate-700">Sign-in is not configured for this deployment.</p>
      )}
    </div>
  );
}
