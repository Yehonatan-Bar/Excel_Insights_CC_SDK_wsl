# Database Setup Guide

This guide explains how to set up PostgreSQL database for the Excel Insights Dashboard with user authentication and tracking.

## Prerequisites

- PostgreSQL 12 or higher installed
- Python 3.8+ with required packages (see requirements.txt)

## Database Setup Steps

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Start PostgreSQL service:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User

Connect to PostgreSQL as the postgres user:
```bash
sudo -u postgres psql
```

Create database and user:
```sql
CREATE DATABASE excel_insights;
CREATE USER excel_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE excel_insights TO excel_user;
\q
```

### 3. Initialize Database Schema

Run the initialization script:
```bash
psql -U excel_user -d excel_insights -f init_db.sql
```

Or connect and run manually:
```bash
psql -U excel_user -d excel_insights
```

Then paste the contents of `init_db.sql`.

### 4. Configure Environment Variables

Create or update `.env` file with database credentials:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=excel_insights
DB_USER=excel_user
DB_PASSWORD=your_secure_password

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

**Generate a secure SECRET_KEY:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 6. Initialize Default Users

The `init_db.sql` script creates a default admin user entry in the database.

User authentication is managed via `users.yaml`. Default users:

- **Admin**: username: `admin`, password: `admin123`
- **Demo**: username: `demo`, password: `demo123`

**⚠️ Important**: Change default passwords in production!

### 7. Add New Users

#### Option 1: Via Admin Panel (Recommended)
1. Log in as admin
2. Go to Admin Panel (🔧 button)
3. Click "הוסף משתמש חדש" (Add New User)
4. Fill in details and save

#### Option 2: Via Command Line
Generate password hash:
```python
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
```

Add to `users.yaml`:
```yaml
- username: newuser
  full_name: New User Name
  password_hash: "$2b$12$..."
  role: user  # or 'admin'
```

## Database Schema Overview

### Tables

1. **users** - User accounts
   - `id`: Primary key
   - `username`: Unique username
   - `full_name`: Display name
   - `role`: 'admin' or 'user'
   - `created_at`: Registration timestamp
   - `last_login`: Last login timestamp

2. **analyses** - Excel file analysis sessions
   - `id`: Primary key
   - `user_id`: Foreign key to users
   - `filename`: Original file name
   - `run_id`: Unique run identifier
   - `status`: pending, running, completed, error
   - `result_data`: JSON result data
   - `created_at`, `completed_at`: Timestamps

3. **conversations** - Refinement conversations
   - `id`: Primary key
   - `user_id`: Foreign key to users
   - `analysis_id`: Foreign key to analyses
   - `title`: Conversation title
   - `created_at`, `updated_at`: Timestamps

4. **messages** - Individual messages in conversations
   - `id`: Primary key
   - `conversation_id`: Foreign key to conversations
   - `role`: user, assistant, system
   - `content`: Message text
   - `metadata`: JSON metadata
   - `created_at`: Timestamp

5. **activity_logs** - Audit trail
   - `id`: Primary key
   - `user_id`: Foreign key to users
   - `analysis_id`: Foreign key to analyses (nullable)
   - `event_type`: Event type (login, logout, upload, refine, etc.)
   - `event_data`: JSON event data
   - `created_at`: Timestamp

## Authentication Flow

1. **Login**: User credentials verified against `users.yaml`
2. **Session**: Flask session stores user data
3. **Database Sync**: User record created/updated in PostgreSQL
4. **Activity Logging**: All actions logged to `activity_logs` table
5. **Tracking**: Analyses and refinements linked to user

## Security Best Practices

1. **Change Default Passwords**
   ```bash
   # Use admin panel or update users.yaml with new hashes
   ```

2. **Secure Database Connection**
   - Use strong database password
   - Restrict database access to localhost or specific IPs
   - Use SSL for remote connections

3. **Secure Flask Secret Key**
   - Generate strong random key
   - Never commit to version control
   - Keep in `.env` file

4. **File Permissions**
   ```bash
   chmod 600 .env
   chmod 600 users.yaml
   ```

5. **Production Deployment**
   - Enable HTTPS
   - Set `SESSION_COOKIE_SECURE = True`
   - Use environment variables for all secrets
   - Regular database backups

## Troubleshooting

### Connection Error
```
psycopg2.OperationalError: could not connect to server
```
**Solution**: Check PostgreSQL is running and credentials are correct in `.env`

### Permission Denied
```
permission denied for table users
```
**Solution**: Grant proper permissions:
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO excel_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO excel_user;
```

### Import Error
```
ModuleNotFoundError: No module named 'psycopg2'
```
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Maintenance

### Backup Database
```bash
pg_dump -U excel_user excel_insights > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql -U excel_user -d excel_insights < backup_20240101.sql
```

### View Activity Logs
```sql
SELECT u.username, al.event_type, al.created_at
FROM activity_logs al
JOIN users u ON al.user_id = u.id
ORDER BY al.created_at DESC
LIMIT 50;
```

### User Statistics
```sql
SELECT u.username, u.full_name,
       COUNT(a.id) as analyses_count,
       MAX(a.created_at) as last_analysis
FROM users u
LEFT JOIN analyses a ON u.id = a.user_id
GROUP BY u.id, u.username, u.full_name
ORDER BY analyses_count DESC;
```

## Support

For issues or questions:
- Check logs: Flask console output and PostgreSQL logs
- Verify environment variables are set correctly
- Ensure all dependencies are installed
- Check PostgreSQL service status: `sudo systemctl status postgresql`
