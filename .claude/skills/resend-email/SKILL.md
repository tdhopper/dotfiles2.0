---
name: resend-email
description: Send emails via Resend.com API. Use when the user wants to (1) send an email, (2) email someone, (3) send a message to an email address, (4) send email with attachments, (5) schedule an email for later. Requires RESEND_API_KEY environment variable.
---

# Resend Email

Send emails via the Resend.com API using `RESEND_API_KEY` environment variable.

## Sending Email

Use `scripts/send_email.py` to send emails:

```bash
python3 scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Hello" \
  --from "Your Name <you@yourdomain.com>" \
  --text "Email body here"
```

### Required Parameters

| Parameter | Description |
|-----------|-------------|
| `--to` | Recipient(s), comma-separated for multiple |
| `--subject` | Email subject line |
| `--from` | Sender address (format: `Name <email>` or just `email`) |
| `--text` or `--html` | Body content (at least one required) |

### Optional Parameters

| Parameter | Description |
|-----------|-------------|
| `--html` | HTML body content |
| `--text` | Plain text body |
| `--cc` | CC recipient(s), comma-separated |
| `--bcc` | BCC recipient(s), comma-separated |
| `--reply-to` | Reply-to address(es), comma-separated |
| `--attachment` | File path to attach (repeat flag for multiple) |
| `--scheduled-at` | Schedule delivery (ISO 8601 or natural language) |

### Examples

**Simple text email:**
```bash
python3 scripts/send_email.py \
  --to "user@example.com" \
  --subject "Quick update" \
  --from "sender@domain.com" \
  --text "Just a quick note."
```

**HTML email with friendly name:**
```bash
python3 scripts/send_email.py \
  --to "user@example.com" \
  --subject "Newsletter" \
  --from "Company <news@company.com>" \
  --html "<h1>Hello</h1><p>Welcome to our newsletter.</p>"
```

**With attachments:**
```bash
python3 scripts/send_email.py \
  --to "user@example.com" \
  --subject "Report attached" \
  --from "sender@domain.com" \
  --text "Please find the report attached." \
  --attachment "/path/to/report.pdf" \
  --attachment "/path/to/data.csv"
```

**Multiple recipients with CC:**
```bash
python3 scripts/send_email.py \
  --to "alice@example.com,bob@example.com" \
  --cc "manager@example.com" \
  --subject "Team update" \
  --from "sender@domain.com" \
  --text "Hi team..."
```

**Scheduled email:**
```bash
python3 scripts/send_email.py \
  --to "user@example.com" \
  --subject "Reminder" \
  --from "sender@domain.com" \
  --text "Don't forget!" \
  --scheduled-at "2024-12-25T09:00:00Z"
```

### Output

Returns JSON with `id` on success:
```json
{"id": "49a3999c-0ce1-4ea6-ab68-afcd6dc2e794"}
```

Returns JSON with `error` on failure.

## Limits

- Max 50 recipients per email
- Max 40MB total size (including base64-encoded attachments)
- Sender domain must be verified in Resend dashboard
