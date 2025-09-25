import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_form_email(subject, template_name, context):
    """
    Send form email using Django's send_mail with Outlook SMTP.
    Renders the template and sends to the configured recipients.
    """
    try:
        # Render the email template
        html_message = render_to_string(template_name, context)

        # Get recipients from settings (supports comma-separated list)
        recipients_str = settings.FORMS_TO_EMAIL
        recipients = [email.strip() for email in recipients_str.split(',')]

        # Send the email
        send_mail(
            subject=subject,
            message="",  # Plain text version (empty for now)
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        logger.info(f"Email sent successfully: {subject} to {recipients}")
        print(f"Email sent successfully: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        print(f"EMAIL ERROR: {str(e)}")
        raise  # Re-raise to let calling code handle it
