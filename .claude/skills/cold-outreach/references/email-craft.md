# Email craft: anatomy, template, greeting rule, defaults

## Anatomy of a validation cold email

Keep it under ~120 words. Five moves, in order:

1. **Who you are + the signal.** One sentence of identity, then the real, per-prospect observation. The signal is what separates you from spam — it proves you looked at *them*.
2. **The recurring pain, named plainly.** One line. Make them nod. Don't explain their business back to them at length; gesture at the chore and move on.
3. **The offer.** Prefer a concierge free sample of their own work ("send me X and I'll hand back Y, free, this once"). Otherwise, a five-minute call. Describe the outcome, not the tech.
4. **The single ask.** A reply, or a short call. One thing. Optionally: "want to see it first? reply and I'll run a few of yours."
5. **Graceful opt-out.** "If it's not relevant, tell me and I'll leave you be."

Then the signature.

## Reusable template

Placeholders in [BRACKETS]. `[GREETING]` = `Hi [FirstName],` only when the name is confirmed; otherwise `Hi there,`.

```
Subject: [outcome or observation, lowercase, specific — e.g. "your next sale's catalog, done for you (free)"]

[GREETING]

I'm Tim Hopper. [one-line identity relevant to them], and [the real signal about THIS prospect]. [one line naming the recurring pain].

[The offer — concierge free sample of their own work, or a five-minute call. Outcome, not features.]

[Single low-friction ask. Optionally: offer to show a sample of their own first.]

If it's not useful, tell me and I'll leave you be.

Thanks,
Tim Hopper
tim.hopper@ehop.me
434-906-5120 · Brownsburg, IN
```

## The greeting rule (important)

- **Confirmed name on their page** → use the first name (`Hi Mark,`).
- **Name only inferred** from an email local-part, or no name found → `Hi there,`. Never guess. A wrong name is a faster delete than no name.

## Signature and hard line breaks

Tim's default identity and signature (satisfies the CAN-SPAM postal-identity + real-sender floor):

```
Tim Hopper
tim.hopper@ehop.me
434-906-5120 · Brownsburg, IN
```

When creating a Fastmail draft, the body is markdown and **single newlines collapse**, so the three signature lines would run onto one line. Force line breaks by ending each line with **two trailing spaces** (a markdown hard break):

```
Thanks,··
Tim Hopper··
tim.hopper@ehop.me··
434-906-5120 · Brownsburg, IN
```

(`··` = two literal spaces before the newline.) After creating a draft, it's worth reading one back to confirm the signature stacked correctly.

## Fastmail draft mechanics

- Tool: `mcp__fastmail__draft_email`. Load via ToolSearch if needed: `select:mcp__fastmail__draft_email,mcp__fastmail__list_identities`.
- `from`: `tim.hopper@ehop.me` (confirm available identities with `list_identities`).
- `to`: use the org name as the display name when the person's name isn't confirmed, e.g. `[{"name": "Graber Auctions", "email": "graberauctions@gmail.com"}]`.
- One draft per prospect. Subject and body personalized with that prospect's signal.
- To change the from-address or fix a body after the fact, delete the draft (`mcp__fastmail__delete_email`) and recreate — there's no in-place body edit.

## Deliverability discipline

- Send 5-8/day, not the whole list at once. Bursts of cold mail to consumer domains (gmail/yahoo/aol) get spam-foldered and erode the sending domain's reputation.
- Verify off-domain or low-confidence addresses before sending (a quick site/phone check) so they don't bounce.
- Never route cold outreach through transactional email APIs (Resend, etc.) — their terms discourage unsolicited mail and can suspend the account. Stage drafts in the real mailbox and send from there.

## Worked example (from a real campaign)

Buyer: clerk-treasurer at a small Indiana town. Signal: their meeting videos and minutes live on two pages that never link. Offer: a tool that auto-assembles the compliant page. Ask: a five-minute call.

```
Subject: your meeting videos and minutes on the Dunkirk website

Hi Kara,

I'm Tim Hopper, an Indiana resident who builds small web tools. I've been
looking at how Indiana towns post their public-meeting recordings, and I
noticed your website has a meeting-video page and a separate minutes page,
but the two don't link to each other.

[one line on the recurring chore] ... [the tool, as an outcome] ...

Who on your staff keeps the video, agenda, and minutes together after each
meeting, and honestly, how much of a hassle is it? A five-minute call would
help me a lot, and I'll share what I find either way.

If this isn't relevant to you, tell me and I won't follow up.

Thanks,
Tim Hopper
tim.hopper@ehop.me
434-906-5120 · Brownsburg, IN
```
