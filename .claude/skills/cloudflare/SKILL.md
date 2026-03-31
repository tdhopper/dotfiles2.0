---
name: cloudflare
description: Bootstrap, deploy, and manage Cloudflare Pages sites, D1 databases, and Workers. Use when the user wants to (1) create a new site or web app on Cloudflare, (2) deploy a project to Cloudflare Pages, (3) create or apply D1 database migrations, (4) add a custom domain to a CF Pages project, (5) add a new page or route to an existing CF site, (6) add a standalone Cloudflare Worker to a project, (7) any Cloudflare site management task. Subcommands: bootstrap, deploy, migrate, domain, add-page, add-worker.
---

# Cloudflare Site Toolkit

Umbrella skill for the full lifecycle of Cloudflare-hosted sites: bootstrap, deploy, migrate, manage domains, add content, and attach Workers.

## Prerequisites

Before any subcommand, verify the required tools are available. If missing, provide the install command and stop.

| Tool | Check | Install |
|------|-------|---------|
| wrangler | `npx wrangler --version` | `npm install -g wrangler` then `wrangler login` |
| gh | `gh --version` | `brew install gh` then `gh auth login` |
| node | `node --version` | `brew install node` |
| hugo | `hugo version` (Hugo template only) | `brew install hugo` |

Auth check: run `npx wrangler whoami` to verify Cloudflare auth. If it fails, prompt the user to run `wrangler login` or set `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` env vars.

## Naming Conventions

All resource names derive from the project name (kebab-case):

| Resource | Pattern | Example |
|----------|---------|---------|
| Repo | `<project>` | `prayer-tracker` |
| CF Pages project | `<project>` | `prayer-tracker` |
| D1 database (prod) | `<project>-db` | `prayer-tracker-db` |
| D1 database (preview) | `<project>-preview-db` | `prayer-tracker-preview-db` |
| Worker | `<project>-<purpose>` | `prayer-tracker-email` |
| GitHub Actions workflow | `deploy.yml` | `deploy.yml` |

## Error Handling

When any wrangler or gh command fails:

1. Read the error output carefully
2. Diagnose the cause:
   - "not authenticated" / "not logged in" → prompt user to run `wrangler login` or `gh auth login`
   - "already exists" → suggest alternative name or confirm the user wants to use the existing resource
   - "exceeded" / "quota" / "limit" → explain the limit and suggest alternatives
   - Network errors → retry once, then report
3. Attempt automatic fix when possible (e.g., retry with alternative name)
4. If unfixable, explain clearly and suggest manual steps

---

## Subcommand: bootstrap

Create a new site from scratch — files, GitHub repo, CF Pages project, optional D1, optional custom domain, first deploy.

### Step 1: Gather inputs

Ask the user (use AskUserQuestion):

1. **Project name** and short description
2. **Site type** — one of:
   - Hugo documentation site
   - Vanilla JS + D1 app
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
- Is there a `wrangler.toml`?
- Does the CF Pages project exist? (`npx wrangler pages project list | grep <project>`)
- Does a D1 database exist? (`npx wrangler d1 list | grep <project>-db`)

Skip any step whose output already exists. Report what was skipped.

### Step 3: Generate project files

Generate all files based on the site type. Use the canonical configs below as reference, adapting names and options.

### Step 4: Git + GitHub

```bash
git init
git add -A
git commit -m "Initial scaffold"
gh repo create <project> --private --source=. --push
```

### Step 5: Create CF Pages project

```bash
npx wrangler pages project create <project> --production-branch main
```

### Step 6: Create D1 database (if requested)

```bash
npx wrangler d1 create <project>-db
npx wrangler d1 create <project>-preview-db
```

Capture the database IDs from the output and write them into `wrangler.toml`. Then apply the initial migration:

```bash
npx wrangler d1 migrations apply <project>-db --remote
```

### Step 7: CI/CD setup

**Use CF native git integration when:**
- Hugo site without D1 or custom build steps
- Simple Astro site without D1

To set up CF native: connect GitHub repo to CF Pages project in dashboard, or:
```bash
npx wrangler pages project update <project> --repo <owner>/<project> --production-branch main
```

**Use GitHub Actions when:**
- D1 migrations need to run before deploy
- Custom build steps (tests, multi-tool builds)
- Standalone Workers need deployment

Generate `.github/workflows/deploy.yml` using the canonical workflow pattern.

### Step 8: Custom domain (if requested)

Delegate to the `domain` subcommand.

### Step 9: First deploy

```bash
npx wrangler pages deploy <build-output-dir> --project-name=<project>
```

Verify it's live by checking the output URL.

### Step 10: Generate CLAUDE.md

Write a `CLAUDE.md` tailored to the site type and user's convention choices. Include only what was requested. Keep it concise and actionable.

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
compatibility_date = "2025-01-01"
pages_build_output_dir = "public"
```

If D1 requested, add the `[[d1_databases]]` binding (IDs filled in after creation).

If Pages Functions requested, create `functions/api/` directory with an example function.

**Build output:** `public/`

**CI/CD:** CF native git integration unless D1 is enabled.

---

## Site Type: Vanilla JS + D1 App

No framework — vanilla HTML/CSS/JS with Cloudflare Pages Functions and D1. Reference: catechism.

**Template options to ask:**
- Include auth? (session-based auth with cookies)
- Include example CRUD routes?

**Files to generate:**

`public/index.html`: Basic HTML shell with `<script src="/app.js"></script>`

`public/app.js`: Minimal JS app skeleton.

`public/styles.css`: Basic CSS reset and layout.

`functions/api/[[path]].js`: Catch-all API router:
```javascript
export async function onRequest(context) {
  const url = new URL(context.request.url);
  const path = url.pathname.replace('/api/', '');

  // Route to handlers based on path
  // Add route handlers here

  return new Response('Not found', { status: 404 });
}
```

`wrangler.toml`:
```toml
name = "<project>"
compatibility_date = "2025-01-01"
pages_build_output_dir = "./public"

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
  "scripts": {
    "dev": "npx wrangler pages dev public",
    "test": "vitest run",
    "migrate:local": "npx wrangler d1 migrations apply <project>-db --local",
    "migrate:remote": "npx wrangler d1 migrations apply <project>-db --remote"
  },
  "devDependencies": {
    "wrangler": "^4",
    "vitest": "^3",
    "better-sqlite3": "^11"
  }
}
```

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
compatibility_date = "2025-01-01"
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
compatibility_date = "2025-01-01"
pages_build_output_dir = "dist"

[[d1_databases]]
binding = "DB"
database_name = "<project>-db"
database_id = "<filled-after-creation>"
preview_database_id = "<filled-after-creation>"
migrations_dir = "migrations"
```

If better-auth requested, generate:
- `app/lib/auth.ts`: better-auth server config with D1 adapter
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

      # Include this step only if D1 is configured
      - name: Apply D1 migrations
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: d1 migrations apply <db-name> --remote

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy <build-output-dir> --project-name=<project>
```

Adapt placeholders (`<db-name>`, `<build-output-dir>`, `<project>`) to the actual project. Add Hugo install step for Hugo sites, or other tool-specific steps as needed.

Remind the user to set `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as GitHub repo secrets:
```bash
gh secret set CLOUDFLARE_API_TOKEN
gh secret set CLOUDFLARE_ACCOUNT_ID
```

---

## Subcommand: deploy

Full deployment pipeline for the current project.

### Steps

1. **Detect project type**: Read `wrangler.toml`, `hugo.yaml`/`hugo.toml`, `astro.config.*`, `app.config.ts` to determine the site type.

2. **Run tests** (if present): Check for test scripts in `package.json`. Run `npm test`. If tests fail, report and stop.

3. **Apply D1 migrations** (if configured): Check `wrangler.toml` for `[[d1_databases]]`. If present:
   ```bash
   npx wrangler d1 migrations apply <db-name> --remote
   ```

4. **Build**:
   - Hugo: `hugo --gc --minify`
   - Vanilla JS: no build step (static files in `public/`)
   - Astro: `npm run build`
   - TanStack Start: `npm run build`

5. **Deploy**:
   ```bash
   npx wrangler pages deploy <build-output-dir> --project-name=<project>
   ```

6. **Verify**: Check the output URL from wrangler. Report the live URL to the user.

7. **Deploy Workers** (if any): Check for `workers/*/wrangler.toml`. For each:
   ```bash
   cd workers/<name> && npx wrangler deploy
   ```

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
4. Ask the user what SQL to include, or generate it based on their description

### migrate apply

1. Read `wrangler.toml` to get the database name
2. Apply to production:
   ```bash
   npx wrangler d1 migrations apply <db-name> --remote
   ```
3. Apply to preview (if preview database configured):
   ```bash
   npx wrangler d1 migrations apply <db-name> --remote --preview
   ```

### migrate status

1. List files in `migrations/` directory
2. Run `npx wrangler d1 migrations list <db-name> --remote` to show applied migrations
3. Report which migrations are pending

---

## Subcommand: domain

Add or manage a custom domain for a CF Pages project.

### Steps

1. Ask for the domain name (e.g., `example.com` or `app.example.com`)
2. Get the CF Pages project name from `wrangler.toml`
3. Check if the domain's zone exists on Cloudflare:
   ```bash
   npx wrangler pages project list  # confirm project exists
   ```
4. Add the custom domain:
   ```bash
   npx wrangler pages project add-domain <project> <domain>
   ```
5. If the zone is on Cloudflare, DNS records are auto-configured. If not, provide the CNAME record the user needs to add:
   - CNAME `<subdomain>` → `<project>.pages.dev`
6. Report that SSL will be provisioned automatically and may take a few minutes

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
- Create `src/pages/<slug>.astro` with the project's layout imported:
  ```astro
  ---
  import Layout from '../layouts/Layout.astro';
  ---
  <Layout title="<Title>">
    <main>
      <h1><Title></h1>
    </main>
  </Layout>
  ```
- If using content collections, create in `src/content/` instead

**TanStack Start:**
- Create `app/routes/<slug>.tsx` with route boilerplate:
  ```tsx
  import { createFileRoute } from '@tanstack/react-router';

  export const Route = createFileRoute('/<slug>')({
    component: RouteComponent,
  });

  function RouteComponent() {
    return <div><h1><Title></h1></div>;
  }
  ```
- If the route needs data, add a loader function
- For nested routes, create the appropriate directory structure

**Vanilla JS + D1:**
- Create `public/<slug>.html` with the project's HTML structure
- If an API endpoint is needed, create `functions/api/<slug>.js`

---

## Subcommand: add-worker

Attach a standalone Cloudflare Worker to an existing project.

### Steps

1. Ask the user:
   - Worker name/purpose (e.g., "email", "cron-cleanup", "webhook")
   - Trigger type: HTTP, cron schedule, or both
   - Bindings needed: D1, KV, secrets, etc.

2. Create `workers/<name>/` directory structure:

`workers/<name>/src/index.ts`:
```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // HTTP handler
    return new Response('OK');
  },

  // Include only if cron trigger requested:
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    // Cron handler
  },
};

interface Env {
  // Add bindings here
}
```

`workers/<name>/wrangler.toml`:
```toml
name = "<project>-<purpose>"
main = "src/index.ts"
compatibility_date = "2025-01-01"

# Include only if cron trigger requested:
# [triggers]
# crons = ["0 8 * * *"]
```

Add D1 bindings, KV namespaces, or secrets to the wrangler.toml as requested.

`workers/<name>/package.json`:
```json
{
  "name": "<project>-<purpose>",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy"
  },
  "devDependencies": {
    "wrangler": "^4",
    "typescript": "^5"
  }
}
```

`workers/<name>/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "types": ["@cloudflare/workers-types"]
  }
}
```

3. If the project uses GitHub Actions, add a deploy step for the worker:
   ```yaml
   - name: Deploy <name> worker
     uses: cloudflare/wrangler-action@v3
     with:
       apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
       accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
       command: deploy
       workingDirectory: workers/<name>
   ```

4. Run `cd workers/<name> && npm install`
