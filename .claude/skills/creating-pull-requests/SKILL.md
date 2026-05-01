---
name: creating-pull-requests
description: Use this skill when creating or updating pull requests. Ensures proper PR formatting with active-voice titles and structured descriptions explaining why, how, and context links. Also use when the user says "update PR", "refresh PR description", "rewrite PR", or wants to sync a PR's title/description with the current branch state.
---

# Creating & updating pull requests

A PR description is prose written to manage a reviewer's attention. Optimise for review speed, not comprehensiveness: a good description gets the reviewer oriented in 30 seconds and answers "what changed, why, and where do I start reading?" before they open the diff.

# Critical rules

NEVER:
- Add `Co-Authored-By` headers on commits.
- Include "Generated with Claude Code" or any AI/Claude attribution.
- Mention Claude, AI, agents, or assistants anywhere in the PR.

# Load PROSE.md before drafting

If `~/.claude/PROSE.md` exists, read it before writing the description. PR descriptions are prose; the rules there apply directly. Most load-bearing for PRs:

- **Active voice, present tense.** "X overrides Y" not "Y is overridden by X". "`total_pairs` came from the CSV" not "`total_pairs` was derived from the CSV".
- **Omit needless words.** Cut "in order to", "the fact that", hedges like "rather", "quite", "very".
- **Front-load keywords.** Put the most important word in the first two words of each paragraph and header.
- **Bold sparingly (Von Restorff).** One bolded headline per Reviewer-notes bullet. If you bold everything, nothing stands out.
- **Concrete > abstract.** "showed `71 / 113  63%` instead of `71 / 160  44%`" lands harder than "showed an inflated percentage".
- **Paragraphs 2–4 lines.** Long blocks get skipped; one-line fragments fragment.
- **No "In conclusion", "Overall", "In summary".** End with a next step or a final fact.

# Title format

Active voice, present tense, full scope.

| Good | Bad |
|------|-----|
| Add user authentication | Added user authentication |
| Fix memory leak in cache | Fixing memory leak |
| Use AnnotationHub sample sources for listening-test progress | Update bq_export.py |

Pattern: `<Verb> <what> [in/for/to <context>]`

Common verbs: Add, Fix, Update, Remove, Refactor, Implement, Improve, Replace, Enable, Disable, Use, Make.

# Description structure

Pick the template that matches the PR's complexity. Don't bloat a 30-line bug fix with a TL;DR and files table; don't bury a 400-line refactor in a single paragraph.

## Small PR (one concern, < ~50 lines)

```markdown
## Why

[2–3 sentences: what problem, what the PR does about it. Concrete example or number if possible.]

## How it works

[Brief technical description. Bullets if there are 3+ moving parts.]

## Links

- [Ticket](url)
```

## Non-trivial PR (multiple files, non-obvious tradeoffs, or > ~50 lines)

```markdown
## TL;DR

[Two sentences. First names the symptom with a concrete number/example. Second names the fix.]

**Files to review (N, +X / -Y):**

| File | Why |
|---|---|
| `path/to/start_here.py` *(new)* | One-line pointer. Mark one file as the natural entry point. |
| `path/to/other.py` | Short reason. |

## Root cause / Why

[Why the PR exists. Show the problem with concrete numbers, error messages, or a before/after.]

## Fix / How

[The change, top-down. Numbered steps work well for pipelines; bullets for parallel changes.]

## Reviewer notes

**One key fact per note (bolded headline).** Use these for tradeoffs you considered, fallback behaviour, why a helper lives in a separate module — anything the reviewer would otherwise stop and ask about.

## Tests

[Bullets: what's covered, what isn't, how many tests pass.]

## Follow-up

[Out-of-scope items this PR sets up for later. Optional.]

## Links

- [Ticket](url)
- [Slack thread](url)
```

# Reviewer-friendliness checklist

A reviewer should be able to:

- Read the title → know the full scope.
- Read the TL;DR → know symptom + fix without scrolling.
- Read the files-to-review table → know where to start (mark one file "start here" when there's a natural entry point).
- Find non-obvious gotchas in **Reviewer notes** instead of hunting in the diff.

If you can't draft the TL;DR in two clean sentences, you don't yet understand the PR well enough to describe it. Re-read the diff first.

# Process

## 1. Detect: create or update?

```bash
# If a PR exists for this branch, this is an update.
gh pr view --json number,title,body,baseRefName,url 2>/dev/null
```

For Spotify GHE: `GH_HOST=ghe.spotify.net gh pr view --repo <org>/<repo> <num> ...`.

## 2. Gather context

```bash
BASE=$(gh pr view --json baseRefName -q '.baseRefName' 2>/dev/null || echo "main")

git diff $BASE...HEAD          # full diff — what the PR represents
git diff $BASE...HEAD --stat   # shape: files, +/- counts
git log $BASE..HEAD --oneline  # commits
```

Read the actual diff, not just the stat. The description must reflect what the code does now.

## 3. Find links

Pull from commits, branch name, and ask the user for:
- Jira/ticket numbers
- Slack threads
- Fusion runs, GCS paths, dashboards

When updating, preserve every link from the existing description.

## 4. Draft

Apply PROSE.md. Sketch the TL;DR first — it forces clarity before you commit to a structure.

## 5. Apply

```bash
gh pr create --title "..." --body "$(cat <<'EOF'
...
EOF
)"

gh pr edit <number> --title "..." --body "$(cat <<'EOF'
...
EOF
)"
```

# Updating an existing PR

The description must reflect the **current full state** of the branch vs base — not a changelog of changes since the last push. Drop "also adds", "additionally", "now includes". Just describe what the PR does.

**Bad** (changelog style):
> Title: `Add retry logic and circuit breaker to HTTP client`
> "This PR now also adds a circuit breaker pattern…"

**Good** (current state):
> Title: `Add resilient HTTP client with retry and circuit breaker`
> "HTTP requests to external services fail under load. This PR wraps the HTTP client with exponential backoff retry and a circuit breaker that opens after repeated failures…"

# Worked example (non-trivial PR)

Title: `Use AnnotationHub sample sources for listening-test pair progress`

```markdown
## TL;DR

The soundboard UI overstated listening-test progress: a 160-pair test would show `71 / 113  63%` instead of `71 / 160  44%`, and could flip to `complete` while a third of the manifest had never been annotated. This PR reads the true pair count from AnnotationHub's `download_sample_sources` API and patches `total_pairs` / `completion_pct` / `status` before they reach BigQuery.

**Files to review (4, +342 / -7):**

| File | Why |
|---|---|
| `diffusify/listening_tests/sample_sources.py` *(new)* | Pure helpers. Start here. |
| `diffusify/listening_tests/bq_export.py` | Calls AnnotationHub per tier; applies the override. |
| `tests/diffusify_tests/test_lt_sample_sources.py` *(new)* | 10 unit tests for the helpers. |

## Root cause

`total_pairs` came from the annotation download CSV, which only contains pairs with ≥1 annotation. Unannotated pairs silently dropped out, so the percentage was always wrong by a different amount and `status=complete` could trigger before annotators saw every uploaded pair.

## Reviewer notes

**Match by `comparison_id`, not by model pair.** Tier projects are shared across many tests, so the same model pair appears under different test names…

**Falls back on every failure mode.** If the AnnotationHub fetch fails or returns malformed data, the helper logs and returns `None`; the export keeps the legacy denominator…
```

# Final checks

- Title: active voice, present tense, describes full scope.
- TL;DR (if present): two sentences, concrete example/number.
- Each Reviewer note: one bolded headline, one fact per note.
- No `Co-Authored-By`, no "Generated with…", no AI/Claude mentions.
- Links preserved on update.
- Description describes current state, not a changelog.
