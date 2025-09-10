import os
from mailjet_rest import Client
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Load API keys from env
api_key = os.environ.get("MAILJET_API_KEY")
api_secret = os.environ.get("MAILJET_API_SECRET")
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

FROM = os.environ.get("DEFAULT_FROM_EMAIL")
TO   = os.environ.get("FORMS_TO_EMAIL")

def send_form_email(subject, template_name, context):
    """
    Sends an email via Mailjet with both HTML and plain text.
    template_name = path to a Django template (e.g. 'emails/referral.html')
    context = dictionary of values to pass into template
    """
    html = render_to_string(template_name, context)
    text = strip_tags(html)

    data = {
      'Messages': [{
        'From': {'Email': FROM, 'Name': 'Geeza Break Forms'},
        'To':   [{'Email': TO, 'Name': 'Geeza Break Staff'}],
        'Subject': subject,
        'TextPart': text,
        'HTMLPart': html
      }]
    }
    result = mailjet.send.create(data=data)
    return result
