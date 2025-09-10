#!/usr/bin/env python
"""
Detailed Mailjet API test to debug 401 error
"""
import os
import sys
from mailjet_rest import Client

# Add the project directory to the Python path
sys.path.append('c:\\Users\\DevanshSharma\\Desktop\\FULL REBOOT')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def test_mailjet_api():
    """Test Mailjet API with detailed error reporting"""
    print("🔍 Testing Mailjet API connection...")

    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")

    print(f"API Key: {api_key[:10]}..." if api_key else "NOT SET")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "NOT SET")

    if not api_key or not api_secret:
        print("❌ API keys not found in environment")
        return False

    try:
        # Initialize Mailjet client
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        print("✅ Mailjet client initialized")

        # Test API connection with a simple request
        print("🔍 Testing API connectivity...")
        result = mailjet.contact.get()

        print(f"API Response Status: {result.status_code}")
        print(f"API Response: {result.json()}")

        if result.status_code == 200:
            print("✅ Mailjet API connection successful!")
            return True
        else:
            print(f"❌ Mailjet API error: {result.status_code}")
            print(f"Response: {result.json()}")
            return False

    except Exception as e:
        print(f"❌ Error testing Mailjet API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_email_sending():
    """Test actual email sending"""
    print("\n📧 Testing email sending...")

    try:
        # Import Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')
        import django
        django.setup()

        from core.emails import send_form_email

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

        result = send_form_email(
            subject="Mailjet Integration Test - Debug",
            template_name="emails/feedback.html",
            context={"feedback": feedback}
        )

        print(f"Send result status: {result.status_code}")
        print(f"Send result: {result.json()}")

        if result.status_code == 200:
            print("✅ Email sent successfully!")
            return True
        else:
            print(f"❌ Email sending failed: {result.status_code}")
            print(f"Response: {result.json()}")
            return False

    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MAILJET DEBUG TEST")
    print("=" * 50)

    api_test = test_mailjet_api()
    email_test = test_email_sending()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"API Connection: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"Email Sending: {'✅ PASS' if email_test else '❌ FAIL'}")

    if not api_test:
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if your Mailjet API keys are correct")
        print("2. Verify your Mailjet account is active")
        print("3. Check if you have sending permissions")
        print("4. Try regenerating your API keys in Mailjet dashboard")

    sys.exit(0 if api_test and email_test else 1)
