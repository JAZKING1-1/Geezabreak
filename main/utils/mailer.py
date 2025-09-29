from django.conf import settings
from mailjet_rest import Client


def send_form_email(subject, body_text, recipients, html_body=None, reply_to_email=None):
    """
    Send an email via Mailjet HTTPS API.
    - Always CC Devansh.
    - Never raise on API errors (return False instead).
    - Supports TextPart + optional HTMLPart.
    """
    always_cc = ["devansh.sharma@geezabreak.org.uk"]
    final_recipients = sorted(set((recipients or []) + always_cc))

    client = Client(
        auth=(settings.MAILJET_API_KEY or "", settings.MAILJET_API_SECRET or ""),
        version="v3.1",
    )

    message = {
        "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": "Geeza Break Website"},
        "To": [{"Email": email} for email in final_recipients],
        "Subject": subject,
        "TextPart": body_text or "",
    }
    if html_body:
        message["HTMLPart"] = html_body
    if reply_to_email:
        message["ReplyTo"] = {"Email": reply_to_email}

    payload = {"Messages": [message]}

    try:
        result = client.send.create(data=payload)
        print("📤 Mailjet response:", result.status_code, result.json())
        return int(result.status_code) == 200
    except Exception as e:
        print("🚨 Mailjet send failed:", str(e))
        return False
