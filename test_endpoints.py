#!/usr/bin/env python
"""
Test alternative Mailjet API endpoints to verify authentication
"""
import os
import sys
from mailjet_rest import Client

# Add the project directory to the Python path
sys.path.append('c:\\Users\\DevanshSharma\\Desktop\\FULL REBOOT')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def test_mailjet_endpoints():
    """Test different Mailjet API endpoints"""
    print("🔍 Testing Mailjet API endpoints...")

    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")

    if not api_key or not api_secret:
        print("❌ API keys not found")
        return

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    endpoints = [
        ('Account', mailjet.account.get),
        ('Sender', mailjet.sender.get),
        ('Contact', mailjet.contact.get),
        ('Campaign', mailjet.campaign.get),
    ]

    for name, endpoint_func in endpoints:
        try:
            print(f"\n🔍 Testing {name} endpoint...")
            result = endpoint_func()
            print(f"Status: {result.status_code}")

            if result.status_code == 200:
                print(f"✅ {name} endpoint works!")
                return True
            elif result.status_code == 401:
                print(f"❌ {name} endpoint: Authentication failed")
            elif result.status_code == 404:
                print(f"⚠️ {name} endpoint: Not found (may be normal)")
            else:
                print(f"⚠️ {name} endpoint: Status {result.status_code}")

        except Exception as e:
            print(f"❌ {name} endpoint error: {str(e)}")

    return False

if __name__ == "__main__":
    success = test_mailjet_endpoints()
    if not success:
        print("\n" + "="*60)
        print("🚨 ACTION REQUIRED:")
        print("="*60)
        print("Your Mailjet API keys appear to be invalid or expired.")
        print("\nPlease:")
        print("1. Log into your Mailjet account at https://app.mailjet.com/")
        print("2. Go to Account Settings → API Keys")
        print("3. Verify your API Key and Secret are correct")
        print("4. If needed, regenerate new API keys")
        print("5. Make sure your account has sending permissions")
        print("6. Update the .env file with the correct keys")
        print("\nThen run this test again.")
