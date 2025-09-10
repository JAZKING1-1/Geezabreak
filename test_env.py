#!/usr/bin/env python
"""
Test script to check environment variables
"""
import os
import sys

# Add the project directory to the Python path
sys.path.append('c:\\Users\\DevanshSharma\\Desktop\\FULL REBOOT')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

print("Environment Variables:")
print(f"MAILJET_API_KEY: {os.environ.get('MAILJET_API_KEY', 'NOT SET')}")
print(f"MAILJET_API_SECRET: {os.environ.get('MAILJET_API_SECRET', 'NOT SET')}")
print(f"FORMS_TO_EMAIL: {os.environ.get('FORMS_TO_EMAIL', 'NOT SET')}")
print(f"DEFAULT_FROM_EMAIL: {os.environ.get('DEFAULT_FROM_EMAIL', 'NOT SET')}")

# Test Mailjet client initialization
try:
    from mailjet_rest import Client
    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")

    if api_key and api_secret:
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        print("✅ Mailjet client initialized successfully")
    else:
        print("❌ Mailjet API keys not found")

except Exception as e:
    print(f"❌ Error initializing Mailjet client: {str(e)}")
