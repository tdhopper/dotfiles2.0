---
name: adversarial-validate
description: >-
  Validate a claim by running independent investigators to gather evidence, then skeptics
  to attempt refutation, then synthesize a verdict with confidence level. Use when the user
  says "validate this claim", "adversarial check", "is this actually true", "verify this",
  "adversarial validate", "fact-check this", "prove or disprove", or when the user makes a
  factual claim about the codebase and wants it stress-tested before acting on it. Also
  trigger when the user describes a production incident hypothesis that needs verification.
---

# Adversarial Validation

Validate a claim through two serialized phases: investigators gather evidence, then skeptics attempt refutation using that evidence. The phase separation prevents confirmation bias: investigators don't know what skeptics will attack, and skeptics get evidence they didn't gather.

**Common failure mode:** Investigators and skeptics reaching the same conclusion because they share framing. The phases must be independent. Skeptics receive only the claim, the evidence summaries, and a mandate to refute.

## Step 1: Frame the Claim

Extract from the user's input:
- **The claim:** A single, falsifiable statement. If the user gives multiple claims, validate each separately. If the claim is vague ("something is wrong with model X"), ask the user to sharpen it.
- **Context:** What prompted the claim? (Incident, code review, metric anomaly, intuition)
- **Scope:** What repos, files, or systems are relevant?

State the claim back in one sentence and confirm: "Validating: [claim]. Scope: [repos/systems]. Starting investigation."

## Step 2: Investigation Phase (parallel)

Spawn 3 investigators using the Agent tool, all in the same turn. Each investigates from a different angle. Use `subagent_type: "skeptical-reviewer"` for all three, but override their stance to investigator mode in the prompt.

**Investigator 1: Code path tracer**
```
Agent(
  subagent_type: "skeptical-reviewer",
  description: "Investigate code paths",
  prompt: "You are in INVESTIGATOR mode, not skeptic mode. Gather evidence, do not judge.

Claim: [the claim]
Your angle: Trace the code path. Read source files, follow function calls, verify behavior.
Scope: [repos/files to check]

Output numbered evidence items with file:line references. Note what you checked and what you found. Note what you could not check. Do NOT render a verdict."
)
```

**Investigator 2: History analyst**
```
prompt: "...Your angle: Check git log, blame, PR history. When was relevant code changed? What did the PR say? What did reviews flag? Look for related incidents or discussions."
```

**Investigator 3: Runtime evidence**
```
prompt: "...Your angle: Check configs, test fixtures, deployment state, environment variables. What does the system actually do vs. what code says it should do? Look for discrepancies between declared behavior and actual behavior."
```

All three run concurrently. Wait for all to complete before Phase 2.

## Step 3: Compile Evidence

Read all three investigator outputs. Compile a single evidence summary organized by theme (not by investigator). This summary is what the skeptics receive.

## Step 4: Refutation Phase (parallel)

Spawn 3 skeptics using the Agent tool, all in the same turn. Each uses a different refutation strategy. Use `subagent_type: "skeptical-reviewer"` with their default skeptic stance.

**Skeptic 1: Alternative explanation**
```
Agent(
  subagent_type: "skeptical-reviewer",
  description: "Refute via alternative explanation",
  prompt: "Attempt to refute this claim by arguing for a different conclusion from the same evidence.

Claim: [the claim]
Your strategy: Accept the evidence but argue it supports a different conclusion.

Evidence gathered by investigators:
[compiled evidence summary]

If you cannot construct a valid refutation, say so honestly. Do not manufacture doubt.
Rate your refutation strength: fatal / significant / minor / none.
Note what additional evidence would strengthen or weaken your refutation."
)
```

**Skeptic 2: Evidence quality attack**
```
prompt: "...Your strategy: Challenge the evidence itself. Is it stale? Misread? From the wrong branch? Does it prove what the investigators claim it proves?"
```

**Skeptic 3: Missing variable**
```
prompt: "...Your strategy: Argue that the investigation missed a critical factor. What wasn't checked? What system, config, or code path could change the conclusion?"
```

All three run concurrently. Wait for all to complete.

## Step 5: Verdict Synthesis

Read all skeptic outputs. Determine the verdict:

- **CONFIRMED:** Investigators found consistent evidence AND no skeptic produced a fatal or significant refutation.
- **REFUTED:** At least one skeptic produced a fatal refutation that the evidence does not counter.
- **UNCERTAIN:** Evidence is mixed or skeptics raised significant (not fatal) concerns that need resolution.
- **INSUFFICIENT:** Investigators could not gather enough evidence to judge.

## Output Format

```
## Adversarial Validation

### Claim
[The claim, one sentence]

### Verdict: [CONFIRMED | REFUTED | UNCERTAIN | INSUFFICIENT]
**Confidence:** high | medium | low

### Evidence Summary
[Compiled from all investigators, organized by theme]

### Refutation Attempts
| Skeptic | Strategy | Strength | Key argument |
|---------|----------|----------|--------------|
| 1 | Alternative explanation | none/minor/significant/fatal | [summary] |
| 2 | Evidence quality | ... | ... |
| 3 | Missing variable | ... | ... |

### Strongest Refutation
[If any skeptic raised a significant or fatal point, detail it here.
If none could refute: "No skeptic produced a significant refutation."]

### Reasoning
[Why the verdict is what it is. Cite specific evidence and refutation attempts.]

### Open Questions
[What would change the verdict. Actionable next steps if UNCERTAIN or INSUFFICIENT.]
```

## Step 6: Follow-up

If UNCERTAIN or INSUFFICIENT, propose specific follow-up actions: "Check production config X," "Run test Y with flag Z," "Ask [person] whether [assumption] holds."

If CONFIRMED or REFUTED, state it directly and suggest next steps based on the implication.
