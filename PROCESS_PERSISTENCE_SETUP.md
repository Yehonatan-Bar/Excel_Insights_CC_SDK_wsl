# Process Persistence - Setup & Testing Guide

## Overview

Process persistence allows users to close their browser or experience a server restart while an analysis is running, and seamlessly resume when they return. The analysis progress, events, and state are preserved in the database.

## Features Implemented

### 1. **Database Persistence**
- New `job_state` JSONB column in `analyses` table stores complete job information
- Job state includes: status, message, events, progress, email preferences, etc.
- Database methods to save, retrieve, and restore active jobs

### 2. **Server-Side Restoration**
- On server startup, all active jobs are restored from database to memory
- Jobs continue where they left off (if still processing)
- Completed/errored states are preserved accurately

### 3. **Client-Side Session Recovery**
- When user returns to the page, frontend checks for active jobs via API
- Active processes are automatically displayed with progress
- Seamless resumption of polling and event updates

### 4. **Job State Synchronization**
- Job state is persisted to database:
  - When job is created
  - When status changes (starting → running → completed/error)
  - Every 5 events during processing (for efficiency)
  - On completion or error

## Installation Steps

### Step 1: Apply Database Migration

Run the migration script to add the `job_state` column:

```bash
python apply_migration.py
```

Or manually apply the migration:

```bash
psql -U postgres -d excel_insights -f migrations/001_add_job_state.sql
```

Expected output:
```
✅ Migration applied successfully!
New column 'job_state' added to analyses table.
Process persistence is now enabled!
```

### Step 2: Restart the Application

```bash
python app.py
```

You should see:
```
🔄 Checking for active jobs to restore...
📦 Restored N active job(s) from database
```

## Testing Guide

### Test 1: Browser Closure During Analysis

1. **Start an analysis:**
   - Upload an Excel file
   - Wait for analysis to start (you should see events appearing)

2. **Close the browser completely** (not just the tab)

3. **Reopen the browser and navigate back to the application:**
   - Log in if needed
   - You should see: "🔄 המשך ניתוח פעיל: filename.xlsx"
   - The analysis should continue from where it left off
   - All previous events should still be visible

**Expected behavior:**
- Loading indicator appears automatically
- Progress message shows current status
- Events continue to stream
- Analysis completes normally

---

### Test 2: Server Restart During Analysis

1. **Start an analysis:**
   - Upload an Excel file
   - Wait for analysis to start

2. **Stop the Flask server** (Ctrl+C)

3. **Restart the server:**
   ```bash
   python app.py
   ```

4. **Refresh the page in browser:**
   - The active job should be restored
   - Status should show the job is still running

**Expected behavior:**
- Server logs show: "✅ Restored active job: run_id (status: running)"
- Frontend picks up the active job automatically
- Analysis continues (if still processing) or shows final state

---

### Test 3: Multiple Sessions

1. **Start an analysis**

2. **Open a second browser/tab** (while logged in as the same user)

3. **Navigate to the home page**

**Expected behavior:**
- Second session should detect the active job
- Shows: "🔄 המשך ניתוח פעיל"
- Both sessions show the same progress
- Completing in one session updates both

---

### Test 4: Guest Users

1. **Log in as guest** (guest users don't have database persistence)

2. **Upload a file**

3. **Close browser and return**

**Expected behavior:**
- No active jobs are restored (guests don't persist to DB)
- Guest sees empty upload form
- This is intentional - guests are session-only

---

### Test 5: Completed Analysis

1. **Let an analysis complete fully**

2. **Close browser**

3. **Return to the page**

**Expected behavior:**
- No active job notification (completed jobs don't restore)
- User sees normal upload form
- Can view the dashboard from history

---

## Architecture Details

### Database Schema

```sql
-- analyses table now has:
job_state JSONB  -- Complete job state for persistence
```

### Job State Structure

```json
{
  "status": "running",
  "message": "Claude Agent is analyzing...",
  "filename": "data.xlsx",
  "user_id": 123,
  "events": [...],
  "event_count": 42,
  "send_email": true,
  "user_email": "user@example.com",
  "user_full_name": "User Name"
}
```

### API Endpoints

- `GET /api/active-jobs` - Returns all active jobs for current user
- `GET /status/{run_id}` - Check status of specific job (existing)

### Key Functions

**Backend (app.py):**
- `persist_job_state(run_id)` - Save job state to database
- `restore_jobs_from_database()` - Load active jobs on startup
- `get_active_jobs()` - API endpoint for active jobs

**Frontend (index.html):**
- `checkForActiveJobs()` - Check for active jobs on page load
- `pollStatus(run_id, startTime)` - Poll for job status (existing)

## Troubleshooting

### Issue: Migration fails

**Solution:** Check database connection settings in `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=excel_insights
DB_USER=postgres
DB_PASSWORD=your_password
```

### Issue: Jobs not restoring

**Check:**
1. Database migration applied: `\d analyses` should show `job_state` column
2. Server logs show: "🔄 Checking for active jobs to restore..."
3. Active jobs exist in database: `SELECT * FROM analyses WHERE status IN ('starting', 'running');`

### Issue: Frontend not detecting active jobs

**Check:**
1. Browser console for errors
2. Network tab shows successful call to `/api/active-jobs`
3. Response contains active jobs array

### Issue: Guest users not working

**Expected:** Guests don't have persistence (by design)
- Guests use `session['user_id'] = None`
- No database tracking for guests
- Jobs are memory-only during their session

## Benefits

✅ **User Experience:**
- Users can close browser without losing progress
- Long-running analyses won't be lost
- Seamless continuation of work

✅ **Server Resilience:**
- Server restarts don't lose job state
- Deployments can happen with running jobs
- State is preserved in database

✅ **Multi-Device:**
- User can check progress from different devices
- All logged-in sessions see same progress
- Real-time synchronization via polling

## Security Considerations

- Guest users: No persistence (by design)
- User isolation: Users only see their own active jobs
- Authentication: All endpoints require login
- Data privacy: Job state is user-specific

## Performance

- **Database writes:** Every 5 events (efficient batching)
- **Poll interval:** 2 seconds (unchanged)
- **Restoration:** O(n) where n = active jobs (typically < 10)
- **JSONB storage:** Efficient for complex nested data

---

**Implementation completed! 🎉**

Users can now safely close their browser during analysis, and the process will continue seamlessly when they return.
