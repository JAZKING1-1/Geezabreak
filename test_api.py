#!/usr/bin/env python
"""
Test script to verify Mailjet API connection
"""
import os
import sys

# Add the project directory to the Python path
sys.path.append('c:\\Users\\DevanshSharma\\Desktop\\FULL REBOOT')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from mailjet_rest import Client

def test_mailjet_api():
    """Test basic Mailjet API connectivity"""
    print("Testing Mailjet API connectivity...")

    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")

    if not api_key or not api_secret:
        print("❌ API keys not found")
        return False

    try:
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')

        # Try to get account information (this should work with valid credentials)
        result = mailjet.account.get()

        if result.status_code == 200:
            print("✅ Mailjet API connection successful!")
            print(f"Account: {result.json()}")
            return True
        else:
            print(f"❌ Mailjet API error: {result.status_code}")
            print(f"Response: {result.json()}")
            return False

    except Exception as e:
        print(f"❌ Error connecting to Mailjet API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mailjet_api()
    sys.exit(0 if success else 1)
