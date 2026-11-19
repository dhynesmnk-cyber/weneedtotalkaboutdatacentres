# PR: Release 1 — site shell, editor's desk, essays

Ready to paste into `gh pr create` for `claude/bold-goldberg-0ek4ml` → `main`.

**Title:** Release 1: site shell, the editor's desk, and the first two essays

---

## Why

The observatory is built and loaded but looks like a scaffold, has nowhere to write or publish essays, and shows developer setup text to the public. This is Release 1 of `docs/DELIVERY-PLAN.md`: the foundation and the first essay, from the author's answers to the ten scoping questions (10 Nov).

Migrations `0014`–`0017` were applied to the hosted database on 11 Nov and both drafts were loaded unapproved. **The database is therefore already ahead of `main`.** This PR brings the code up to the schema that is actually serving.

## What is in it

**Design system and shell** — self-hosted Newsreader, Inter and IBM Plex Mono; `lib/design/tokens.ts` as the single source of tokens, exposed as CSS variables with `darkMode: 'media'`; `Container`, `PageHeader`, `EventItem` (replacing three copies), `FieldList`, `Breadcrumb`, `EmptyStateMessage`; a two-group navigation that separates the record from the analysis; a disclosure menu below `md` with 44px targets; `loading.tsx` on the heavy routes; icon, OG images, `robots.ts` (disallowing `/admin`) and `sitemap.ts`. `NotConnected` now tells the public the record is temporarily unavailable and shows setup steps only in development.

**The editor's desk** — `0014` editor allow-list, `is_editor()` and the approvals log; `0015` essay fields, `data_as_of_date`, provenance and `essay_revisions`; `0016` the citation trigger and the fix for the existing `citations_public_read` leak; `0017` editor RLS, `approve_essay` and `retract_essay`. Magic-link sign-in with `shouldCreateUser:false`, cookie-based `@supabase/ssr` (no browser client), `middleware.ts` as an early turn-away with the database as the real authority, `noindex`/`no-store` on every admin page. `/admin` lists drafts; `/admin/essays/[id]` edits Markdown with a live preview, runs the checker, and saves, approves or retracts.

**Rendering, checker, loader** — `react-markdown` + `remark-gfm` with raw HTML off; shared rules in `lib/editorial/rules.ts` (cited sources match the markers, story card and question ids exist, conflict disclosure where ST-016/RG-012/Anthropic is touched, a name screen drawn at check time from the pipeline and never committed as a list); `npm run check:essays` and `npm run load:essays`, which emit a reviewed artefact of draft rows only, skip anything the editor has touched, and roll back if a row would not land unapproved.

**Content** — ES-001 "Six in seven" (eight sources, institutions only, people by role) and ES-000 "Where we stand", both drafts; `/about` with the method, the standing Anthropic disclosure and corrections.

## Hard rules

No agent publishes. Approval is a `SECURITY DEFINER` database function that takes the approver from the signed-in token, accepts no approver argument, and cannot be executed by `anon` or `service_role`. The column-level UPDATE grant excludes `approved_*`. An essay needs five distinct cited sources, a `data_as_of_date`, and an `## Our view` heading so the argument sits after the divider; naming people requires a legal acknowledgement. Citations are derived by trigger and an unknown `SRC_` id rejects the save. `person` and `notes` are never published.

Rule changes the author chose are recorded in `docs/SUBAGENTS.md`, `docs/UX.md` and `docs/UX-PLAN.md`: agents draft in full, only the author approves. `enable_signup=false` stays; the one editor is invited.

## Also fixes

- The weekly backup against the migrated database. `lib/backup/tables.ts` gains `editorial.editors`, `editorial.approvals` and `editorial.essay_revisions`, all classified irreplaceable; without this the export's live cross-check fails on the uncovered tables. `tests/backup/tables.test.ts` now reads every migration in the directory instead of a hardcoded list of four, which is why the guard could not see `0014`–`0017`.
- The public reading of citation rows belonging to unapproved essays (`0004`'s `using (true)`).

## Verification

Run locally on Node 22: `lint` clean, `typecheck` clean, **509 unit tests pass**, `build` succeeds with no credentials (23 routes), `check:essays` passes both drafts, `load:essays` emits the artefact with its rollback assertion. Every public route returns 200 with honest empty states when no database is connected; a malformed id does not 500; `/admin` redirects when signed out.

**This branch has not been through CI.** The suites that matter here are the ones that need Postgres and a browser, and they must go green before merge:

- `test:rls` on Postgres 17 and 16 — anon cannot read a draft's citations; a non-editor cannot read, update or approve; the editor gets `42501` writing `approved_by`, cannot edit an approved row, and is refused approval under five sources; `service_role` cannot execute `approve_essay`; the trigger rejects an unknown `SRC_` id.
- `test:load` — drafts stay unapproved, citations are derived, rows edited in admin are skipped, the load stays idempotent.
- `test:ui` — `/about`, `/where-we-stand`, `/admin/sign-in`; axe in light and dark.

The whole editor loop (emailed link, non-editor refused, edit, approve, publish, retract) was run end to end against a local Supabase stack before the commit.

## After merge — the author's steps

`docs/SUPABASE_SETUP.md` step 6a. The research reload and the migrations are done. What remains: invite yourself in Auth; add your address to `editorial.editors`; allow the Site URL and `/admin/auth/callback` redirect URLs; set up SMTP; set `SITE_URL` on Netlify; `npm run load:essays`, review, apply; then read, edit and approve at `/admin`.

Then dispatch **Weekly backup** once by hand and check the manifest lists all sixteen tables.

## Known gaps, not blocking

`engines`/`.nvmrc` for Node 22 are still missing, so `npm test` fails two suites on Node 20 (`node:sqlite`). `docs/SUPABASE_SETUP.md` still says "thirteen migrations" in its body, and `docs/RESEARCH-PLAN.md` quotes stale counts (actual: 20 resolved / 42 in progress / 32 open). Small follow-up PR.