#!/usr/bin/env python3
"""
Test script to verify ANTHROPIC_API_KEY is set correctly
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("\n" + "="*70)
print("API Key Configuration Test")
print("="*70 + "\n")

api_key = os.environ.get('ANTHROPIC_API_KEY')

if api_key:
    print("✅ ANTHROPIC_API_KEY is set!")
    print(f"   Preview: {api_key[:20]}...")
    print(f"   Length: {len(api_key)} characters")

    if api_key.startswith('sk-ant-'):
        print("✅ Key format looks correct (starts with sk-ant-)")
    else:
        print("⚠️  Warning: Key should start with 'sk-ant-'")

    print("\n✅ You can now run the app:")
    print("   python app.py")
else:
    print("❌ ANTHROPIC_API_KEY is NOT set!")
    print("\nPlease set it using ONE of these methods:\n")
    print("1. Create a .env file in this directory with:")
    print("   ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE\n")
    print("2. Export it in your terminal:")
    print("   export ANTHROPIC_API_KEY='sk-ant-api03-YOUR_KEY_HERE'\n")
    print("3. For Windows PowerShell:")
    print("   $env:ANTHROPIC_API_KEY='sk-ant-api03-YOUR_KEY_HERE'\n")
    print("Get your API key at: https://console.anthropic.com/")

print("\n" + "="*70 + "\n")
