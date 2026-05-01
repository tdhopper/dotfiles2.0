---
name: reviewing-code
description: Review pull requests, branch changes, or code diffs. Triggers on "review this PR", "review my changes", "code review", "review branch", or GitHub PR URLs. Focuses on bugs, tests, complexity, and performance - not linting.
---

# Code Review

Focus on substantive issues: bugs, missing tests, complexity, performance, duplication, incomplete implementations. Skip linting concerns (formatting, imports, naming style).

## Step 1: Get the Diff

- PR: `gh pr view NUMBER --json title,body,files` then `gh pr diff NUMBER`
- Branch: `git diff origin/master...HEAD`
- Uncommitted: `git diff`

## Step 2: External Review (Codex)

Check for Codex availability:

```bash
command -v codex >/dev/null 2>&1 && echo "Codex available"
```

**If Codex is available, you MUST run it before proceeding.** Do not skip this step.

- Local branch: `codex review --config model_reasoning_effort="high" --base BASE_BRANCH`
- Remote PR: `gh pr diff NUMBER | codex review --config model_reasoning_effort="high" -`

Run Codex in the background while you do your own review in parallel.

## Step 3: Your Own Review

Gather context: PR description, commit messages, project CLAUDE.md.

Review each file for:

- **Completeness**: All code paths handled? Stubs left behind?
- **Tests**: Added? Meaningful? Edge cases covered?
- **Complexity**: Justified abstractions? Simpler alternatives?
- **Performance**: Hot path regressions? Unbatched I/O?
- **Duplication**: Similar code already exists? (`rg "pattern"`)

**In scope**: Logic errors, missing error handling, test gaps, performance regressions, unnecessary complexity, duplication, incomplete implementations, project guideline violations.

**Out of scope** (linters handle): Formatting, import order, naming style, type annotations, docstring format.

## Step 4: Triage and Auto-Fix Obvious Issues

Once you have both your review and the Codex review, merge the findings and split them into two buckets:

**Bucket A — Obvious fixes** (clear bugs, typos, missing null checks, off-by-one errors, trivial test gaps where the fix is unambiguous): If and only if I am the author of the code, fix these silently. Don't ask about them: just do it and note what you fixed. Otherwise discuss in step 5.

**Bucket B — Judgment calls** (design trade-offs, architectural concerns, performance questions, ambiguous behavior, missing tests where the right test isn't obvious, things that might be intentional): These go to the interactive discussion in Step 5.

## Step 5: Present All Findings

Present **all** Bucket B findings at once in a list. For each finding include:

- What the issue is and where (`file:line`)
- Whether Codex and Claude agree or disagree
- Your suggested fix or concern

Also list what you already auto-fixed from Bucket A so Tim has full visibility. Present all the issues before stopping to fix anything.

Then use a series of `AskUserQuestion` asking Tim to classify each item as one of:
- **Fix** — agent will fix it
- **Flag** — add to concerns list for the PR author
- **Skip** — not worth addressing

## Step 6: Execute and Summarize

Fix everything Tim marked "Fix". Then present a final summary:

```markdown
## Auto-Fixed (Bucket A)
- [list of obvious fixes you made silently]

## Fixed (Bucket B — Tim approved)
- [list of judgment-call fixes Tim chose to fix]

## To Raise with PR Author
- [concerns Tim chose to flag, with file:line references]
```

**Do NOT post comments on the PR.** Tim will handle that himself. Just present the summary so he can copy or adapt it.
