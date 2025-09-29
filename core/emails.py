import logging
from mailjet_rest import Client
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_form_email(subject, template_name, context):
    """
    Send form email using Mailjet REST API.
    Renders the template and sends to the configured recipients.
    """
    try:
        # Render the email template
        html_message = render_to_string(template_name, context)

        # Get recipients from settings (supports comma-separated list)
        recipients_str = settings.FORMS_TO_EMAIL
        recipients = [email.strip() for email in recipients_str.split(',')]

        # Send via Mailjet
        mailjet = Client(
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET),
            version="v3.1"
        )

        data = {
            "Messages": [
                {
                    "From": {
                        "Email": settings.DEFAULT_FROM_EMAIL,
                        "Name": "Geeza Break Website"
                    },
                    "To": [{"Email": email} for email in recipients],
                    "Subject": subject,
                    "HTMLPart": html_message,
                }
            ]
        }

        result = mailjet.send.create(data=data)
        logger.info(f"Mailjet response: {result.status_code} - {subject} to {recipients}")
        print(f"📤 Mailjet response: {result.status_code}")
        return result.status_code == 200

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        print(f"🚨 Mailjet send failed: {e}")
        raise  # Re-raise to let calling code handle it
