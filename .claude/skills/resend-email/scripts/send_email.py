#!/usr/bin/env python3
"""Send email via Resend API."""

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path


def send_email(
    to: str | list[str],
    subject: str,
    from_addr: str,
    html: str | None = None,
    text: str | None = None,
    cc: str | list[str] | None = None,
    bcc: str | list[str] | None = None,
    reply_to: str | list[str] | None = None,
    attachments: list[str] | None = None,
    scheduled_at: str | None = None,
) -> dict:
    """Send an email via Resend API.

    Args:
        to: Recipient email address(es), up to 50
        subject: Email subject line
        from_addr: Sender email (format: "Name <email@domain.com>" or "email@domain.com")
        html: HTML body content
        text: Plain text body (auto-generated from html if omitted)
        cc: Carbon copy recipient(s)
        bcc: Blind carbon copy recipient(s)
        reply_to: Reply-to address(es)
        attachments: List of file paths to attach
        scheduled_at: Schedule delivery (ISO 8601 or natural language)

    Returns:
        dict with 'id' of sent email on success, or 'error' on failure
    """
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        return {"error": "RESEND_API_KEY environment variable not set"}

    if not html and not text:
        return {"error": "Either html or text body is required"}

    # Build request payload
    payload = {
        "from": from_addr,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
    }

    if html:
        payload["html"] = html
    if text:
        payload["text"] = text
    if cc:
        payload["cc"] = [cc] if isinstance(cc, str) else cc
    if bcc:
        payload["bcc"] = [bcc] if isinstance(bcc, str) else bcc
    if reply_to:
        payload["reply_to"] = [reply_to] if isinstance(reply_to, str) else reply_to
    if scheduled_at:
        payload["scheduled_at"] = scheduled_at

    # Handle attachments
    if attachments:
        payload["attachments"] = []
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                return {"error": f"Attachment not found: {filepath}"}
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
            payload["attachments"].append({
                "filename": path.name,
                "content": content,
            })

    # Send request
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "resend-email-skill/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            return {"error": json.loads(error_body)}
        except json.JSONDecodeError:
            return {"error": error_body}


def main():
    parser = argparse.ArgumentParser(description="Send email via Resend API")
    parser.add_argument("--to", required=True, help="Recipient email(s), comma-separated")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--from", dest="from_addr", required=True, help="Sender email")
    parser.add_argument("--html", help="HTML body content")
    parser.add_argument("--text", help="Plain text body")
    parser.add_argument("--cc", help="CC recipient(s), comma-separated")
    parser.add_argument("--bcc", help="BCC recipient(s), comma-separated")
    parser.add_argument("--reply-to", help="Reply-to address(es), comma-separated")
    parser.add_argument("--attachment", action="append", help="File path to attach (can repeat)")
    parser.add_argument("--scheduled-at", help="Schedule delivery time")

    args = parser.parse_args()

    # Parse comma-separated addresses
    to = [e.strip() for e in args.to.split(",")] if "," in args.to else args.to
    cc = [e.strip() for e in args.cc.split(",")] if args.cc and "," in args.cc else args.cc
    bcc = [e.strip() for e in args.bcc.split(",")] if args.bcc and "," in args.bcc else args.bcc
    reply_to = [e.strip() for e in args.reply_to.split(",")] if args.reply_to and "," in args.reply_to else args.reply_to

    result = send_email(
        to=to,
        subject=args.subject,
        from_addr=args.from_addr,
        html=args.html,
        text=args.text,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
        attachments=args.attachment,
        scheduled_at=args.scheduled_at,
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if "id" in result else 1)


if __name__ == "__main__":
    main()
