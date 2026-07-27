---
name: cold-outreach
description: >-
  Run a disciplined cold-outreach campaign to VALIDATE a product or business
  idea — find real, reachable prospects, draft signal-led personalized emails
  with one low-friction ask, and stage them as Fastmail drafts (never
  auto-sent). Use this whenever Tim wants to test an idea by talking to real
  buyers: "reach out to some [X] about [idea]", "cold email these people",
  "build an outreach list", "who could I talk to to validate this", "draft
  outreach for the [X] idea", a concierge/free-sample pilot offer, or first-ten-
  customer / first-invoice validation. Trigger even when he doesn't say "cold
  outreach" — if the underlying job is finding and contacting strangers to learn
  whether an idea is real, this is the skill. Do NOT use it for warm replies to
  existing threads, marketing copy for a website, or mass promotional blasts.
---

# Cold Outreach for Idea Validation

The goal of a cold-outreach campaign is **to learn, not to sell.** You are buying a fast, cheap yes/no on whether a real buyer has the painful problem you think they have, and whether they'll act. A signed pilot is the win; a clear "nobody cares" for the price of a few emails is *also* a win, because it saves months. Hold that frame the whole way through — it changes every decision below.

The failure mode to avoid: spraying generic pitches at a vague audience. That teaches you nothing and burns the list. Everything here pushes the opposite way — one buyer, one real signal per person, one ask.

## The one-line constraint

Before writing a single email, pin these down. If any is fuzzy, the campaign will be too.

> **One buyer × one recurring painful job × one promise × one CTA × one kill bar.**

- **One buyer** — a specific role at a specific kind of org, or a specific kind of person. Not "small businesses." "The clerk-treasurer at a small Indiana town." "The owner of a single-location estate auction house."
- **One recurring painful job** — something that hurts *repeatedly*, costs money/time/risk, and that they can't easily ignore.
- **One promise** — the outcome you deliver, in their words, not your feature list.
- **One CTA** — a five-minute call, or a free concierge sample. Never a menu.
- **One kill bar** — decided *now*, in writing: "If I can't land N conversations / N paying pilots from ~M contacts, I kill or pivot." Without this, a dead idea limps for months.

State these back to Tim and get a nod before building the list. Getting the buyer wrong wastes the whole campaign, so it's worth 60 seconds.

## Step 1 — Define the buyer and the signal

A **signal** is observable evidence that a specific prospect probably has the pain *right now*. It's what makes a cold email land as "this person actually looked at us" instead of spam. Good signals are concrete and per-prospect:

- A public artifact that reveals the pain (a thin catalog, a broken compliance page, a manual spreadsheet, a job posting for the work you'd automate).
- A recent trigger (a new law, a migration, an outage, a new hire, a funding event).
- Visible spend on a worse workaround (they pay a vendor that doesn't solve it).

Write down the exact signal you'll look for. It becomes both the list-filter and the first line of every email.

## Step 2 — Build the target list

Aim for ~20-30 verified prospects. This is research, and it's often best handed to a subagent (or several in parallel) so the main thread stays clean. Whoever does it, the rules are strict because a single fabricated detail poisons trust:

- **Never invent a contact, a name, or a fact.** Only include an email/name read directly off the org's own site or a listing page. If no email is verifiable, record the contact-page URL and phone instead — a blank beats a wrong address.
- **Never invent familiarity or the signal.** Each prospect's signal must be a real observation. If you didn't see it, don't claim it.
- **Only use a first name when it's confirmed** on their page. Names guessed from an email local-part ("j.smith@") are *not* confirmed — use a neutral greeting for those. A wrong name on a cold email is a fast delete.
- **Flag confidence** per row (address verified? profile fits?) so low-confidence ones get a human check before sending.

Capture per prospect: org, location, the platform/context, contact name (only if confirmed) + role, verified email (or contact URL + phone), the real signal (one line), and a confidence flag.

## Step 3 — Draft the emails

Read `~/.claude/PROSE.md` and follow it — these are short, human, and land best when they read like one real person wrote them, not a template. See `references/email-craft.md` for the full anatomy, the reusable template, the greeting rule, and Tim's signature/identity defaults. The essentials:

- **Open with the prospect's real signal.** First sentence proves you looked. This is the whole reason cold outreach works.
- **One problem → one outcome.** Name the recurring pain, then the result you deliver. Skip the feature tour.
- **Lead with a concierge free sample when you can.** "Send me your next sale's photos and I'll hand back finished catalog records, free, this once" beats "want to buy my SaaS." Doing a slice of their real work is the most persuasive demo and the cleanest willingness-to-pay test: someone who won't take a free sample of their own job will never pay. When a sample isn't feasible, the ask is a five-minute call.
- **One low-friction CTA.** A reply, a short call — not a link, a signup, and a Discord invite all at once. At validation stage you want the *conversation*; a link quietly swaps the ask to "go evaluate my product alone" and kills reply rate.
- **Graceful opt-out.** A line like "if it's not relevant, tell me and I'll leave you be" is respectful, improves replies, and covers the CAN-SPAM spirit.
- **No product link in the first email** unless it's a live, personalized artifact (their own data). A generic marketing page is a pamphlet; skip it.

**Compliance floor** (US commercial email): a truthful subject and sender, a real postal identity (city/town is fine for a solo sender), and a working opt-out. The signature defaults in `references/email-craft.md` satisfy this.

## Step 4 — Stage as Fastmail drafts (never auto-send)

Create each as a **draft**, never a send. Cold outreach to strangers is Tim's call to send, one glance per email, and drafts also let him fix the low-confidence rows first.

- Use the fastmail MCP `draft_email` tool. If it isn't loaded, load it via ToolSearch (`select:mcp__fastmail__draft_email,mcp__fastmail__list_identities`). If the fastmail MCP has no write tools, the auth may need refreshing (`/mcp`); fall back to a paste-ready doc only if drafts truly aren't possible.
- **From** Tim's chosen identity — default `tim.hopper@ehop.me` (the full-name address reads as a real person; confirm with `list_identities`).
- **Signature needs hard line breaks.** Markdown collapses single newlines, so the signature lines run together. End each signature line with two trailing spaces (a markdown hard break). See the template.
- Verify low-confidence / off-domain addresses before they're sent (note it in the draft or a task) so they don't bounce.
- **Deliverability: small daily batches, not a blast.** 20-30 cold emails fired at once — especially to consumer domains (gmail/yahoo/aol) — risks spam-foldering and hurts the sending domain's reputation, which Tim also uses for real mail. 5-8/day keeps it clean and keeps replies manageable around a full-time job. Resend and other *transactional* email tools are the wrong channel for cold sends (their terms discourage it and can suspend the account) — stage drafts in the real mailbox instead.

## Step 5 — Track and honor the kill bar

Give Tim a simple tracker (a doc, or one OmniFocus task per prospect with the draft reference in the note). Columns that matter:

`Prospect · Contact · Signal · Draft staged? · Sent? · Replied? · Call/sample done? · Paid or verbal-yes? · Next step`

Then hold the kill bar you set in the constraint. Count real conversations and real yeses, not opens. If the warm, free-sample offer can't convert against the alternatives after the target number of contacts, that's the answer — shelve it cheaply and move on. If it converts, the campaign earned the next stage.

## Quick reference

- Email anatomy, template, greeting rule, signature defaults: `references/email-craft.md`
- The mindset in one line: you're spending a few emails to buy the truth about an idea. Optimize for a fast, honest answer, not for looking impressive.
