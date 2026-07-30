---
name: cloudflare
description: Bootstrap, deploy, and manage Cloudflare sites — Workers with Static Assets, Pages, D1, KV, cron workers. Use when the user wants to (1) create a new site or web app on Cloudflare, (2) deploy a project to Cloudflare, (3) create or apply D1 database migrations, (4) add a custom domain, (5) add a new page or route to an existing CF site, (6) add a standalone Cloudflare Worker (cron, email, scraper) to a project, (7) manage wrangler secrets, (8) any Cloudflare site management task. Subcommands are bootstrap, deploy, migrate, domain, add-page, add-worker, secrets.
---

# Cloudflare Site Toolkit

Umbrella skill for the full lifecycle of Cloudflare-hosted sites: bootstrap, deploy, migrate, manage domains, add content, attach Workers, manage secrets.

`references/gotchas.md` holds the expensive-to-rediscover platform traps (Pages limitations, D1 preview/database_id behavior, token taxonomy, caching, cron idempotency, email senders). **Read it before choosing Pages for a new project and whenever debugging deploys, secrets, email, or Pages weirdness.**

## Prerequisites

Before any subcommand, verify the required tools are available. If missing, provide the install command and stop.

| Tool | Check | Install |
|------|-------|---------|
| wrangler | `npx wrangler --version` (want v4+) | `npm install -g wrangler` then `wrangler login` |
| gh | `gh --version` | `brew install gh` then `gh auth login` |
| node | `node --version` | `brew install node` |
| hugo | `hugo version` (Hugo template only) | `brew install hugo` |

Auth check: run `npx wrangler whoami` to verify Cloudflare auth. If it fails, prompt the user to run `wrangler login` or set `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` env vars.

## Architecture decision first

Before generating anything, pick the platform shape:

**Worker + Static Assets (default for app-like sites).** One Worker serves static files via the `assets` config and runs server code first when needed. Unlike Pages Functions, a real Worker supports cron triggers, the `send_email` binding, `[observability]`/`wrangler tail`, and config-declared custom domains. Choose this whenever the site has any server-side component (API, cron, dynamic meta tags, email).

**Pages.** Still right for pure static sites (Hugo, Astro) using CF's native git integration, and for existing Pages projects. If a Pages project later needs cron/email/observability, add a standalone Worker beside it (see add-worker) rather than fighting Pages.

**Multi-app repo.** One directory per app, each with its own `wrangler.toml` + `package.json` (e.g. `api/`, `scraper/`, `frontend/`, or `worker/` + `pages/`, or `workers/<name>/` inside a Pages repo). Apps share data by pointing at the same D1 `database_id` or KV namespace `id` in each config. A standalone Worker may import shared code from the repo's `src/lib/` via relative imports — wrangler bundles them. Orchestrate with a root Makefile (`install` / `dev-<app>` / `deploy-<app>` / `deploy`) and/or a CI matrix.

## Naming Conventions

All resource names derive from the project name (kebab-case):

| Resource | Pattern | Example |
|----------|---------|---------|
| Repo | `<project>` | `task-tracker` |
| CF Pages project / Worker | `<project>` | `task-tracker` |
| D1 database (prod) | `<project>-db` | `task-tracker-db` |
| D1 database (preview) | `<project>-preview-db` | `task-tracker-preview-db` |
| Attached worker | `<project>-<purpose>` | `task-tracker-digest` |
| GitHub Actions workflow | `deploy.yml` | `deploy.yml` |

## Error Handling

When any wrangler or gh command fails:

1. Read the error output carefully
2. Diagnose the cause:
   - "not authenticated" / "not logged in" → prompt user to run `wrangler login` or `gh auth login`
   - "already exists" → suggest alternative name or confirm the user wants to use the existing resource
   - "exceeded" / "quota" / "limit" → explain the limit and suggest alternatives
   - `Authentication error [code: 10000]` on one CI step while others pass → the API token is missing a scope (see gotchas: token taxonomy)
   - `error code: 1104` on a request carrying a custom secret header → the secret contains `/` or `+`; regenerate as hex
   - `D1_ERROR ... object to be reset` → transient CF-side hiccup, retry
   - Network errors → retry once, then report
3. Attempt automatic fix when possible
4. If unfixable, explain clearly and suggest manual steps

---

## Subcommand: bootstrap

Create a new site from scratch — files, GitHub repo, CF project, optional D1, optional custom domain, first deploy.

### Step 1: Gather inputs

Ask the user (use AskUserQuestion):

1. **Project name** and short description
2. **Site type** — one of:
   - Worker + Static Assets (recommended default for apps)
   - Hugo documentation site
   - Vanilla JS + D1 app (Pages)
   - Astro static site
   - TanStack Start + D1
3. **Template options** (varies by type, see below)
4. **Custom domain?** — if yes, which domain
5. **CLAUDE.md conventions** — ask which to include:
   - Build and deploy commands
   - Content/writing guidelines
   - Code style conventions
   - Framework-specific patterns
   - D1 migration workflow
   - Testing conventions

### Step 2: Check idempotency

Before generating anything, check what already exists:
- Is there a git repo? (`git rev-parse --git-dir`)
- Is there a `wrangler.toml`/`wrangler.jsonc`?
- Does the CF project exist? (`npx wrangler pages project list | grep <project>` or `npx wrangler deployments list`)
- Does a D1 database exist? (`npx wrangler d1 list | grep <project>-db`)

Skip any step whose output already exists. Report what was skipped.

### Step 3: Generate project files

Generate all files based on the site type. Use the canonical configs below as reference, adapting names and options. Use a **recent compatibility_date** (today's date or close to it) for new projects.

### Step 4: Git + GitHub

```bash
git init
git add -A
git commit -m "Initial scaffold"
gh repo create <project> --private --source=. --push
```

### Step 5: Create the CF project

Pages: `npx wrangler pages project create <project> --production-branch main`
Worker + Assets: no create step — the first `npx wrangler deploy` creates it.

### Step 6: Create D1 database (if requested)

```bash
npx wrangler d1 create <project>-db
npx wrangler d1 create <project>-preview-db
```

Capture the database IDs from the output and write them into the wrangler config. Then apply the initial migration:

```bash
npx wrangler d1 migrations apply <project>-db --remote
```

### Step 7: CI/CD setup

**Use CF native git integration when:** Hugo/Astro static site without D1 or custom build steps.

**Use GitHub Actions when:** D1 migrations must run before deploy, tests exist, standalone Workers need deployment, or it's a Worker + Assets project. Generate `.github/workflows/deploy.yml` from the canonical workflow below.

### Step 8: Custom domain (if requested)

Worker + Assets: declared in config (see that site type) — nothing else to do beyond the zone existing on CF. Pages: delegate to the `domain` subcommand.

### Step 9: First deploy

Pages: `npx wrangler pages deploy <build-output-dir> --project-name=<project>`
Worker + Assets: `npx wrangler deploy`

Verify it's live by checking the output URL.

### Step 10: Generate CLAUDE.md

Write a `CLAUDE.md` tailored to the site type and user's convention choices. Include only what was requested. Keep it concise and actionable. Always include: architecture sketch (what runs where, which bindings), local dev commands, deploy path (push-to-deploy vs manual), migration workflow if D1, and any manual-trigger URLs for cron workers.

---

## Site Type: Worker + Static Assets

One Worker serving a static directory, optionally running server code first. Reference: mic-compare (howdousound.com). No build step, no framework required.

**Template options to ask:**
- Run worker first? (dynamic HTML rewriting, API routes in the worker) or assets-only
- D1 / KV / R2 bindings?
- Custom domain now?

**Files to generate:**

`wrangler.jsonc`:
```jsonc
{
  "name": "<project>",
  "main": "src/worker.js",
  "compatibility_date": "<recent>",
  "assets": {
    "directory": "./site",
    "binding": "ASSETS",
    "run_worker_first": true
  },
  // Custom domains are declared here — no dashboard step, no separate domain command:
  "routes": [
    { "pattern": "example.com", "custom_domain": true },
    { "pattern": "www.example.com", "custom_domain": true }
  ]
}
```

`src/worker.js` — pass through to assets by default; intercept only what needs server logic:
```javascript
export default {
  async fetch(request, env) {
    // default: serve static assets
    return env.ASSETS.fetch(request);
  },
};
```

Useful pattern: **HTMLRewriter over an asset response** for dynamic OG/meta tags (share links, per-URL previews) without templating the whole site — fetch the static HTML via `env.ASSETS.fetch()`, then `.on('meta[property="og:title"]', ...)` transform it.

`site/` — plain HTML/CSS/JS. `site/_headers` for cache-control and MIME fixes (AudioWorklet/module files may need explicit `Content-Type: application/javascript`).

**Build output:** none (deploy serves `site/` directly). **Deploy:** `npx wrangler deploy`.

**CI/CD (minimal — no build, no npm):**
```yaml
name: Deploy to Cloudflare Workers
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          wranglerVersion: "4"
```

---

## Site Type: Hugo Documentation Site

Framework: Hugo with Hextra theme. Reference: python-developer-tooling-handbook.

**Template options to ask:**
- Include D1 database? (for feedback, voting, etc.)
- Include Pages Functions? (API routes)

**Files to generate:**

`hugo.yaml`:
```yaml
baseURL: https://<project>.pages.dev/
languageCode: en-us
title: <Project Title>

module:
  imports:
    - path: github.com/imfing/hextra

markup:
  goldmark:
    renderer:
      unsafe: true
  highlight:
    noClasses: false

enableRobotsTXT: true
enableGitInfo: true
```

`package.json`:
```json
{
  "name": "<project>",
  "scripts": {
    "build": "hugo --gc --minify",
    "dev": "hugo server -D"
  }
}
```

`content/_index.md`:
```markdown
---
title: <Project Title>
---

Welcome to <Project Title>.
```

`wrangler.toml`:
```toml
name = "<project>"
compatibility_date = "<recent>"
pages_build_output_dir = "public"
```

If D1 requested, add the `[[d1_databases]]` binding (IDs filled in after creation).

If Pages Functions requested, create `functions/api/` directory with an example function.

**Build output:** `public/`

**CI/CD:** CF native git integration unless D1 is enabled.

---

## Site Type: Vanilla JS + D1 App (Pages)

No framework — vanilla HTML/CSS/JS with Cloudflare Pages Functions and D1. Reference: catechism (chiefend.reformedconfessions.com). Before picking this for a new project, consider Worker + Static Assets instead — see gotchas for what Pages Functions can't do.

**Template options to ask:**
- Include auth? (Better Auth on D1 — see notes below)
- Include example CRUD routes?

**Files to generate:**

`public/index.html`: Basic HTML shell with `<script src="/app.js"></script>`

`public/app.js`: Minimal JS app skeleton.

`public/styles.css`: Basic CSS reset and layout.

`public/_headers`: mark HTML + `app.js` + `styles.css` as `Cache-Control: no-cache` so deploys reach returning users immediately (pair with zone Browser Cache TTL = "Respect Existing Headers").

`public/_redirects` (if the app has API routes): must include `/api/* /api/:splat 200`. For an SPA, do NOT create a `404.html` — it disables the SPA fallback (see gotchas).

`functions/api/[[path]].js` — thin catch-all that delegates to a testable router in `src/lib/`:
```javascript
import { routeApiRequest } from '../../src/lib/api.js';
export async function onRequest(context) {
  return routeApiRequest(context);
}
```

`functions/api/_middleware.js` — auth/guard middleware. Exempt paths that authenticate themselves (auth endpoints, signed webhooks, signed unsubscribe links) before running the session guard.

`wrangler.toml`:
```toml
name = "<project>"
compatibility_date = "<recent>"
pages_build_output_dir = "./public"
# compatibility_flags = ["nodejs_compat"]  # required if using Better Auth / node:* imports

[[d1_databases]]
binding = "DB"
database_name = "<project>-db"
database_id = "<filled-after-creation>"
preview_database_id = "<filled-after-creation>"
migrations_dir = "migrations"
```

`migrations/0001_initial.sql`: Initial schema based on the app's purpose.

`package.json`:
```json
{
  "name": "<project>",
  "type": "module",
  "scripts": {
    "dev": "npx wrangler pages dev public",
    "test": "vitest run",
    "migrate:local": "npx wrangler d1 migrations apply <project>-db --local",
    "migrate:remote": "npx wrangler d1 migrations apply <project>-db --remote"
  },
  "devDependencies": {
    "wrangler": "^4",
    "vitest": "^4",
    "better-sqlite3": "^12"
  }
}
```

**Testing pattern:** unit-test API routes without miniflare — `tests/helpers/test-db.js` builds an in-memory better-sqlite3 DB by applying the migration files (keep its explicit migration list in sync when adding migrations), and a `callApi()` helper constructs a fake Pages `context` (Request + env + injected auth on `context.data`) and calls the router directly.

**Auth (Better Auth) notes:** `nodejs_compat` required; build the instance per request via `createAuth(env)` (never a module singleton); if the frontend lives on a different registrable domain than the API (pages.dev vs workers.dev), use bearer tokens, not cookies. Details in gotchas.

**Build output:** `public/`

**CI/CD:** GitHub Actions (needs migration step).

---

## Site Type: Astro Static Site

Astro with Cloudflare adapter. Modern static site with optional interactivity.

**Template options to ask:**
- Include D1 database?
- Include content collections?
- Include Pages Functions?

**Bootstrap method:**

```bash
npm create astro@latest <project> -- --template minimal --no-install
cd <project>
npx astro add cloudflare
npm install
```

Then overlay custom config:

`astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'static',
  adapter: cloudflare(),
});
```

If D1 requested, switch output to `'server'` or `'hybrid'` and add wrangler.toml with D1 binding.

`wrangler.toml`:
```toml
name = "<project>"
compatibility_date = "<recent>"
pages_build_output_dir = "dist"
```

**Build output:** `dist/`

**CI/CD:** CF native for simple static sites. GitHub Actions if D1 or custom build steps.

---

## Site Type: TanStack Start + D1

Full-stack React with TanStack Start, TanStack Router, Cloudflare adapter, D1.

**Template options to ask:**
- Include better-auth? (auth with D1 session storage)
- Include example CRUD routes? (demonstrates loaders, actions, D1 queries)
- Include D1 schema + initial migration?

**Bootstrap method:**

```bash
mkdir <project> && cd <project>
npm init -y
npm install @tanstack/react-start @tanstack/react-router react react-dom vinxi
npm install -D @types/react @types/react-dom typescript vite wrangler
```

If better-auth requested:
```bash
npm install better-auth
```

**Files to generate:**

`app.config.ts`:
```typescript
import { defineConfig } from '@tanstack/react-start/config';
import { cloudflare } from 'unenv';

export default defineConfig({
  server: {
    preset: 'cloudflare-pages',
    unenv: cloudflare,
  },
});
```

`tsconfig.json`:
```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "strict": true,
    "skipLibCheck": true,
    "paths": {
      "~/*": ["./app/*"]
    }
  }
}
```

`app/router.tsx`: TanStack Router setup with `createRouter`.

`app/routes/__root.tsx`: Root route with HTML shell, `<Outlet />`.

`app/routes/index.tsx`: Home page route with a loader example.

`app/client.tsx`: Client-side entry with `hydrateRoot` and `StartClient`.

`app/ssr.tsx`: Server-side entry with `createStartHandler`.

`wrangler.toml`:
```toml
name = "<project>"
compatibility_date = "<recent>"
pages_build_output_dir = "dist"

[[d1_databases]]
binding = "DB"
database_name = "<project>-db"
database_id = "<filled-after-creation>"
preview_database_id = "<filled-after-creation>"
migrations_dir = "migrations"
```

If better-auth requested, generate:
- `app/lib/auth.ts`: better-auth server config with D1 adapter (per-request factory, `nodejs_compat` flag)
- `app/lib/auth-client.ts`: better-auth client
- `app/routes/api/auth/$.ts`: Auth API catch-all route
- Migration SQL for auth tables (users, sessions, accounts)

If example CRUD routes requested, generate:
- `app/routes/items.tsx`: List route with loader
- `app/routes/items/$id.tsx`: Detail route with loader + action
- Migration SQL for example items table

`package.json` scripts:
```json
{
  "scripts": {
    "dev": "vinxi dev",
    "build": "vinxi build",
    "start": "vinxi start",
    "migrate:local": "npx wrangler d1 migrations apply <project>-db --local",
    "migrate:remote": "npx wrangler d1 migrations apply <project>-db --remote"
  }
}
```

**Build output:** `dist/`

**CI/CD:** GitHub Actions (needs build + migration steps).

---

## Canonical GitHub Actions Workflow

When GitHub Actions is needed, generate `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches:
      - main

concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - name: Install dependencies
        run: npm ci

      # Include this step only if tests exist
      - name: Run tests
        run: npm test

      # Include this step only if D1 is configured — migrations BEFORE deploy
      - name: Apply D1 migrations
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: d1 migrations apply <db-name> --remote

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy <build-output-dir> --project-name=<project>

      # Include one step per standalone Worker. Deploy does NOT touch the
      # Worker's secrets (set once with wrangler secret put). Token needs
      # Workers Scripts: Edit in addition to Pages/D1 scopes.
      - name: Deploy <name> Worker
        uses: cloudflare/wrangler-action@v4
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: deploy --config workers/<name>/wrangler.toml
```

**Multi-app repos** (several Workers + a frontend): use a matrix job instead of serial steps —

```yaml
jobs:
  deploy-workers:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - app: api
            working_directory: <root>/api
          - app: scraper
            working_directory: <root>/scraper
    defaults:
      run:
        working-directory: ${{ matrix.working_directory }}
    env:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: ${{ matrix.working_directory }}/package-lock.json
      - run: npm ci
      - run: npm run deploy
```

Note in the generated CLAUDE.md that **every push redeploys all apps** unless `paths:` filters are added.

Remind the user to set repo secrets, and that the token must be an **Account** API token with all needed scopes (D1 Write, Pages Write, Workers Scripts Edit — see gotchas):
```bash
gh secret set CLOUDFLARE_API_TOKEN
gh secret set CLOUDFLARE_ACCOUNT_ID
```

---

## Subcommand: deploy

Full deployment pipeline for the current project.

### Steps

1. **Detect project type**: Read `wrangler.toml`/`wrangler.jsonc` (an `assets` key = Worker + Assets; `pages_build_output_dir` = Pages), `hugo.yaml`/`hugo.toml`, `astro.config.*`, `app.config.ts`.

2. **Run tests** (if present): Check for test scripts in `package.json`. Run `npm test`. If tests fail, report and stop.

3. **Apply D1 migrations** (if configured): Check the wrangler config for `[[d1_databases]]`. If present:
   ```bash
   npx wrangler d1 migrations apply <db-name> --remote
   ```

4. **Build**:
   - Hugo: `hugo --gc --minify`
   - Vanilla JS / Worker + Assets: no build step
   - Astro / TanStack Start / Vite frontends: `npm run build`

5. **Deploy**:
   - Pages: `npx wrangler pages deploy <build-output-dir> --project-name=<project>`
   - Worker + Assets: `npx wrangler deploy`

6. **Verify**: Check the output URL from wrangler. Report the live URL to the user.

7. **Deploy standalone Workers** (if any): Check for `workers/*/wrangler.toml`. For each:
   ```bash
   npx wrangler deploy --config workers/<name>/wrangler.toml
   ```

**Debugging a deploy:** `npx wrangler tail <worker-name>` for Workers; `npx wrangler pages deployment tail` for Pages Functions (that's all Pages gets — see gotchas).

---

## Subcommand: migrate

D1 database migration management using wrangler's native migration system.

### Usage

Parse the argument to determine the sub-action:
- `/cloudflare migrate create` — create a new migration
- `/cloudflare migrate apply` — apply pending migrations
- `/cloudflare migrate status` — show migration status

### migrate create

1. Ask the user for a migration description
2. List existing migrations in `migrations/` to determine the next number
3. Create `migrations/<NNNN>_<description>.sql` with the next sequential number (zero-padded to 4 digits)
4. Write the SQL based on their description. Migrations are **forward-only** and should be backward-compatible (`ALTER … ADD COLUMN` / `CREATE TABLE IF NOT EXISTS` + backfill `UPDATE`s) so old code keeps running against the new schema
5. If tests build their DB from an explicit migration list (e.g. `tests/helpers/test-db.js`), **add the new migration there too**
6. If a `schema.sql` full-schema file exists in the repo, update it in the same change

### migrate apply

1. Read the wrangler config to get the database name
2. Apply to production:
   ```bash
   npx wrangler d1 migrations apply <db-name> --remote
   ```
3. Apply to preview (if preview database configured): add `--preview`; local dev: `--local`
4. **Cross-worker ordering**: when the schema change spans multiple workers, apply to remote D1 FIRST (it's backward-compatible), then deploy the workers that read/write the new columns

### migrate status

1. List files in `migrations/` directory
2. Run `npx wrangler d1 migrations list <db-name> --remote` to show applied migrations
3. Report which migrations are pending

**Ad-hoc production queries** (grants, backfills, checks) use the OAuth session — no token needed:
```bash
npx wrangler d1 execute <db-name> --remote --command "SELECT ..."
```

---

## Subcommand: domain

Add or manage a custom domain.

### Worker + Assets projects

Declare it in the wrangler config and redeploy — that's the whole procedure:
```jsonc
"routes": [
  { "pattern": "example.com", "custom_domain": true },
  { "pattern": "www.example.com", "custom_domain": true }
]
```
Requires the zone to exist on Cloudflare. DNS + SSL are provisioned automatically on deploy.

### Pages projects

1. Ask for the domain name (e.g., `example.com` or `app.example.com`)
2. Get the CF Pages project name from `wrangler.toml`
3. Add the custom domain:
   ```bash
   npx wrangler pages project add-domain <project> <domain>
   ```
4. If the zone is on Cloudflare, DNS records are auto-configured. If not, provide the CNAME: `<subdomain>` → `<project>.pages.dev`
5. Report that SSL provisions automatically and may take a few minutes
6. **Zone caching check**: set the zone's Browser Cache TTL to "Respect Existing Headers" and make sure `_headers` marks HTML/JS/CSS `no-cache`, or deploys will strand returning users on stale assets (see gotchas)

---

## Subcommand: add-page

Framework-aware content/route creation.

### Steps

1. Detect the project type from config files
2. Ask the user for the page/route name and purpose
3. Generate the appropriate file(s):

**Hugo:**
- Determine the content section from context (ask if ambiguous)
- Create `content/<section>/<slug>.md` with frontmatter:
  ```markdown
  ---
  title: <Title>
  date: <today>
  draft: true
  ---
  ```
- If the section uses a specific archetype, follow that pattern

**Astro:**
- Create `src/pages/<slug>.astro` with the project's layout imported
- If using content collections, create in `src/content/` instead

**TanStack Start:**
- Create `app/routes/<slug>.tsx` with route boilerplate (`createFileRoute`); add a loader if the route needs data

**Vanilla JS / Worker + Assets:**
- Create `public/<slug>.html` (or `site/<slug>.html`) with the project's HTML structure
- If an API endpoint is needed: Pages → route it through the existing `functions/api/` router; Worker + Assets → add a path check in the worker's `fetch`

---

## Subcommand: add-worker

Attach a standalone Cloudflare Worker to an existing project. This is the standard escape hatch for anything a Pages project can't do (cron, `send_email`, observability) and for scrapers/digests/schedulers generally.

### Steps

1. Ask the user:
   - Worker name/purpose (e.g., "digest", "scraper", "webhook")
   - Trigger type: HTTP, cron schedule, or both
   - Bindings needed: D1 (usually the project's existing database), KV, AI, Vectorize, `send_email`, secrets

2. Create `workers/<name>/`:

`workers/<name>/src/index.ts` (or `index.js`):
```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Manual trigger endpoints for testing/backfill — always gate with a
    // shared secret, and default to DRY RUN (require dry=0 to mutate/send).
    if (url.pathname === '/run') {
      const token = url.searchParams.get('key') ?? request.headers.get('X-Run-Key');
      if (!env.RUN_SECRET || token !== env.RUN_SECRET) {
        return new Response('Unauthorized', { status: 401 });
      }
      const dry = url.searchParams.get('dry') !== '0';
      const result = await run(env, { dry });
      return Response.json(result);
    }

    return new Response('OK');
  },

  // Include only if cron trigger requested. With multiple schedules,
  // dispatch on event.cron:
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    switch (event.cron) {
      case '0 8 * * *':
        await run(env, { dry: false });
        break;
    }
  },
};
```

`workers/<name>/wrangler.toml`:
```toml
name = "<project>-<purpose>"
main = "src/index.ts"
compatibility_date = "<recent>"

# Free, no code needed, captures 100% of invocations; enables wrangler tail
# and the Observability dashboard:
[observability]
enabled = true
head_sampling_rate = 1

# Include only if cron trigger requested. COMMENT what each schedule does —
# future-you will not remember:
# [triggers]
# crons = ["0 8 * * *"]  # daily run at 8:00 UTC

# Reuse the project's EXISTING database id to share data with the main app:
# [[d1_databases]]
# binding = "DB"
# database_name = "<project>-db"
# database_id = "<same id as the main app>"

# [vars]
# APP_URL = "https://..."
```

3. **Shared code**: the worker can `import` from the repo's `src/lib/` with relative paths — wrangler bundles them. Reuse the app's own logic rather than duplicating it. Only add `nodejs_compat` if the bundle actually imports `node:*`.

4. **Design rules for cron jobs that send or mutate** (see gotchas for the full rationale):
   - Idempotency ledger: `UNIQUE (subject, kind, period)`, insert **before** the external call
   - Batch within the subrequest budget; add a second cron firing (e.g. the next day) as a ledger-aware resume pass; log when truncated
   - Manual trigger endpoint defaults to dry-run

5. **Secrets**: `npx wrangler secret put <NAME> -c workers/<name>/wrangler.toml`. Worker secrets are separate stores from the Pages project's — a value set on Pages is not readable here; shared secrets (e.g. a link-signing key) must be set in both places with the same value. Header-borne secrets: hex, not base64.

6. If the project uses GitHub Actions, add a deploy step (see canonical workflow). Warn that the CI token needs **Workers Scripts: Edit** or this one step fails with code 10000. Until then: `npx wrangler deploy --config workers/<name>/wrangler.toml` by hand.

7. **Debugging**: `npx wrangler tail <project>-<purpose>` streams live logs; the Observability dashboard has queryable structured logs (~3-day retention).

---

## Subcommand: secrets

Manage secrets across local dev, Pages environments, and Workers.

### Where secrets live

| Store | Set with | Read back? |
|-------|----------|------------|
| Local dev | `.dev.vars` (gitignored) in the app dir | yes (it's a file) |
| Worker | `wrangler secret put <NAME> [-c path/wrangler.toml]` | no |
| Pages preview | `wrangler pages secret put <NAME> --project-name=<p> --env preview` | no |
| Pages production | same with `--env production` | no |
| CI | `gh secret set <NAME>` | no |

Pages secrets are **per-environment and non-inheritable** — always set both envs. Nothing but `.dev.vars` can be read back, so rotations must hit every store or something keeps running on a dead value and fails silently.

### Generate a `set-secrets.sh` for the project

For any project with more than a couple of secrets, generate an idempotent `scripts/set-secrets.sh` following these rules (reference: catechism):

- Generate random signing secrets with `openssl rand -base64 32`; use `openssl rand -hex 24` for anything sent in an HTTP header (WAF rejects `/` and `+` — see gotchas)
- Prompt with `read -rs` (hidden) and pipe with `printf '%s'` (no trailing newline) straight into `wrangler ... secret put`
- Verify API tokens against `https://api.cloudflare.com/client/v4/user/tokens/verify` **before** writing them anywhere
- Loop over target environments (`preview` `production` + any workers holding the same value)
- Offer to write a matching `.dev.vars` at the end; ensure `.dev.vars`/`**/.dev.vars` is gitignored (append if missing)
- Distinguish "regenerate" from "rotate one value": regenerating a session-signing secret signs everyone out — a script that rotates only one token must not touch the others

### Single-key helper

For a one-secret project, a tiny `set-<name>-key.sh` that writes `KEY=value` to the right `.dev.vars` (chmod 600, auto-gitignore) is enough — then `wrangler dev` picks it up; `wrangler dev --remote` binds real AI/bindings while reading local `.dev.vars`.
