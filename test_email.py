#!/usr/bin/env python#!/usr/bin/env python#!/usr/bin/env python#!/usr/bin/env python

import os

import djangoimport os



# Setup Djangoimport djangoimport osimport os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')

django.setup()import datetime



from main.utils.mailer import send_form_emailimport djangoimport django

from django.conf import settings

# Setup Django

print('Testing Geeza Break Email Functionality with Mailjet')

print('=' * 50)os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')import datetimeimport datetime

print(f'Mailjet API Key: {settings.MAILJET_API_KEY[:10]}...' if settings.MAILJET_API_KEY else 'Not set')

print(f'From email: {settings.DEFAULT_FROM_EMAIL}')django.setup()

print(f'Form recipients: {settings.FORM_RECIPIENTS}')

print()



subject = 'Geeza Break Email Test - Mailjet Integration'from main.utils.mailer import send_form_email

message = '''<h2>Hello!</h2>

<p>This is a test email to verify Mailjet integration.</p>from django.conf import settings# Setup Django# Setup Django

<p>If you receive this, the setup is working!</p>

'''



try:print('Testing Geeza Break Email Functionality with Mailjet')os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')

    print('Sending test email...')

    result = send_form_email(subject, message, settings.FORM_RECIPIENTS)print('=' * 50)

    print(f'SUCCESS! Result: {result}')

    print('Check your email inbox.')print(f'Mailjet API Key: {settings.MAILJET_API_KEY[:10]}...' if settings.MAILJET_API_KEY else 'Not set')django.setup()django.setup()

except Exception as e:

    print(f'FAILED: {str(e)}')print(f'Mailjet API Secret: {settings.MAILJET_API_SECRET[:10]}...' if settings.MAILJET_API_SECRET else 'Not set')

    import traceback

    traceback.print_exc()print(f'From email: {getattr(settings, "DEFAULT_FROM_EMAIL", "not set")}')

print(f'Form recipients: {getattr(settings, "FORM_RECIPIENTS", [])}')

print()from main.utils.mailer import send_form_emailfrom django.core.mail import send_mail, EmailMessage



# Test messagefrom django.conf import settingsfrom django.conf import settings

subject = 'Geeza Break Email Test - Mailjet Integration'

message = f'''<h2>Hello!</h2>



<p>This is a test email sent at {datetime.datetime.now()} to verify that your Mailjet integration is working correctly.</p>print('🔄 Testing Geeza Break Email Functionality with Mailjet')print('🔄 Testing Geeza Break Email Functionality')



<p>If you receive this email, it means the Mailjet setup is working.</p>print('=' * 50)print('=' * 50)



<p>Your referral forms, feedback forms, and volunteer interest forms should now be sending emails successfully.</p>print(f'Mailjet API Key: {settings.MAILJET_API_KEY[:10]}...' if settings.MAILJET_API_KEY else 'Not set')print(f'Email backend: {settings.EMAIL_BACKEND}')



<p><strong>Test Details:</strong></p>print(f'Mailjet API Secret: {settings.MAILJET_API_SECRET[:10]}...' if settings.MAILJET_API_SECRET else 'Not set')print(f'From email: {getattr(settings, "DEFAULT_FROM_EMAIL", "not set")}')

<ul>

<li>Mailjet API Key: {settings.MAILJET_API_KEY[:10]}...</li>print(f'From email: {getattr(settings, "DEFAULT_FROM_EMAIL", "not set")}')print(f'Recipients: {getattr(settings, "REFERRAL_NOTIFICATION_RECIPIENTS", [])}')

<li>From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@geezabreak.org')}</li>

<li>To: {', '.join(getattr(settings, 'FORM_RECIPIENTS', ['devansh.sharma@geezabreak.org.uk']))}</li>print(f'Form recipients: {getattr(settings, "FORM_RECIPIENTS", [])}')print(f'Email host: {getattr(settings, "EMAIL_HOST", "not set")}')

</ul>

print()print(f'Email port: {getattr(settings, "EMAIL_PORT", "not set")}')

<p>Best regards,<br>Geeza Break Development Team</p>

'''print(f'Email user: {getattr(settings, "EMAIL_HOST_USER", "not set")}')



try:# Test messageprint(f'Email TLS: {getattr(settings, "EMAIL_USE_TLS", "not set")}')

    print('Attempting to send test email via Mailjet...')

    to_emails = getattr(settings, 'FORM_RECIPIENTS', ['devansh.sharma@geezabreak.org.uk'])subject = 'Geeza Break Email Test - Mailjet Integration'print()

    result = send_form_email(subject, message, to_emails)

    print(f'SUCCESS! Email sent successfully! Result: {result}')message = f'''<h2>Hello!</h2>

    print('Check your email inbox (and spam folder) for the test email.')

    print()# Test message

    print('Your Mailjet email functionality is working correctly!')

    print('All forms (referral, feedback, volunteer interest) should now send emails.')<p>This is a test email sent at {datetime.datetime.now()} to verify that your Mailjet integration is working correctly.</p>subject = 'Geeza Break Email Test - App Password Update'



except Exception as e:message = f'''Hello!

    print(f'FAILED: Email could not be sent: {str(e)}')

    print()<p>If you receive this email, it means:</p>

    print('Troubleshooting steps:')

    print('1. Verify your Mailjet API keys are correct')<ul>This is a test email sent at {datetime.datetime.now()} to verify that your Gmail app password update is working correctly.

    print('2. Check that the sender email is verified in Mailjet')

    print('3. Ensure you have sufficient Mailjet credits')<li>✅ Mailjet API keys are correct</li>

    print('4. Check Mailjet dashboard for any errors')

    import traceback<li>✅ Mailjet REST API is working</li>If you receive this email, it means:

    traceback.print_exc()
<li>✅ Django mailer is configured properly</li>✅ Gmail SMTP settings are correct

</ul>✅ App password is working

✅ Django email backend is configured properly

<p>Your referral forms, feedback forms, and volunteer interest forms should now be sending emails successfully.</p>

Your referral forms, feedback forms, and volunteer interest forms should now be sending emails successfully.

<p><strong>Test Details:</strong></p>

<ul>Test Details:

<li>Mailjet API Key: {settings.MAILJET_API_KEY[:10]}...</li>- Email backend: {settings.EMAIL_BACKEND}

<li>From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@geezabreak.org')}</li>- From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@geezabreak.org.uk')}

<li>To: {', '.join(getattr(settings, 'FORM_RECIPIENTS', ['devansh.sharma@geezabreak.org.uk']))}</li>- To: {', '.join(getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', ['ds16022004@gmail.com']))}

</ul>

Best regards,

<p>Best regards,<br>Geeza Break Development Team</p>Geeza Break Development Team

''''''



try:try:

    print('📤 Attempting to send test email via Mailjet...')    print('📤 Attempting to send test email...')

    to_emails = getattr(settings, 'FORM_RECIPIENTS', ['devansh.sharma@geezabreak.org.uk'])    result = send_mail(

    result = send_form_email(subject, message, to_emails)        subject,

    print(f'✅ SUCCESS! Email sent successfully! Result: {result}')        message,

    print('📧 Check your email inbox (and spam folder) for the test email.')        getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@geezabreak.org.uk'),

    print()        getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', ['ds16022004@gmail.com']),

    print('🎉 Your Mailjet email functionality is working correctly!')        fail_silently=False

    print('All forms (referral, feedback, volunteer interest) should now send emails.')    )

    print(f'✅ SUCCESS! Email sent successfully! Result: {result}')

except Exception as e:    print('📧 Check your Gmail inbox (and spam folder) for the test email.')

    print(f'❌ FAILED: Email could not be sent: {str(e)}')    print()

    print()    print('🎉 Your email functionality is working correctly!')

    print('🔧 Troubleshooting steps:')    print('All forms (referral, feedback, volunteer interest) should now send emails.')

    print('1. Verify your Mailjet API keys are correct')

    print('2. Check that the sender email is verified in Mailjet')except Exception as e:

    print('3. Ensure you have sufficient Mailjet credits')    print(f'❌ FAILED: Email could not be sent: {str(e)}')

    print('4. Check Mailjet dashboard for any errors')    print()

    import traceback    print('🔧 Troubleshooting steps:')

    traceback.print_exc()    print('1. Verify your Gmail app password is correct')
    print('2. Check that 2-factor authentication is enabled on Gmail')
    print('3. Make sure the app password has no spaces: naogtjxenkjmcvbc')
    print('4. Try regenerating the app password in Gmail')
    import traceback
    traceback.print_exc()
