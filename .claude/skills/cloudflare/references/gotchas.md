# Cloudflare platform gotchas (hard-won, from real projects)

Read this when debugging deploys, secrets, email, Pages weirdness — and before choosing Pages for a new project.

## Pages Functions limitations (reasons to prefer a real Worker)

- **No Cron Triggers.** A scheduled job in a Pages repo must be a standalone Worker (`workers/<name>/` with its own wrangler.toml). It can bind the same D1 and import shared code from `src/lib/` via relative imports — wrangler bundles them.
- **No `send_email` binding in Pages config.** It validates fine in `wrangler pages dev` but breaks `wrangler pages secret`/`deploy`. Use the Email Service REST API (`POST /accounts/{id}/email/sending/send`) or Resend instead. Real Workers support the binding.
- **No `[observability]`.** The key is rejected by Pages config validation; the API PATCH silently ignores it; there is no dashboard toggle. Pages Functions get only the project's Metrics tab + `wrangler pages deployment tail`. Real Workers: `[observability] enabled = true` + `head_sampling_rate = 1` is free and captures 100% of invocations; `wrangler tail <name>` works.
- **Preview deployments use the PRODUCTION `database_id`, not `preview_database_id`**, when bindings are managed via wrangler.toml. A `wrangler pages deploy --branch=X` preview reads/writes prod D1 — treat preview as touching prod.
- **Bindings managed via wrangler.toml disable the dashboard "Add binding" UI.** Pick one management mode.
- `wrangler pages deployment delete` **can't delete aliased deployments** (`--force` doesn't pass the API's `?force=true`); use the dashboard.
- **A `404.html` disables SPA routing.** Pages serves it for any unmatched path, preempting the built-in "serve index.html with 200" fallback — and a `_redirects` rewrite (`/* /index.html 200`) does NOT override it. For an SPA: no 404.html at all.
- **`_redirects` still needs `/api/* /api/:splat 200`** or requests never reach `functions/api/` and `/api/*` 404s even though the Functions bundle uploaded fine.

## D1

- Prefer wrangler's native migrations (`migrations/NNNN_name.sql`, `wrangler d1 migrations apply <db> --remote|--local|--preview`) applied in CI before deploy. Forward-only.
- **Cross-worker schema change ordering:** add a backward-compatible migration → apply to remote D1 FIRST → then deploy the workers that read/write the new columns.
- If tests load migrations from an explicit list (e.g. `tests/helpers/test-db.js`), **every new migration must be added there too**.
- Watch for migration drift (schema ahead of the tracking table); a clean drop + re-apply fixes it.
- `D1_ERROR: Internal error while starting up D1 DB storage caused object to be reset` is a **transient Cloudflare-side** Durable Object cold-start hiccup, not an app bug. Self-recovers in seconds; if frequent, add retry-with-backoff around D1 calls.
- Local scripts can hit remote D1 via `wrangler d1 execute <db> --remote` using the `wrangler login` OAuth session (no API token). Retry transient `code 10000` OAuth-refresh races with backoff.
- D1 supports FTS5; keep it in sync with an `AFTER UPDATE` trigger on the source table.

## API tokens & auth

- Cloudflare has **Account** API tokens (under the account) and **User** API tokens (under My Profile); the two lists look identical. `wrangler whoami` prints "Account API Token" vs "User API Token" — fastest way to tell which list to search.
- CI token for a Pages + D1 + standalone-Worker repo needs **D1 Write + Pages Write + Workers Scripts Edit**. A Pages-only token makes the Worker deploy step fail with `Authentication error [code: 10000]` while every other step succeeds.
- **Secrets are write-only** — no store can be read back. A rotation must hit every store (each Pages env + each Worker) or one keeps running with a dead value and fails silently. Verify a new token against `/user/tokens/verify` before writing it anywhere.
- Pages secrets are **per-environment and non-inheritable**: set each in both `preview` and `production`. `--env` works on `wrangler pages secret put/delete` even though `--help` omits it.
- **Header-borne shared secrets must be hex, not base64.** Cloudflare's WAF answers `error code: 1104` when `/` or `+` appears in a custom header value — which looks exactly like the app rejecting the secret. `openssl rand -hex 24`.

## Auth libraries on Workers (Better Auth)

- `nodejs_compat` compatibility flag is required (imports `node:crypto`); without it the Worker won't boot.
- Build the auth instance **per request** from `env` (a `createAuth(env)` factory) — Workers are stateless; never a module-scope singleton.
- `<app>.pages.dev` and `<app>.workers.dev` are **different registrable domains**, so session cookies are third-party (Safari blocks). Use bearer tokens (CORS-exposed response header + localStorage + `Authorization: Bearer`), not cookies, when frontend and API live on different CF-owned domains.
- Email link-scanners (SaneBox etc.) prefetch and **consume single-use magic links**. Prefer passwords; make reset flows spend the token on POST, not GET. Same reason unsubscribe must be POST-mutating only.

## Caching & headers

- Zone **Browser Cache TTL** should be "Respect Existing Headers", with `public/_headers` marking HTML + app JS/CSS as `Cache-Control: no-cache`, so deploys reach returning users immediately. A zone-forced TTL strands users on stale assets.
- `_headers` also fixes MIME types (e.g. AudioWorklet files need `Content-Type: application/javascript`).

## Cron / scheduled workers

- Multiple schedules in one Worker: `[triggers] crons = [...]` and dispatch on `event.cron` in `scheduled()`. **Comment what each cron does** next to the schedule in wrangler.toml.
- Always pair cron with **manual HTTP trigger endpoints** for testing/backfill, gated by a shared secret (query param or header), and **default to dry-run** (`dry=1`), requiring `dry=0` to mutate/send.
- **Idempotency ledger:** a table with `UNIQUE (subject, kind, period)`, row inserted *before* the external call, so a retried cron can never double-send. Validate period keys strictly (`2026-6` ≠ `2026-06` as a key but is the same month).
- **Batching + resume pass:** one invocation stays inside the subrequest budget by sending at most N; schedule the cron twice (e.g. 1st and 2nd of the month) so the ledger-aware second run drains the remainder. Log `truncated`.
- Stagger dependent crons (scrape :00, post-process :15, downstream :45) instead of one mega-job.
- Be polite to scraped sites: delay between requests, custom User-Agent.

## Email senders

Three ways to send from CF projects — don't mix them up:
1. **`[[send_email]]` binding** — Workers only, never Pages. Sender address must be onboarded under Email Sending in the dashboard.
2. **Email Service REST API** — works everywhere including Pages Functions; needs `CF_ACCOUNT_ID` + a User token with only "Email Sending: Edit".
3. **Resend** — plain HTTPS API, good fallback (`email.js` cascades CF token → Resend → console dry-run for local dev).

## CI/CD

- Multi-app repos: a **matrix job** per Worker (`working_directory` per app) + a Pages job; `concurrency: group: deploy-${{ github.ref }}, cancel-in-progress: true` so a newer push cancels an in-flight deploy.
- Without path filters, every push redeploys every app — either accept it or add `paths:` filters per job.
- Order in the deploy job: test → `d1 migrations apply --remote` → `pages deploy` → deploy standalone Workers (`command: deploy --config workers/<name>/wrangler.toml`).
- Deploying a Worker does **not** touch its secrets — set once with `wrangler secret put`.
- Minimal no-build repo (static assets + worker): the whole workflow is checkout + `cloudflare/wrangler-action@v4` with `apiToken` (add `accountId` if the token isn't account-scoped).
