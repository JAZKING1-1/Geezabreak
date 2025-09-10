#!/usr/bin/env python
"""
Test script to verify Mailjet email functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('c:\\Users\\DevanshSharma\\Desktop\\FULL REBOOT')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')
django.setup()

from core.emails import send_form_email

def test_mailjet():
    """Test Mailjet email sending"""
    print("Testing Mailjet email functionality...")

    # Create a mock feedback object
    class MockFeedback:
        def __init__(self):
            self.name = "Test User"
            self.contact_number = "01234567890"
            self.email = "test@example.com"
            self.service_used = "test"
            self.message = "This is a test email from the Mailjet integration test."

        def get_service_used_display(self):
            return "Test Service"

    feedback = MockFeedback()

    try:
        result = send_form_email(
            subject="Mailjet Integration Test",
            template_name="emails/feedback.html",
            context={"feedback": feedback}
        )

        print("✅ Mailjet test successful!")
        print(f"Response: {result}")
        return True

    except Exception as e:
        print(f"❌ Mailjet test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mailjet()
    sys.exit(0 if success else 1)
