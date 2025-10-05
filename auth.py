"""
Authentication utilities for Excel Insights Dashboard
Handles user authentication via users.yaml with bcrypt password hashing
"""
import yaml
import bcrypt
from functools import wraps
from flask import session, redirect, url_for, flash, request
from pathlib import Path


class AuthManager:
    """Manage authentication using users.yaml configuration."""

    def __init__(self, config_path='users.yaml'):
        self.config_path = Path(config_path)
        self.users = self._load_users()

    def _load_users(self):
        """Load users from YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Users configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return {user['username']: user for user in config.get('users', [])}

    def reload_users(self):
        """Reload users from config file (useful after adding new users)."""
        self.users = self._load_users()

    def authenticate(self, username, password):
        """
        Authenticate user with username and password.

        Returns:
            dict: User data if authentication successful, None otherwise
        """
        user = self.users.get(username)

        if not user:
            return None

        # Verify password using bcrypt
        password_hash = user.get('password_hash', '').encode('utf-8')
        password_bytes = password.encode('utf-8')

        try:
            if bcrypt.checkpw(password_bytes, password_hash):
                # Return user data without password hash
                return {
                    'username': user['username'],
                    'full_name': user.get('full_name', username),
                    'role': user.get('role', 'user')
                }
        except (ValueError, TypeError):
            # Invalid hash format
            return None

        return None

    def get_user(self, username):
        """Get user data by username (without password hash)."""
        user = self.users.get(username)
        if user:
            return {
                'username': user['username'],
                'full_name': user.get('full_name', username),
                'role': user.get('role', 'user')
            }
        return None

    def get_all_users(self):
        """Get all users (without password hashes)."""
        return [
            {
                'username': user['username'],
                'full_name': user.get('full_name', user['username']),
                'role': user.get('role', 'user')
            }
            for user in self.users.values()
        ]

    def add_user(self, username, password, full_name=None, role='user'):
        """
        Add new user to users.yaml file.

        Args:
            username: Username
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role ('admin' or 'user')

        Returns:
            bool: True if successful, False if user already exists
        """
        if username in self.users:
            return False

        # Generate bcrypt hash
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Load current config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Add new user
        new_user = {
            'username': username,
            'full_name': full_name or username,
            'password_hash': password_hash,
            'role': role
        }

        config['users'].append(new_user)

        # Write back to file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Reload users
        self.reload_users()

        return True

    def update_user(self, username, password=None, full_name=None, role=None):
        """
        Update existing user in users.yaml.

        Args:
            username: Username to update
            password: New password (optional, will be hashed)
            full_name: New full name (optional)
            role: New role (optional)

        Returns:
            bool: True if successful, False if user not found
        """
        if username not in self.users:
            return False

        # Load current config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Find and update user
        for user in config['users']:
            if user['username'] == username:
                if password:
                    user['password_hash'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                if full_name:
                    user['full_name'] = full_name
                if role:
                    user['role'] = role
                break

        # Write back to file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Reload users
        self.reload_users()

        return True

    def delete_user(self, username):
        """
        Delete user from users.yaml.

        Args:
            username: Username to delete

        Returns:
            bool: True if successful, False if user not found or is admin
        """
        if username not in self.users:
            return False

        # Prevent deleting admin
        if self.users[username].get('role') == 'admin' and username == 'admin':
            return False

        # Load current config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Remove user
        config['users'] = [u for u in config['users'] if u['username'] != username]

        # Write back to file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Reload users
        self.reload_users()

        return True

    @staticmethod
    def hash_password(password):
        """Generate bcrypt hash for a password (utility function)."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Flask decorators for route protection
def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('אנא התחבר כדי לגשת לדף זה', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('אנא התחבר כדי לגשת לדף זה', 'warning')
            return redirect(url_for('login', next=request.url))

        if session['user'].get('role') != 'admin':
            flash('נדרשות הרשאות מנהל לגשת לדף זה', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function
