#!/usr/bin/env python3
"""Test script to verify database schema has email fields"""
import sys
from database import Database

try:
    db = Database()
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Check if email fields exist
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name IN ('email', 'email_notifications')
            ORDER BY column_name
        """)

        cols = cursor.fetchall()

        if len(cols) == 2:
            print("✓ Database connection successful")
            print("✓ Email fields found in users table:")
            for col in cols:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            sys.exit(0)
        else:
            print("✗ Email fields not found or incomplete")
            print(f"  Found {len(cols)} fields, expected 2")
            sys.exit(1)

except Exception as e:
    print(f"✗ Database connection or query failed: {e}")
    sys.exit(1)
