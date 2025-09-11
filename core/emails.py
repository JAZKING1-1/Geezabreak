import logging

logger = logging.getLogger(__name__)

def send_form_email(subject: str, message: str, recipient: str):
    """
    Temporary fallback email sender for production while Mailjet is disabled.
    Instead of sending a real email, this will log the message. Your forms
    can keep calling this function exactly as before.
    """
    log_message = (
        "\n--- FAKE EMAIL SEND ---\n"
        f"To: {recipient}\n"
        f"Subject: {subject}\n"
        f"Message:\n{message}\n"
        "------------------------"
    )
    logger.info(log_message)
    print(log_message)  # also shows in console/Render logs
    return True
