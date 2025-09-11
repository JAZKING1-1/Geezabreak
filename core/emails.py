import logging

logger = logging.getLogger(__name__)

def send_form_email(subject, template_name, context):
    """
    Temporary fallback email sender for production while Mailjet is disabled.
    Instead of sending a real email, this will log the message. Your forms
    can keep calling this function exactly as before.
    """
    log_message = (
        "\n--- FAKE EMAIL SEND ---\n"
        f"Subject: {subject}\n"
        f"Template: {template_name}\n"
        f"Context: {context}\n"
        "------------------------"
    )
    logger.info(log_message)
    print(log_message)  # also shows in console/Render logs
    return True
