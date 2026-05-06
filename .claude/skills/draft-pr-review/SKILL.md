---
name: draft-pr-review
description: >-
  Post review findings as a pending (draft) GitHub review with inline comments.
  Use AFTER reviewing code (via /reviewing-code or manually) when Tim says
  "draft review", "post as draft", "create pending review", "leave draft comments",
  or asks to put review findings on the PR as inline comments.
---

# Draft PR Review

Post review findings as a **pending** GitHub review with inline comments on specific lines. The review is only visible to Tim until he edits and submits from the GitHub UI.

This skill handles the **output** step — it assumes findings already exist from a prior review (via `/reviewing-code`, Codex, or manual analysis). It does not re-analyze the code.

## Input

The skill needs:
1. A PR number (from argument, current conversation, or current branch)
2. A list of findings, each with: file path, line number, and description

If findings haven't been triaged yet, ask Tim which to include before posting.

## Comment format

Each inline comment has two sections:

```markdown
### [Short title]

[Author-facing feedback. Clear, actionable, respectful. 2-6 sentences.]

---

<details><summary>🔍 <b>Context for Tim</b></summary>

[Deeper analysis: code paths, snippets from the codebase, data flow,
concrete examples, Codex vs Claude agreement. Helps Tim understand
the issue fully before deciding whether to submit the comment.]

</details>
```

## Line numbers

- **New files**: `line` = line number in the file, `side` = `"RIGHT"`
- **Modified files** (added/changed lines): `line` = line number in the **new** file version, `side` = `"RIGHT"`
- **Deleted lines** (rare): `line` = line number in the **old** version, `side` = `"LEFT"`

Verify line numbers before posting:
```bash
git show origin/BRANCH:path/to/file.py | sed -n 'Np'
```

## Creating the pending review

```bash
# 1. Get the head commit SHA
COMMIT=$(gh pr view NUMBER --json headRefOid --jq '.headRefOid')

# 2. Post the review — omitting "event" makes it PENDING
gh api repos/{owner}/{repo}/pulls/NUMBER/reviews \
  -X POST --input /tmp/review-payload.json
```

Write the JSON payload to a file first (avoids shell escaping issues with backticks/quotes in comment bodies):

```json
{
  "commit_id": "abc123...",
  "body": "Overall summary — one or two sentences.",
  "comments": [
    {
      "path": "path/to/file.py",
      "line": 42,
      "side": "RIGHT",
      "body": "### Title\n\nAuthor-facing.\n\n---\n\n<details>..."
    }
  ]
}
```

Use the Write tool to create the JSON file, then pass it with `--input`. Do NOT construct the JSON inline in a shell heredoc — markdown in comment bodies will break.

## API reference

| Action | Command |
|--------|---------|
| Create pending review | `gh api repos/OWNER/REPO/pulls/N/reviews -X POST --input file.json` |
| Submit a pending review | `gh api repos/OWNER/REPO/pulls/N/reviews/ID/events -f event="COMMENT"` |
| Delete a pending review | `gh api repos/OWNER/REPO/pulls/N/reviews/ID -X DELETE` |
| List reviews (find ID) | `gh api repos/OWNER/REPO/pulls/N/reviews --jq '.[] \| {id,state,user: .user.login}'` |

## Constraints

- **Never submit the review.** Always leave it PENDING.
- **Never use `gh pr review --comment`** — that submits immediately and can't be batch-edited.
- If the API call fails (line out of range, bad path), diagnose and retry. Don't silently drop comments.
- If a finding spans multiple lines or files, pick the single most relevant line and reference other locations in the body.
- After success, report the review ID + comment count. Do NOT open the browser automatically.
