#!/usr/bin/env python
import os
import django
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings

print('🔄 Testing Geeza Break Email Functionality')
print('=' * 50)
print(f'Email backend: {settings.EMAIL_BACKEND}')
print(f'From email: {getattr(settings, "DEFAULT_FROM_EMAIL", "not set")}')
print(f'Recipients: {getattr(settings, "REFERRAL_NOTIFICATION_RECIPIENTS", [])}')
print(f'Email host: {getattr(settings, "EMAIL_HOST", "not set")}')
print(f'Email port: {getattr(settings, "EMAIL_PORT", "not set")}')
print(f'Email user: {getattr(settings, "EMAIL_HOST_USER", "not set")}')
print(f'Email TLS: {getattr(settings, "EMAIL_USE_TLS", "not set")}')
print()

# Test message
subject = 'Geeza Break Email Test - App Password Update'
message = f'''Hello!

This is a test email sent at {datetime.datetime.now()} to verify that your Gmail app password update is working correctly.

If you receive this email, it means:
✅ Gmail SMTP settings are correct
✅ App password is working
✅ Django email backend is configured properly

Your referral forms, feedback forms, and volunteer interest forms should now be sending emails successfully.

Test Details:
- Email backend: {settings.EMAIL_BACKEND}
- From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@geezabreak.org.uk')}
- To: {', '.join(getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', ['ds16022004@gmail.com']))}

Best regards,
Geeza Break Development Team
'''

try:
    print('📤 Attempting to send test email...')
    result = send_mail(
        subject,
        message,
        getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@geezabreak.org.uk'),
        getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', ['ds16022004@gmail.com']),
        fail_silently=False
    )
    print(f'✅ SUCCESS! Email sent successfully! Result: {result}')
    print('📧 Check your Gmail inbox (and spam folder) for the test email.')
    print()
    print('🎉 Your email functionality is working correctly!')
    print('All forms (referral, feedback, volunteer interest) should now send emails.')

except Exception as e:
    print(f'❌ FAILED: Email could not be sent: {str(e)}')
    print()
    print('🔧 Troubleshooting steps:')
    print('1. Verify your Gmail app password is correct')
    print('2. Check that 2-factor authentication is enabled on Gmail')
    print('3. Make sure the app password has no spaces: naogtjxenkjmcvbc')
    print('4. Try regenerating the app password in Gmail')
    import traceback
    traceback.print_exc()
