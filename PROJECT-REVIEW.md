# Project review — weneedtotalkaboutdatacentres

**Reviewed:** 15 November 2026 (Sydney) · **Repo:** `dhynesmnk-cyber/weneedtotalkaboutdatacentres`
**Checked out:** `review/release-1` → `origin/claude/bold-goldberg-0ek4ml` @ `1964bea` (11 Nov)
**Source tree:** unmodified. Only `.artifacts/load-essays.sql` was generated (gitignored).

---

## Update — 15 Nov 02:00 UTC: durable fix shipped as PR #36

**PR #36** (`review/release-1` → `main`): https://github.com/dhynesmnk-cyber/weneedtotalkaboutdatacentres/pull/36 — 9 files, +434/−20.

- `data-pipeline/scrapers/redact.py` — the redaction rules once, shared by `archive_pages.py` and `ingest_nsw_planning.py`. Google browser keys and `token`/`authtoken` page tokens; a base64 triple elsewhere is evidence and is left alone; a PDF's bytes are never rewritten, its extracted text is cleaned.
- `archive_pages.py` — redacts before writing, hashes the stored bytes, records `redacted` and `upstream_sha256`.
- `data-pipeline/scripts/check_secrets.py` — scans the repository, fails on any credential outside the two raised archives. Wired into CI, the Makefile and `rebuild_all.py`.
- `data-pipeline/README.md` and `docs/DEPLOYMENT.md` — the incident, the rule that constrained the fix, and the Netlify safelist.

**The two archives are untouched.** They are hash-verified, so the README rule applies: raised, not redacted. That decision remains the author's.

Verified: both selftests pass; mutation test (plant a key → exit 1, remove → exit 0); `check_packs` OK (27 packs, 26 curation scripts); `export_csv --verify` PASSED (46 files match the database); lint, typecheck, 509 unit tests. Two false positives were found and fixed during development — the portal's `appendix-e-sk-01-…` slugs read as OpenAI keys under a loose pattern.

CI on PR #36: `check` **success**, with the new `Secrets in the repository` and `Redaction fixtures` steps both confirmed run and passed; `rls (17/16)` and `load (17/16)` **success**; `ui` still running (~21 min).

Compatibility with #34: everything auto-merges except two lines of `data-pipeline/Makefile`, where both PRs add a target name. The exact resolution is in the PR description. Semantics checked too — #34's `archive_pages.py --selftest` passes against the merged file, 10/10.

**This does not unblock the current deploy.** It stops the next occurrence. Production still needs either the `SECRETS_SCAN_SMART_DETECTION_OMIT_VALUES` safelist or the author's decision to redact and re-manifest the two archives.

---

## Update — 15 Nov 01:25 UTC: Netlify root cause identified

Netlify reports: **`Production: main@321a3eb failed — Exposed secrets detected. Failed during stage 'building site': Build script returned non-zero exit code: 2`.**

This is Netlify **Secrets Controller smart detection**, which scans "your repository code and build output" — not just the published directory. It is not a problem with Release 1, and not a build-script fault: `npm run build` passes here and in CI.

**What it found** — third-party credentials embedded in archived HTML kept as research evidence:

| File | Added in | Google Maps keys | Page/session tokens |
| --- | --- | --- | --- |
| `data-pipeline/data/raw/councils/penrith/vpa-microsoft-datacenter.html` | Batch 3 (`f1b539e`) | 1 | 2 |
| `data-pipeline/data/raw/nsw_planning/ipc/talavera-road-data-centre-campus-expansion.html` | Batch 5 (`9defdca`) | 3 (same key) | 0 |

Two distinct `AIza…` keys, four occurrences. The keys belong to Penrith's consultation platform and the NSW Independent Planning Commission, embedded in Google Maps `<script src>` tags and a `gmap_api_key` settings block. The Penrith page also carries a `token` and an `authtoken` for that platform. None of it is ours, and none of it is published: Netlify's publish directory is `.next`, and `data-pipeline/` never enters the build.

This matches the timeline exactly: the earliest failing preview we found is Batch 5 (30 Oct), the commit that added the Talavera archive.

**Why it was not caught earlier.** The 18 Sep fix (`4fa2c41`) redacted three portal snapshots and patched `ingest_nsw_planning.py` to redact at archive time. But these two pages were fetched by `scrapers/archive_pages.py`, the general-purpose archiver, which has no redaction. The guard was applied to one scraper, not the shared path.

**The constraint on fixing it.** `data-pipeline/README.md:601` is explicit: *"Where a redaction would touch a hash-verified document, redact nothing — leave the archive intact and raise it instead."* Both files have `.meta.json` manifests with `sha256` and `bytes`. So redacting them is against the project's own rule without the author's decision. This is therefore raised, not silently changed.

**Options, in order of preference:**

1. **Safelist the exact values** (recommended, unblocks now, preserves the archives byte-for-byte). Netlify → Project configuration → Environment variables → add `SECRETS_SCAN_SMART_DETECTION_OMIT_VALUES` with the comma-separated values, all scopes, then Trigger deploy. This is Netlify's documented false-positive path and leaves scanning active for everything else. The exact values are in `netlify-safelist.txt` beside this file.
2. **Redact and re-manifest**, as `4fa2c41` did: replace the keys with the sentinel, update `sha256`/`bytes` to the stored bytes, and record the redaction plus the upstream digest. Defensible — the precedent exists — but it contradicts the README rule for hash-verified documents, so it needs the author's explicit sign-off and a README amendment.
3. **Disable smart detection** (`SECRETS_SCAN_SMART_DETECTION_ENABLED=false`) or all scanning (`SECRETS_SCAN_ENABLED=false`). Not recommended: it loses protection for real secrets, including the service-role key.

**Durable fix, independent of the choice above:** move the redaction into `archive_pages.py` so every future archive is cleaned before it is written, and add a repo-side secret scan to CI so this is caught before Netlify sees it. Neither touches the existing archives.

---

## Update — 15 Nov 01:00 UTC: merged, backup verified, Netlify blocked

**PR #35 merged.** `main` is now `321a3eb` (merge commit, matching the repo's convention). The admin routes, `/about`, `/where-we-stand` and `middleware.ts` are all confirmed present on `main`.

**Weekly backup dispatched and succeeded** (run on `321a3eb`, artefact `backup-43660724150`, 212 KB, taken 00:58 UTC). Manifest verified — **16 tables**, including the three that `main` could not previously see:

| Table | Rows |
| --- | --- |
| `facts.sources` | 284 |
| `facts.sites` | 93 |
| `facts.entities` | 142 |
| `facts.citations` | 622 |
| `facts.data_gaps` | 1,552 |
| `facts.links` | 59 (proposed, hidden from anon) |
| `facts.research_agenda` | 88 |
| `editorial.essays` | 2 (both drafts) |
| `editorial.essay_revisions` | 0 |
| `editorial.approvals` | 0 |
| `editorial.editors` | **0** |

Finding 1 is closed. The 284 sources confirm the 11 Nov research reload, and the two essay rows confirm the drafts are loaded.

**`editorial.editors` is empty.** The allow-list has no row, so nobody can edit yet even once the site deploys. This is step 6a item 3, still outstanding.

**New blocker — Netlify has not published the merge.** Fourteen minutes after the merge, `https://datacentres.netlify.app/admin/sign-in` still returns 404 and the homepage still lacks the new strapline and self-hosted fonts, so production is serving a pre-Release-1 build. The code is on `main`; the deploy is the missing step. Given deploy previews have failed on 30 Oct, 1 Nov and 15 Nov, the likely causes are a failing Netlify build, exhausted build minutes, or a locked/paused publish. Netlify reports no commit status for production deploys, so this is only visible in the Netlify dashboard: **Deploys → latest deploy for `main` → log**.

Until that is resolved, `/admin` cannot be reached and step 6a cannot be completed. The Supabase-side configuration (Site URL, redirect allow-list, invite, allow-list row, SMTP, `SITE_URL`) can all be done now.

---

## Update — 15 Nov: PR #35 opened, CI green

**PR #35** (`claude/bold-goldberg-0ek4ml` → `main`) is open: https://github.com/dhynesmnk-cyber/weneedtotalkaboutdatacentres/pull/35
103 files, +7,882/−560. `mergeable: true`. Every CI job passed:

| Job | Result | Time |
| --- | --- | --- |
| `check` (lint, typecheck, unit, build) | ✔ success | 107s |
| `rls (17)` | ✔ success | 32s |
| `rls (16)` | ✔ success | 29s |
| `load (17)` | ✔ success | 77s |
| `load (16)` | ✔ success | 82s |
| `ui` (browser + axe, 2 widths × light/dark) | ✔ success | 1,256s |

So the editor RLS, the approval refusals, the citation trigger, the idempotent load and WCAG 2.2 AA in both colour schemes are now **proven in CI**, not just read. Finding 2 below is closed. The UI job takes ~21 min rather than the previous ~10 because it now runs four passes instead of two and adds four pages — expected, not a hang.

**New finding — Netlify deploy previews have been broken for weeks.** PR #35's preview failed at 00:31 UTC. It is not Release 1's fault: the same `netlify/datacentres/deploy-preview` failure is recorded on PR #34's head (1 Nov) and on Batch 5 (30 Oct), both of which merged and shipped. `npm ci` from the committed lockfile succeeds here, so it is not lockfile drift.

This is why GitHub reports `mergeable_state: unstable` — CI is green, the failing check is Netlify's. It also means the delivery plan's step "by hand, on a Netlify deploy preview" has been unavailable since at least 30 October, so recent releases went out without that human pass. The log needs a Netlify login: https://app.netlify.com/projects/datacentres/deploys/6af8fd2c6b094d3dd3913dd3

---

## 1. Where the project actually is

The previous session did not lose its work. It is all committed and pushed — but **not to `main`, and not in a pull request.**

| Ref | Date | State |
| --- | --- | --- |
| `main` @ `be055d3` | 30 Oct | v2.7.0. Batches 0–5 merged. CI green. This is what Netlify serves. |
| `claude/bold-goldberg-0ek4ml` @ `1964bea` | 11 Nov | **Release 1, complete.** 5 commits, 103 files, +7,882/−560. No PR ever opened. |
| PR #34 (`claude/adoring-lovelace-da1366`) | 1 Nov | Open, CI green, 13 files, sitting unmerged for two weeks. |

Release 1 contains: the design system and site shell (self-hosted fonts, tokens, dark mode, mobile menu, loading states, sitemap/robots/OG images), the editor's desk at `/admin` (magic-link auth, Markdown editor with live preview, checker panel, save/approve/retract), migrations `0014`–`0017`, essay rendering, the essay checker and loader, `/about`, `/where-we-stand`, and two full drafts (ES-001 "Six in seven", ES-000 "Where we stand").

The commit named "WIP: editor CMS…" is not actually work in progress — the two later commits finish it, and there are no `TODO`/`FIXME` markers left anywhere in `app/`, `lib/`, `components/`, `scripts/` or the migrations.

**The important asymmetry:** the hosted database has already been moved forward, but the deployed code has not.

- Migrations `0014`–`0017` were applied to production on 11 Nov, the research was reloaded (284 sources), and both drafts were loaded **unapproved**.
- `main` has no `/admin`, no `middleware.ts`, and none of the new essay rendering. So the author currently **cannot sign in or approve anything on the live site**, and the drafts sit invisible.

Both branches merge cleanly, and Release 1 is a fast-forward on `main` (`main` is an ancestor). Nothing needs untangling.

---

## 2. What I verified locally

| Check | Result |
| --- | --- |
| `npm run lint` | ✔ No warnings or errors |
| `npm run typecheck` | ✔ Clean |
| `npm test` (Node 22) | ✔ **509 tests, 30 files, all pass** |
| `npm test` (Node 20) | ✘ 2 suites fail to load — see finding 4 |
| `npm run build` (no credentials) | ✔ 23 routes, middleware 86.9 kB |
| `npm run check:essays` | ✔ Both drafts pass the essay rules |
| `npm run load:essays` | ✔ Emits reviewable SQL; skips rows edited in admin; rolls back if a draft does not land unapproved |
| Every public route | ✔ 200 on `/`, `/map`, `/list`, `/coverage`, `/research`, `/essays`, `/about`, `/where-we-stand`, `/how-to-read`, `/robots.txt`, `/sitemap.xml` |
| Empty states | ✔ "The record is unavailable right now… Nothing has been put in their place." No sample figures anywhere |
| Malformed id (`/sites/not-a-uuid`) | ✔ No 500 |
| `/admin` when signed out | ✔ Redirects to `/admin/sign-in`; `robots.txt` disallows `/admin` |

**What I could not verify:** `npm run test:rls`, `test:load` and `test:ui`. They need Docker/Postgres, which this sandbox does not have. That matters more than usual — those are precisely the suites that prove the new editor permissions, and **they have never run in CI for this branch, because no PR was opened.** The last CI runs are on `main` and on the research branch only.

I read the security-critical SQL instead (see §5). It is sound, but reading is not testing.

---

## 3. Findings, in priority order

### 1. The weekly backup will not capture the new tables — and it runs in about 19 hours

`.github/workflows/backup.yml` runs on `main` at **19:00 UTC Sunday** (06:00 Monday Sydney). Last run: 8 Nov, *before* the migrations. Next run: **Sunday 15 Nov, 19:00 UTC**.

`main`'s backup catalogue lists 13 tables. Production now has 16. Missing from `main`: `editorial.editors`, `editorial.approvals`, `editorial.essay_revisions`.

The export has a live cross-check (`scripts/backup/export-database.ts:84-101`) that reads the database's table list and **fails loudly** when it finds an uncovered table. So the likely outcome is a failed job and no backup that week. The weaker path: if that service-role endpoint cannot be read, it warns and continues, producing a backup with three tables silently absent.

The primary guard cannot catch this on `main`: `tests/backup/tables.test.ts` compares the catalogue against a **hardcoded list of four migration filenames**, so it cannot see `0014`–`0017` at all.

Release 1 already fixes both halves — it adds the three tables with `recoverability: 'curated'`, and replaces the hardcoded list with a directory glob. The `service_role` SELECT grants for the new tables are also already in `0014`/`0015`. **Merging is the fix.**

What is at risk is not the essay text (`editorial.essays` is covered on `main`) but the revision history, the publication audit trail, and the editor allow-list — the three things that exist nowhere else and cannot be rebuilt by any loader.

### 2. Release 1 has never been through CI — **closed 15 Nov**

PR #35 triggered the full set and all six jobs passed, including RLS on both Postgres versions and the browser/axe suite in light and dark. Kept here for the record: the gap was real, and it existed because no PR had been opened.

### 3. Production schema is ahead of deployed code

Consequences while this persists: the author cannot approve the drafts; `/where-we-stand` and `/about` do not exist on the live site; and `main`'s migration set still carries the old `citations_public_read using (true)` policy. Production is already fixed by `0016`, but any database rebuilt from `main` — a `test:load` run, a disaster-recovery restore — reintroduces the leak where citation rows of unapproved essays are publicly readable. Merging closes the drift in both directions.

### 4. Node 22 is required but declared nowhere

`tests/essayFile.test.ts` and `tests/storyCards.test.ts` require `node:sqlite`, which is Node 22+. On Node 20 `npm test` fails with `No such built-in module: node:sqlite` — a confusing first experience for anyone picking this up. CI and Netlify both pin 22, so this is a local-developer gap only. `package.json` has no `engines` field and there is no `.nvmrc`. Three-line fix.

### 5. Documentation drift (small, but the project's own definition of done requires it)

- `docs/SUPABASE_SETUP.md` still says "There are **thirteen** migrations" in the body, while its own status header correctly says seventeen.
- `docs/RESEARCH-PLAN.md` quotes 14 resolved / 16 in progress / 64 open. The pipeline actually holds **20 resolved / 42 in progress / 32 open** (94 total). Release 2 already lists this correction.

### 6. Research is blocked on a human, not on an agent

Every agent-available batch (0–5) is done. 32 questions are open and 42 in progress; the next movement needs the **21 free browser downloads** in `docs/requests/DOWNLOADS.md` — the author chose no FOI, GIPA or paid searches for now. Upstream is in good order: 93 sites, 142 entities, 284 sources, 31 lobbying rows, 19 story cards. PR #34 is a small, green, clean-merging research batch that has been waiting two weeks.

---

## 4. Recommended next steps

**Step 1 — today, before 19:00 UTC Sunday.** Open the Release 1 PR into `main` and let CI run the full suite set. Review it in the four areas the plan already divides it into (shell/tokens; migrations `0014`–`0017`; rendering/checker/loader; content). Merge on green — it fast-forwards. A ready-to-paste PR description is in `PR-RELEASE-1.md`.

If CI cannot finish before the cron, either trigger **Weekly backup → Run workflow** manually *after* the merge, or accept one failed run and re-dispatch. Do not let the week pass with no backup of the editorial tables.

**Step 2 — the author, about 30 minutes.** `docs/SUPABASE_SETUP.md` step 6a, in order: invite yourself in Supabase Auth; insert your address into `editorial.editors`; set the Site URL and the `/admin/auth/callback` redirect URLs (including the deploy-preview wildcard); configure custom SMTP; set `SITE_URL` on Netlify; then `npm run load:essays`, read `.artifacts/load-essays.sql`, apply it. Steps 1–2 of that list (reload research, apply migrations) are already done.

**Step 3 — verify the safety net.** Dispatch the backup once by hand, then `npm run backup:verify` on the artefact, and confirm the manifest lists 16 tables including the three new ones.

**Step 4 — publish something.** Read, edit and approve ES-001 "Six in seven" at `/admin`, then ES-000. This is the point where the project stops being a scaffold and becomes the resource the plan describes. The flagship essay is well chosen: an industry-commissioned figure reaching the NSW guidelines without disclosure, all parties institutional, eight sources, no downloads needed.

**Step 5 — clear the queue.** Merge PR #34. Then start Release 2 (CSV exports and `/data` for journalists, plus working the downloads as they arrive).

**Hygiene, any time:** add `engines`/`.nvmrc` for Node 22; fix the two stale doc passages.

I have no push credentials in this sandbox, so steps 1 and 5 need you (or a token). Everything else I can do here.

---

## 5. Judgement on the work itself

This is unusually disciplined code, and the hard rules in `CLAUDE.md` are enforced where it counts — in the database, not in the application.

What I checked by reading:

- **Approval cannot be forged.** `editorial.approve_essay` is `SECURITY DEFINER` with `search_path = ''`, takes the approver from the signed-in token (no approver argument), and `EXECUTE` is granted to `authenticated` only — explicitly revoked from `anon` and `service_role`. No agent can publish.
- **Approval is gated on substance:** row unchanged since the editor opened it (optimistic lock), a publish date, a `data_as_of_date`, non-empty body, ≥5 distinct cited sources, an `## Our view` / `## Our proposal` heading so opinion sits after the divider, and a legal acknowledgement when `named_parties` is non-empty. Column-level UPDATE grants exclude `approved_*`.
- **Citations are derived, not asserted.** A trigger extracts `[SRC_*]` markers, resolves them against `facts.sources`, and rejects the save on any unknown id. `0016` also closes the pre-existing leak so editorial citations are visible only when their parent record is.
- **Audit and recovery:** every update snapshots the body into `essay_revisions`; every approval/retraction is logged with the actor and a body hash; all three new tables are classified irreplaceable in the backup catalogue.
- **Conflict of interest is handled, not hidden.** The drafting agent is made by Anthropic, which is the Western Downs tenant (ST-016, RG-012); `/about` carries a standing disclosure and the checker enforces it on any piece touching those records.
- **People stay out.** Roles only, until legal review. The loader publishes neither `lobbying.person` nor `notes`.
- **The empty states are honest.** With no database the site says the record is unavailable and puts nothing in its place.

Things to keep an eye on, none blocking:

1. **One editor, no break-glass.** The allow-list is a single row inserted by hand. If that address becomes unreachable there is no second approver and no documented recovery path. Worth a line in `docs/DEPLOYMENT.md`.
2. **Magic-link requests** rely on Supabase's own rate limits; there is no application-level throttle on `/admin/sign-in`. The reply is uniform, so it cannot be used to enumerate editors — good.
3. **Fonts** ship via `@fontsource` packages rather than the committed `app/fonts/` files the plan described. Fine (the build still fetches nothing), but the OFL licences now live in `node_modules` rather than the repo.
4. **`node:sqlite` is experimental** in Node 22 and prints a warning on every checker/test run. Harmless today, worth pinning an eye on at the next Node upgrade.

---

## 6. Running it here

The production build is serving on **port 3000** (live preview). Use the production server, not `npm run dev`: this sandbox is capped at 1 GB and the dev server was OOM-killed compiling the Leaflet map route. The production build is stable and every route returns 200.

```bash
cd weneedtotalkaboutdatacentres
export PATH=/tmp/n22/node-v22.14.0-linux-x64/bin:$PATH   # Node 22, needed for node:sqlite
npm run lint && npm run typecheck && npm test
npm run check:essays
npx next start -H 0.0.0.0 -p 3000
```

Without `.env.local` every page shows the honest "record unavailable" state, so the preview shows the new shell, typography, navigation and dark mode — not the loaded records. To see real data, add the Supabase keys.

`test:rls`, `test:load` and `test:ui` need Docker and Postgres; run them in CI.