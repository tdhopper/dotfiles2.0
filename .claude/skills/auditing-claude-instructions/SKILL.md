---
name: auditing-claude-instructions
description: Use this skill when evaluating, auditing, reviewing, or optimizing CLAUDE.md files (or agents.md files) for effectiveness. Triggers on "review my CLAUDE.md", "optimize my claude instructions", "is my CLAUDE.md effective", "audit my claude config", or when users share their CLAUDE.md content for feedback. Evaluates files against a research-backed rubric covering minimality, tooling, codebase overviews, novelty, and authorship.
---

# Auditing Claude Instructions

Evaluate CLAUDE.md and agents.md files against a research-backed rubric. Score each file on 5 criteria (4 points each, 20 max) and provide actionable recommendations.

## Evaluation Process

### 1. Locate the File

```bash
fd -H "CLAUDE.md" .
fd -H "agents.md" .
```

### 2. Gather Context

Before scoring, check what other documentation exists in the repo:

```bash
fd -H "README.md" .
fd -d 1 . docs/ 2>/dev/null
```

This informs the Novelty vs. Redundancy criterion—instructions that duplicate README content are actively harmful.

### 3. Score Against Rubric

Apply each criterion from `./scoring-rubric.md`. For every criterion, assign a score of 4 (Excellent), 3 (Satisfactory), or 1 (Needs Improvement).

**The 5 criteria:**

1. **Minimality of Requirements** — Only what's needed to interact with the repo. Extra instructions increase exploration time and raise inference costs by 20%+.
2. **Specification of Tooling and Environment** — Explicit tool names and commands. Agents strictly adhere to specified tools.
3. **Absence of Codebase Overviews** — No enumerated directories or file summaries. Research shows overviews don't help agents find files faster and can cause models to waste steps re-reading context.
4. **Novelty vs. Redundancy** — Unique operational context not found elsewhere in the repo. Redundancy with README/docs only helps if all other docs are deleted.
5. **Authorship and Curation** — Human-written or heavily human-edited. Purely LLM-generated files reduce task success rates by 3% on average.

### 4. Generate Report

## Output Format

```markdown
## CLAUDE.md Audit Report

### Scores

| Criterion | Score | Rating |
|-----------|-------|--------|
| Minimality of Requirements | X/4 | [Excellent/Satisfactory/Needs Improvement] |
| Tooling and Environment | X/4 | [Excellent/Satisfactory/Needs Improvement] |
| Absence of Codebase Overviews | X/4 | [Excellent/Satisfactory/Needs Improvement] |
| Novelty vs. Redundancy | X/4 | [Excellent/Satisfactory/Needs Improvement] |
| Authorship and Curation | X/4 | [Excellent/Satisfactory/Needs Improvement] |
| **Total** | **X/20** | |

### Findings

#### [Criterion Name] — [Score]/4
**Evidence**: [Quote or reference specific lines]
**Issue**: [What's wrong and why it matters, citing research]
**Fix**: [Concrete rewrite or removal]

### Recommended Rewrite

[If score < 16, provide a complete rewritten version of the file]
```

## Scoring Thresholds

- **17-20**: Well-optimized file. Minor tweaks only.
- **13-16**: Functional but has clear areas for improvement.
- **9-12**: Significant issues reducing agent effectiveness.
- **5-8**: File is likely hurting more than helping. Consider a full rewrite.

## Key Principles

- **Cut aggressively**: For every line, ask "Would removing this cause the agent to make mistakes?" If no, cut it.
- **Commands over prose**: Replace explanatory paragraphs with runnable commands.
- **Detect LLM generation**: Watch for telltale signs—exhaustive file trees, generic advice ("write clean code"), walls of boilerplate. These indicate an unedited LLM-generated file.
- **Check for README duplication**: If content appears in both CLAUDE.md and README.md, it should be removed from CLAUDE.md.
- **Verify tooling specificity**: Vague references like "run the tests" should be `pytest -x` or `npm test`.
