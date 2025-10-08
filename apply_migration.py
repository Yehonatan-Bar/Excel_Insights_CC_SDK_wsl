#!/usr/bin/env python3
"""
Apply database migration for job state persistence
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def apply_migration():
    """Apply the job_state column migration."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'excel_insights'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }

    try:
        print("🔄 Connecting to database...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        print("📝 Applying migration: Add job_state column...")

        # Read migration file
        with open('migrations/001_add_job_state.sql', 'r') as f:
            migration_sql = f.read()

        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()

        print("✅ Migration applied successfully!")
        print("\nNew column 'job_state' added to analyses table.")
        print("Process persistence is now enabled!")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except FileNotFoundError:
        print("❌ Migration file not found: migrations/001_add_job_state.sql")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


if __name__ == '__main__':
    print("="*70)
    print("DATABASE MIGRATION - Process Persistence")
    print("="*70)
    print()

    success = apply_migration()

    if success:
        print()
        print("="*70)
        print("✅ MIGRATION COMPLETE")
        print("="*70)
        print("\nYou can now restart the application.")
        print("Active processes will persist across browser sessions!")
    else:
        print()
        print("="*70)
        print("❌ MIGRATION FAILED")
        print("="*70)
        print("\nPlease check the error messages above.")
