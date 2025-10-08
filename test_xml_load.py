#!/usr/bin/env python3
"""Test script to verify users.xml loads successfully"""
import sys
from auth import AuthManager

try:
    auth = AuthManager()
    users = auth.get_all_users()

    print("✓ users.xml loaded successfully")
    print(f"✓ Found {len(users)} users")
    print("\nUser details:")
    for user in users:
        print(f"  - {user['username']}:")
        print(f"    Full Name: {user['full_name']}")
        print(f"    Email: {user['email']}")
        print(f"    Role: {user['role']}")
        print(f"    Email Notifications: {user['email_notifications']}")

    # Test authentication
    demo_auth = auth.authenticate('demo', 'demo123')
    if demo_auth:
        print("\n✓ Authentication test successful (demo/demo123)")
        print(f"  Authenticated user: {demo_auth}")
    else:
        print("\n✗ Authentication test failed")
        sys.exit(1)

    sys.exit(0)

except Exception as e:
    print(f"✗ Failed to load users.xml: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
