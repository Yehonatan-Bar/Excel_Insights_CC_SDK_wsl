# Testing Instructions for Email Notification Feature

## Overview
This document contains instructions for testing the email notification and user management features recently added to the Excel Insights Dashboard application.

---

## What Was Changed

### 1. Email Notification System
- Users can now opt-in to receive email notifications when their Excel analysis completes
- Emails are sent via SendGrid from `Excel-insights@metro-mail.co.il`
- Users receive:
  - Success email with dashboard link when analysis completes
  - Error email with error details if analysis fails
- Guest users do NOT see the email checkbox (no email to send to)

### 2. Configuration Migration
- User configuration migrated from YAML (`users.yaml`) to XML (`users.xml`)
- All user management now uses XML format with ElementTree parsing
- Email field added to user profiles

### 3. Database Schema Updates
- Added `email` VARCHAR(255) field to users table
- Added `email_notifications` BOOLEAN field (defaults to TRUE)

### 4. Admin Panel Enhancements
- Users table now displays email column
- Add/Edit User modals include email input field
- Email is optional throughout the system

### 5. Files Modified
- `init_db.sql` - Database schema with email fields
- `users.xml` - New XML configuration format (replaces users.yaml)
- `auth.py` - Complete rewrite for XML parsing
- `email_service.py` - New SendGrid email service
- `requirements.txt` - Added sendgrid, removed PyYAML
- `.env` - Added SendGrid API key placeholder
- `app.py` - Email notification integration
- `database.py` - Email field handling
- `templates/index.html` - Email notification checkbox
- `templates/admin.html` - Email column and input fields

---

## Prerequisites

### 1. Playwright MCP Server
The Playwright MCP server has been installed globally and configured. After Claude Code restarts, you'll have access to browser automation for testing the UI.

**Verify Playwright MCP is available:**
```bash
# Check if server is configured
cat ~/.claude.json | grep -A 5 '"playwright"'

# Should show:
# "playwright": {
#   "command": "node",
#   "args": ["/home/adminuser/.nvm/versions/node/v22.19.0/bin/playwright-mcp-server"],
#   "disabled": false
# }
```

### 2. Environment Setup
The application requires these environment variables in `.env`:

```bash
# SendGrid Configuration (required for email notifications)
SENDGRID_API_KEY=your-sendgrid-api-key-here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=excel_insights
DB_USER=excel_user
DB_PASSWORD=your-database-password-here

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
```

---

## Testing Tasks

### Task 1: Verify Database Schema
**Goal:** Confirm the database has the new email fields

**Steps:**
1. Connect to PostgreSQL database
2. Check the users table schema:
   ```sql
   \d users
   ```
3. Verify these fields exist:
   - `email` VARCHAR(255)
   - `email_notifications` BOOLEAN DEFAULT TRUE

**Expected Result:**
- Both fields present in schema
- No errors when querying users table

---

### Task 2: Verify XML Configuration
**Goal:** Confirm users.xml is properly formatted and loadable

**Steps:**
1. Read the `users.xml` file
2. Verify XML structure:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <users>
       <user>
           <username>admin</username>
           <full_name>Administrator</full_name>
           <email>admin@example.com</email>
           <password_hash>$2b$12$...</password_hash>
           <role>admin</role>
           <email_notifications>true</email_notifications>
       </user>
   </users>
   ```
3. Check that `auth.py` successfully loads the XML:
   ```bash
   python3 -c "from auth import AuthManager; auth = AuthManager(); print(auth.get_all_users())"
   ```

**Expected Result:**
- Valid XML structure
- Users load successfully with email fields

---

### Task 3: Test Admin Panel - Add User with Email
**Goal:** Verify admin can add users with email addresses

**Steps:**
1. Start the Flask application:
   ```bash
   source venv/bin/activate
   python app.py
   ```
2. Use Playwright MCP to:
   - Navigate to `http://localhost:5000`
   - Login as admin (username: admin, password from users.xml)
   - Navigate to admin panel (`/admin`)
   - Click "הוסף משתמש חדש" (Add New User)
   - Fill in the form:
     - Username: `test_user`
     - Full Name: `Test User`
     - Email: `test@example.com`
     - Password: `testpass123`
     - Role: `user`
   - Submit the form
3. Verify the user appears in the users table with email displayed
4. Check `users.xml` file to confirm user was added with email field

**Expected Result:**
- User added successfully
- Email displays in admin table
- `users.xml` contains new user with email element

---

### Task 4: Test Admin Panel - Edit User Email
**Goal:** Verify admin can update existing user emails

**Steps:**
1. In admin panel, find the test user created in Task 3
2. Click "ערוך" (Edit) button
3. Update email to `updated@example.com`
4. Save changes
5. Verify email updated in table
6. Check `users.xml` to confirm change persisted

**Expected Result:**
- Email updates successfully
- Changes visible in UI and XML file

---

### Task 5: Test Email Notification Checkbox (Logged-in User)
**Goal:** Verify email checkbox appears for logged-in users with email addresses

**Steps:**
1. Login as the test user (`test_user` / `testpass123`)
2. Navigate to upload page
3. Select an Excel file (.xlsx)
4. Verify email notification section appears with:
   - Checkbox (checked by default)
   - Text: "📧 שלח לי מייל כשהניתוח יושלם (test@example.com)"
   - Info text about email notification
5. Take a screenshot of the upload form

**Expected Result:**
- Checkbox section visible after file selection
- User's email displayed in checkbox label
- Section has RTL Hebrew layout

---

### Task 6: Test Email Notification Checkbox (Guest User)
**Goal:** Verify email checkbox does NOT appear for guest users

**Steps:**
1. Logout (if logged in)
2. Navigate to home page
3. Click "כניסה ללא רישום" (Continue as Guest)
4. Select an Excel file (.xlsx)
5. Verify email notification section does NOT appear
6. Take a screenshot

**Expected Result:**
- No email checkbox visible for guests
- Upload form works normally otherwise

---

### Task 7: Test Email Service Configuration
**Goal:** Verify SendGrid email service is properly configured

**Steps:**
1. Check that `email_service.py` exists and imports correctly:
   ```bash
   python3 -c "from email_service import email_service; print(f'Email service enabled: {email_service.enabled}')"
   ```
2. Verify `.env` has `SENDGRID_API_KEY` placeholder
3. Check that app.py imports email_service:
   ```bash
   grep "from email_service import" app.py
   ```

**Expected Result:**
- Email service module loads successfully
- Service reports enabled=False (no API key set yet)
- No import errors

---

### Task 8: Test File Upload with Email Notification (Mock)
**Goal:** Verify the email notification flag is captured and tracked

**Steps:**
1. Login as test user with email
2. Add debug logging to `app.py` in the upload route to print:
   ```python
   print(f"DEBUG: send_email={send_email}, user_email={user_email}")
   ```
3. Upload a small test Excel file with checkbox checked
4. Monitor console output for debug message
5. Check that `analysis_jobs[run_id]` includes:
   - `send_email: True`
   - `user_email: test@example.com`
   - `user_full_name: Test User`

**Expected Result:**
- Email preference captured from form
- Analysis job tracks email details
- No crashes or errors

---

### Task 9: Verify Email Templates (Code Review)
**Goal:** Confirm email templates are properly formatted in RTL Hebrew

**Steps:**
1. Read `email_service.py`
2. Review the HTML email templates in:
   - `send_analysis_complete()` method
   - `send_analysis_error()` method
3. Verify:
   - HTML has `lang="he" dir="rtl"`
   - Subject lines in Hebrew
   - Gradient styling matches app theme
   - Links to dashboard include run_id
   - From address: `Excel-insights@metro-mail.co.il`

**Expected Result:**
- Templates well-formatted with RTL support
- Professional appearance matching app design
- All required variables present in templates

---

### Task 10: Integration Test - Full Upload Flow
**Goal:** Test complete flow from upload to email trigger point

**Steps:**
1. Start the Flask app with debug logging
2. Login as test user
3. Upload a valid Excel file with email checkbox checked
4. Monitor the console for:
   - File upload success
   - Analysis job created
   - Run analysis async started
   - **Look for the point where `email_service.send_analysis_complete()` would be called**
5. Check if the code path reaches the email sending block:
   ```python
   if analysis_jobs[run_id].get('send_email') and analysis_jobs[run_id].get('user_email'):
       email_service.send_analysis_complete(...)
   ```

**Expected Result:**
- Flow completes without errors
- Email sending code is reached (even if API key not configured)
- Graceful handling if SendGrid not configured

---

## Playwright MCP Testing Scenarios

### Use Playwright to Automate UI Testing

**Scenario 1: Screenshot Comparison**
```
Use the Playwright MCP to:
1. Navigate to http://localhost:5000
2. Take a screenshot of the login page
3. Login as admin
4. Navigate to /admin
5. Take a screenshot of the admin panel showing the email column
6. Save screenshots to a test_results/ folder
```

**Scenario 2: Form Interaction Test**
```
Use the Playwright MCP to:
1. Login as test user
2. Click the file upload button
3. Verify the email checkbox appears
4. Check the checkbox state
5. Take a screenshot of the upload form with checkbox visible
```

**Scenario 3: Guest Mode Verification**
```
Use the Playwright MCP to:
1. Navigate to home page
2. Click "כניסה ללא רישום" (Continue as Guest)
3. Attempt to find the email checkbox element
4. Verify it does NOT exist in the DOM
5. Report the result
```

---

## Success Criteria

### All Tests Pass If:
- ✅ Database schema includes email fields
- ✅ users.xml loads successfully with email data
- ✅ Admin panel displays email column
- ✅ Admin can add users with email addresses
- ✅ Admin can edit user email addresses
- ✅ Email checkbox appears for logged-in users with emails
- ✅ Email checkbox does NOT appear for guest users
- ✅ Email service module loads without errors
- ✅ Upload flow captures email notification preference
- ✅ Email templates are properly formatted in RTL Hebrew
- ✅ No crashes or errors in any workflow

---

## Troubleshooting

### Common Issues:

**1. Database connection errors:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify .env database credentials are correct
- Run `psql -U excel_user -d excel_insights` to test connection

**2. XML parsing errors:**
- Validate users.xml structure
- Check for special characters that need escaping
- Verify UTF-8 encoding

**3. Email service import errors:**
- Verify sendgrid is installed: `pip list | grep sendgrid`
- Check requirements.txt includes `sendgrid==6.11.0`
- Reinstall if needed: `pip install sendgrid`

**4. Playwright MCP not available:**
- Verify MCP server configuration: `cat ~/.claude.json | grep playwright`
- Restart Claude Code to load MCP servers
- Check Node.js is available: `which node`

**5. Email checkbox not appearing:**
- Check browser console for JavaScript errors
- Verify user object in session has email field
- Check Jinja2 conditional: `{% if user and not user.is_guest and user.email %}`

---

## Notes for Testing Agent

### Recommended Testing Order:
1. Start with verification tasks (1-3) to confirm foundation
2. Test admin functionality (4-5) to ensure user management works
3. Test UI behavior (6-7) for both logged-in and guest users
4. Review code and email templates (8-9)
5. Run integration test (10)
6. Use Playwright MCP for automated UI testing

### Important Considerations:
- **DO NOT** try to actually send emails without a valid SendGrid API key
- **DO** verify the code path reaches the email sending logic
- **DO** test graceful fallback when API key is not configured
- **DO** use Playwright MCP for UI automation where appropriate
- **DO** take screenshots to document UI changes

### SendGrid API Key:
If you want to test actual email sending:
1. Get a SendGrid API key from https://sendgrid.com/
2. Add it to `.env`: `SENDGRID_API_KEY=SG.xxx...`
3. Verify sender email address in SendGrid dashboard
4. Run a full test with a real email address

---

## Expected Output

After completing all tests, provide:
1. **Test Results Summary:** Pass/Fail for each task
2. **Screenshots:** From Playwright automation
3. **Issues Found:** Any bugs or problems discovered
4. **Recommendations:** Suggestions for improvements
5. **Code Quality:** Assessment of implementation

---

## Contact

If you encounter issues or need clarification:
- Check the git commit messages for context on recent changes
- Review the code comments in modified files
- The last session completed both Part 1 and Part 2 of the email feature

---

**Good luck with testing! 🧪**
