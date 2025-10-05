"""
Database models and connection management for Excel Insights
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from contextlib import contextmanager
import json


class Database:
    """Database connection and query manager."""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'excel_insights'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = psycopg2.connect(**self.db_config)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_cursor(self, conn):
        """Get a cursor that returns dictionaries."""
        return conn.cursor(cursor_factory=RealDictCursor)


# Global database instance
db = Database()


class User:
    """User model for authentication and tracking."""

    @staticmethod
    def get_by_username(username):
        """Get user by username from database."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            return cursor.fetchone()

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            return cursor.fetchone()

    @staticmethod
    def create_or_update(username, full_name=None):
        """Create or update user record (called after config file auth)."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                INSERT INTO users (username, full_name, last_login)
                VALUES (%s, %s, %s)
                ON CONFLICT (username)
                DO UPDATE SET
                    last_login = EXCLUDED.last_login,
                    full_name = COALESCE(EXCLUDED.full_name, users.full_name)
                RETURNING id, username, full_name, created_at, last_login
                """,
                (username, full_name, datetime.now())
            )
            return cursor.fetchone()


class Analysis:
    """Analysis session model."""

    @staticmethod
    def create(user_id, filename, run_id):
        """Create a new analysis record."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                INSERT INTO analyses
                (user_id, filename, run_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, user_id, filename, run_id, status, created_at
                """,
                (user_id, filename, run_id, 'pending', datetime.now())
            )
            return cursor.fetchone()

    @staticmethod
    def update_status(run_id, status, result_data=None):
        """Update analysis status and results."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                UPDATE analyses
                SET status = %s,
                    result_data = %s,
                    completed_at = CASE WHEN %s = 'completed' THEN %s ELSE completed_at END
                WHERE run_id = %s
                RETURNING id, status, completed_at
                """,
                (status, json.dumps(result_data) if result_data else None,
                 status, datetime.now(), run_id)
            )
            return cursor.fetchone()

    @staticmethod
    def get_by_run_id(run_id):
        """Get analysis by run_id."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                "SELECT * FROM analyses WHERE run_id = %s",
                (run_id,)
            )
            return cursor.fetchone()

    @staticmethod
    def get_user_analyses(user_id, limit=50):
        """Get all analyses for a user, ordered by most recent."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                SELECT id, filename, run_id, status, created_at, completed_at,
                       result_data
                FROM analyses
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )
            return cursor.fetchall()


class Conversation:
    """Conversation and message tracking."""

    @staticmethod
    def create(user_id, analysis_id, title=None):
        """Create a new conversation."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                INSERT INTO conversations
                (user_id, analysis_id, title, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, user_id, analysis_id, title, created_at
                """,
                (user_id, analysis_id, title, datetime.now(), datetime.now())
            )
            return cursor.fetchone()

    @staticmethod
    def add_message(conversation_id, role, content, metadata=None):
        """Add a message to a conversation."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                INSERT INTO messages
                (conversation_id, role, content, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, conversation_id, role, content, created_at
                """,
                (conversation_id, role, content,
                 json.dumps(metadata) if metadata else None, datetime.now())
            )
            # Update conversation timestamp
            cursor.execute(
                "UPDATE conversations SET updated_at = %s WHERE id = %s",
                (datetime.now(), conversation_id)
            )
            return cursor.fetchone()

    @staticmethod
    def get_messages(conversation_id):
        """Get all messages for a conversation."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                SELECT id, role, content, metadata, created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conversation_id,)
            )
            return cursor.fetchall()

    @staticmethod
    def get_user_conversations(user_id, limit=50):
        """Get all conversations for a user."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                SELECT c.id, c.title, c.created_at, c.updated_at,
                       a.filename, a.run_id,
                       (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
                FROM conversations c
                LEFT JOIN analyses a ON c.analysis_id = a.id
                WHERE c.user_id = %s
                ORDER BY c.updated_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )
            return cursor.fetchall()

    @staticmethod
    def get_by_analysis(analysis_id):
        """Get conversation by analysis ID."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                "SELECT * FROM conversations WHERE analysis_id = %s",
                (analysis_id,)
            )
            return cursor.fetchone()


class ActivityLog:
    """Track user activity and events."""

    @staticmethod
    def log_event(user_id, analysis_id, event_type, event_data=None):
        """Log an activity event."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                INSERT INTO activity_logs
                (user_id, analysis_id, event_type, event_data, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, analysis_id, event_type,
                 json.dumps(event_data) if event_data else None, datetime.now())
            )
            return cursor.fetchone()

    @staticmethod
    def get_user_activity(user_id, limit=100):
        """Get recent activity for a user."""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                """
                SELECT id, event_type, event_data, created_at,
                       a.filename, a.run_id
                FROM activity_logs al
                LEFT JOIN analyses a ON al.analysis_id = a.id
                WHERE al.user_id = %s
                ORDER BY al.created_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )
            return cursor.fetchall()
