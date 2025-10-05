"""
Authentication utilities for Excel Insights Dashboard
Handles user authentication via users.xml with bcrypt password hashing
"""
import xml.etree.ElementTree as ET
import bcrypt
from functools import wraps
from flask import session, redirect, url_for, flash, request
from pathlib import Path


class AuthManager:
    """Manage authentication using users.xml configuration."""

    def __init__(self, config_path='users.xml'):
        self.config_path = Path(config_path)
        self.users = self._load_users()

    def _load_users(self):
        """Load users from XML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Users configuration file not found: {self.config_path}")

        tree = ET.parse(self.config_path)
        root = tree.getroot()

        users = {}
        for user_elem in root.findall('user'):
            user = {
                'username': user_elem.find('username').text,
                'full_name': user_elem.find('full_name').text,
                'email': user_elem.find('email').text if user_elem.find('email') is not None else None,
                'password_hash': user_elem.find('password_hash').text,
                'role': user_elem.find('role').text,
                'email_notifications': user_elem.find('email_notifications').text.lower() == 'true' if user_elem.find('email_notifications') is not None else True
            }
            users[user['username']] = user

        return users

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
                    'email': user.get('email'),
                    'role': user.get('role', 'user'),
                    'email_notifications': user.get('email_notifications', True)
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
                'email': user.get('email'),
                'role': user.get('role', 'user'),
                'email_notifications': user.get('email_notifications', True)
            }
        return None

    def get_all_users(self):
        """Get all users (without password hashes)."""
        return [
            {
                'username': user['username'],
                'full_name': user.get('full_name', user['username']),
                'email': user.get('email'),
                'role': user.get('role', 'user'),
                'email_notifications': user.get('email_notifications', True)
            }
            for user in self.users.values()
        ]

    def add_user(self, username, password, full_name=None, email=None, role='user', email_notifications=True):
        """
        Add new user to users.xml file.

        Args:
            username: Username
            password: Plain text password (will be hashed)
            full_name: User's full name
            email: User's email address
            role: User role ('admin' or 'user')
            email_notifications: Enable email notifications

        Returns:
            bool: True if successful, False if user already exists
        """
        if username in self.users:
            return False

        # Generate bcrypt hash
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Parse XML
        tree = ET.parse(self.config_path)
        root = tree.getroot()

        # Create new user element
        user_elem = ET.SubElement(root, 'user')
        ET.SubElement(user_elem, 'username').text = username
        ET.SubElement(user_elem, 'full_name').text = full_name or username
        if email:
            ET.SubElement(user_elem, 'email').text = email
        ET.SubElement(user_elem, 'password_hash').text = password_hash
        ET.SubElement(user_elem, 'role').text = role
        ET.SubElement(user_elem, 'email_notifications').text = str(email_notifications).lower()

        # Write back to file with proper formatting
        self._indent_xml(root)
        tree.write(self.config_path, encoding='UTF-8', xml_declaration=True)

        # Reload users
        self.reload_users()

        return True

    def update_user(self, username, password=None, full_name=None, email=None, role=None, email_notifications=None):
        """
        Update existing user in users.xml.

        Args:
            username: Username to update
            password: New password (optional, will be hashed)
            full_name: New full name (optional)
            email: New email (optional)
            role: New role (optional)
            email_notifications: Enable/disable email notifications (optional)

        Returns:
            bool: True if successful, False if user not found
        """
        if username not in self.users:
            return False

        # Parse XML
        tree = ET.parse(self.config_path)
        root = tree.getroot()

        # Find and update user
        for user_elem in root.findall('user'):
            if user_elem.find('username').text == username:
                if password:
                    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    user_elem.find('password_hash').text = password_hash
                if full_name:
                    user_elem.find('full_name').text = full_name
                if email is not None:
                    email_elem = user_elem.find('email')
                    if email_elem is not None:
                        email_elem.text = email
                    else:
                        ET.SubElement(user_elem, 'email').text = email
                if role:
                    user_elem.find('role').text = role
                if email_notifications is not None:
                    notif_elem = user_elem.find('email_notifications')
                    if notif_elem is not None:
                        notif_elem.text = str(email_notifications).lower()
                    else:
                        ET.SubElement(user_elem, 'email_notifications').text = str(email_notifications).lower()
                break

        # Write back to file
        self._indent_xml(root)
        tree.write(self.config_path, encoding='UTF-8', xml_declaration=True)

        # Reload users
        self.reload_users()

        return True

    def delete_user(self, username):
        """
        Delete user from users.xml.

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

        # Parse XML
        tree = ET.parse(self.config_path)
        root = tree.getroot()

        # Remove user
        for user_elem in root.findall('user'):
            if user_elem.find('username').text == username:
                root.remove(user_elem)
                break

        # Write back to file
        self._indent_xml(root)
        tree.write(self.config_path, encoding='UTF-8', xml_declaration=True)

        # Reload users
        self.reload_users()

        return True

    def _indent_xml(self, elem, level=0):
        """Helper method to add pretty-printing indentation to XML."""
        indent = "\n" + "    " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent

    @staticmethod
    def hash_password(password):
        """Generate bcrypt hash for a password (utility function)."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Guest user utilities
def create_guest_session():
    """Create a guest session for anonymous users."""
    import uuid
    guest_id = str(uuid.uuid4())[:8]
    return {
        'username': f'guest_{guest_id}',
        'full_name': 'אורח',
        'role': 'guest',
        'is_guest': True,
        'guest_id': guest_id
    }


def is_guest_user():
    """Check if current session is a guest user."""
    return session.get('user', {}).get('is_guest', False)


def is_authenticated_user():
    """Check if current session is an authenticated (non-guest) user."""
    return 'user' in session and not session['user'].get('is_guest', False)


# Flask decorators for route protection
def login_required(f):
    """Decorator to require login OR guest access for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('אנא התחבר או המשך כאורח', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def registered_user_required(f):
    """Decorator to require registered user (no guests allowed)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('אנא התחבר כדי לגשת לדף זה', 'warning')
            return redirect(url_for('login', next=request.url))

        if is_guest_user():
            flash('תכונה זו זמינה רק למשתמשים רשומים. אנא התחבר או הירשם.', 'warning')
            return redirect(url_for('login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for a route (guests not allowed)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('אנא התחבר כדי לגשת לדף זה', 'warning')
            return redirect(url_for('login', next=request.url))

        if is_guest_user():
            flash('תכונה זו זמינה רק למשתמשים רשומים.', 'error')
            return redirect(url_for('index'))

        if session['user'].get('role') != 'admin':
            flash('נדרשות הרשאות מנהל לגשת לדף זה', 'error')
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function
