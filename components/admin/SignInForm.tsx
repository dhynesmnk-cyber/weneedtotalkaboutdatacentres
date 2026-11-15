'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { signInAction, type SignInState } from '@/app/admin/actions';

function Submit() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="min-h-11 rounded bg-fact-ink px-4 font-medium text-white disabled:opacity-60"
    >
      {pending ? 'Sending…' : 'Email me a sign-in link'}
    </button>
  );
}

export function SignInForm() {
  const [state, action] = useFormState<SignInState, FormData>(signInAction, { sent: false });

  if (state.sent) {
    return (
      <p role="status" className="max-w-xl rounded border border-slate-200 p-4 text-slate-800">
        If that address may edit this site, a sign-in link is on its way. It works once and
        expires within the hour.
      </p>
    );
  }

  return (
    <form action={action} className="max-w-md space-y-3">
      <label className="block text-sm font-medium text-slate-900" htmlFor="email">
        Email
      </label>
      <input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        required
        className="block w-full rounded border border-slate-500 bg-white px-3 py-2 text-slate-900"
      />
      {state.message && (
        <p role="alert" className="text-sm text-defect-ink">
          {state.message}
        </p>
      )}
      <Submit />
    </form>
  );
}
