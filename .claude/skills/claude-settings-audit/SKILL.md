---
name: claude-settings-audit
description: Analyze a repository to generate recommended Claude Code settings.json permissions. Use when setting up a new project, auditing existing settings, or determining which read-only bash commands to allow. Detects tech stack, build tools, and monorepo structure.
---

# Claude Settings Audit

Analyze this repository and generate recommended Claude Code `settings.json` permissions for read-only commands.

## Phase 1: Detect Tech Stack

Run these commands to detect the repository structure:

```bash
ls -la
find . -maxdepth 2 \( -name "*.toml" -o -name "*.json" -o -name "*.lock" -o -name "*.yaml" -o -name "*.yml" -o -name "Makefile" -o -name "Dockerfile" -o -name "*.tf" \) 2>/dev/null | head -50
```

Check for these indicator files:

| Category | Files to Check |
|----------|---------------|
| **Python** | `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile`, `poetry.lock`, `uv.lock` |
| **Node.js** | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| **Go** | `go.mod`, `go.sum` |
| **Rust** | `Cargo.toml`, `Cargo.lock` |
| **Ruby** | `Gemfile`, `Gemfile.lock` |
| **Java** | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| **Build** | `Makefile`, `Dockerfile`, `docker-compose.yml` |
| **Infra** | `*.tf` files, `kubernetes/`, `helm/` |
| **Monorepo** | `lerna.json`, `nx.json`, `turbo.json`, `pnpm-workspace.yaml` |

## Phase 2: Detect Services

Check for service integrations:

Read dependency files to identify frameworks:
- `package.json` → check `dependencies` and `devDependencies`
- `pyproject.toml` → check `[project.dependencies]` or `[tool.poetry.dependencies]`
- `Gemfile` → check gem names
- `Cargo.toml` → check `[dependencies]`

## Phase 3: Check Existing Settings

```bash
cat .claude/settings.json 2>/dev/null || echo "No existing settings"
```

## Phase 4: Generate Recommendations

Build the allow list by combining:

### Baseline Commands (Always Include)

```json
[
  "Bash(ls:*)",
  "Bash(pwd:*)",
  "Bash(find:*)",
  "Bash(file:*)",
  "Bash(stat:*)",
  "Bash(wc:*)",
  "Bash(head:*)",
  "Bash(tail:*)",
  "Bash(cat:*)",
  "Bash(tree:*)",
  "Bash(git status:*)",
  "Bash(git log:*)",
  "Bash(git diff:*)",
  "Bash(git show:*)",
  "Bash(git branch:*)",
  "Bash(git remote:*)",
  "Bash(git tag:*)",
  "Bash(git stash list:*)",
  "Bash(git rev-parse:*)",
  "Bash(gh pr view:*)",
  "Bash(gh pr list:*)",
  "Bash(gh pr checks:*)",
  "Bash(gh pr diff:*)",
  "Bash(gh issue view:*)",
  "Bash(gh issue list:*)",
  "Bash(gh run view:*)",
  "Bash(gh run list:*)",
  "Bash(gh run logs:*)",
  "Bash(gh repo view:*)",
  "Bash(gh api:*)"
]
```

### Stack-Specific Commands

| If Detected | Add These Commands |
|-------------|-------------------|
| **Python** | `python --version`, `python3 --version`, `pip list`, `pip show`, `pip freeze`, `poetry show`, `poetry env info`, `uv pip list` |
| **Node.js** | `node --version`, `npm list`, `npm view`, `npm outdated`, `yarn list`, `yarn info`, `yarn why`, `pnpm list`, `tsc --version` |
| **Go** | `go version`, `go list`, `go mod graph`, `go env` |
| **Rust** | `rustc --version`, `cargo --version`, `cargo tree`, `cargo metadata` |
| **Ruby** | `ruby --version`, `gem list`, `bundle list`, `bundle show` |
| **Java** | `java --version`, `mvn --version`, `mvn dependency:tree`, `gradle --version`, `gradle dependencies` |
| **Docker** | `docker --version`, `docker ps`, `docker images`, `docker-compose ps`, `docker-compose config` |
| **Terraform** | `terraform --version`, `terraform providers`, `terraform state list` |
| **Make** | `make --version`, `make -n` |

```

#### Framework-Specific

| If Detected | Add Domains |
|-------------|-------------|
| **Django** | `docs.djangoproject.com` |
| **Flask** | `flask.palletsprojects.com` |
| **FastAPI** | `fastapi.tiangolo.com` |
| **React** | `react.dev` |
| **Next.js** | `nextjs.org` |
| **Vue** | `vuejs.org` |
| **Express** | `expressjs.com` |
| **Rails** | `guides.rubyonrails.org`, `api.rubyonrails.org` |
| **Go** | `pkg.go.dev` |
| **Rust** | `docs.rs`, `doc.rust-lang.org` |
| **Docker** | `docs.docker.com` |
| **Kubernetes** | `kubernetes.io` |
| **Terraform** | `registry.terraform.io` |

### MCP Server Suggestions

MCP servers are configured in `.mcp.json` (not `settings.json`). Check for existing config:

```bash
cat .mcp.json 2>/dev/null || echo "No existing .mcp.json"
```

#### Sentry MCP (if Sentry SDK detected)

Add to `.mcp.json`:
```json
{
  "mcpServers": {
    "sentry": {
      "command": "uvx",
      "args": ["mcp-server-sentry"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}"
      }
    }
  }
}
```

#### Linear MCP (if Linear usage detected)

Add to `.mcp.json`:
```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "@linear/mcp-server"],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    }
  }
}
```

**Note**: Never suggest GitHub MCP. Always use `gh` CLI commands for GitHub.

## Output Format

Present your findings as:

1. **Summary Table** - What was detected
2. **Recommended settings.json** - Complete JSON ready to copy
3. **MCP Suggestions** - If applicable
4. **Merge Instructions** - If existing settings found

Example output structure:

```markdown
## Detected Tech Stack

| Category | Found |
|----------|-------|
| Languages | Python 3.x |
| Package Manager | poetry |
| Frameworks | Django, Celery |
| Services | Sentry |
| Build Tools | Docker, Make |

## Recommended .claude/settings.json

\`\`\`json
{
  "permissions": {
    "allow": [
      // ... grouped by category with comments
    ],
    "deny": []
  }
}
\`\`\`


```

## Important Notes

- Only suggest READ-ONLY commands - never commands that modify state
- The `:*` suffix allows any arguments to the base command
- Group commands with comments for readability
- If existing settings found, show what to add vs what's already present
