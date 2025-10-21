# 🔍 Debug Monitor Setup Guide

## Overview

The Debug Monitor provides comprehensive visibility into the Claude Agent SDK's internal operations, including:

- ✅ System and user prompts
- ✅ All SDK events (thinking, text, tool calls, results)
- ✅ Detailed event timeline
- ✅ Tool call tracking
- ✅ API call monitoring
- ✅ Error tracking
- ✅ Real-time statistics

---

## Quick Setup (3 Steps)

### Step 1: Add Import to app.py

Add this import near the top of `app.py` (after other imports):

```python
from debug_routes import register_debug_routes
```

### Step 2: Register Routes in app.py

Add this line BEFORE the `if __name__ == '__main__':` block (around line 1129):

```python
# Register debug monitoring routes
register_debug_routes(app, analysis_jobs, login_required)
```

### Step 3: Integrate Monitor into agent_service.py

Add this import at the top of `agent_service.py`:

```python
from agent_monitor import AgentMonitor
```

Then in the `analyze_file()` method, add monitoring:

```python
# After line 272 (run_dir.mkdir...)
# Initialize monitoring
monitor = AgentMonitor(run_id, output_dir=self.output_dir)
monitor.set_configuration({
    'model': options.model,
    'permission_mode': options.permission_mode,
    'max_turns': options.max_turns,
    'mcp_servers': list(options.mcp_servers.keys())
})
monitor.set_prompts(system_prompt, user_prompt)
```

And in the event loop (around line 636):

```python
async for event in client.receive_response():
    # Record event in monitor
    monitor.record_event(event)

    # ... rest of existing code ...
```

Finally, before returning (around line 677):

```python
# Finalize monitoring
monitor.finalize(status='completed' if dashboard_path.exists() else 'error')
```

---

## Manual Integration (if files are locked)

If you can't modify the files directly, follow these steps:

### Create Integration Script

Save this as `integrate_debug_monitor.py`:

```python
#!/usr/bin/env python3
"""
Integrate Debug Monitor into Flask App
Run this script to automatically add debug monitoring to your app.
"""

import fileinput
import sys

def integrate_app_py():
    """Add debug routes to app.py"""
    # Find the line to insert after
    with open('app.py', 'r') as f:
        lines = f.readlines()

    # Find import section
    import_idx = None
    for i, line in enumerate(lines):
        if 'from chat_service import get_chat_service' in line:
            import_idx = i + 1
            break

    if import_idx:
        lines.insert(import_idx, 'from debug_routes import register_debug_routes\n')

    # Find where to register routes (before if __name__)
    register_idx = None
    for i, line in enumerate(lines):
        if "if __name__ == '__main__':" in line:
            register_idx = i
            break

    if register_idx:
        lines.insert(register_idx, '\n# Register debug monitoring routes\n')
        lines.insert(register_idx + 1, 'register_debug_routes(app, analysis_jobs, login_required)\n\n')

    # Write back
    with open('app.py', 'w') as f:
        f.writelines(lines)

    print("✅ app.py updated")

def integrate_agent_service():
    """Add monitoring to agent_service.py"""
    print("⚠️  agent_service.py requires manual integration")
    print("   See the integration steps in this guide")

if __name__ == '__main__':
    print("🔧 Integrating Debug Monitor...")
    integrate_app_py()
    integrate_agent_service()
    print("✅ Integration complete!")
    print("\nNext steps:")
    print("1. Manually integrate monitoring into agent_service.py (see guide)")
    print("2. Restart Flask app")
    print("3. Upload a file and visit /debug/<run_id>")
```

Then run:

```bash
python integrate_debug_monitor.py
```

---

## Usage

### Access the Debug Monitor

Once integrated, restart your Flask app:

```bash
python app.py
```

Then:

1. Upload an Excel file for analysis
2. Get the `run_id` from the upload (e.g., `20251019_171509`)
3. Navigate to: `http://localhost:5000/debug/20251019_171509`

### Monitor Interface Tabs

- **📊 Overview**: Configuration and general info
- **📝 Prompts**: Full system and user prompts
- **⏱️ Timeline**: Chronological event log
- **🧠 Thinking**: All thinking blocks
- **🔧 Tool Calls**: All tool invocations
- **📋 All Events**: Raw event data
- **❌ Errors**: Error tracking

### Auto-Refresh

The interface auto-refreshes every 5 seconds while the analysis is running.

### API Access

Get monitoring data as JSON:

```bash
curl http://localhost:5000/api/debug/20251019_171509
```

---

## Architecture

**★ Insight ─────────────────────────────────────**
The monitoring system uses a three-layer architecture:
1. **AgentMonitor** (agent_monitor.py) - Captures and stores detailed SDK events
2. **Flask Routes** (debug_routes.py) - Serves monitoring data via HTTP
3. **UI Template** (debug_monitor.html) - Visualizes events with tabs and real-time updates

This separation ensures monitoring doesn't interfere with analysis performance.
**─────────────────────────────────────────────────**

### Data Flow

```
Claude SDK → agent_service.py → AgentMonitor → JSON file → Flask routes → HTML UI
```

### File Storage

Monitoring data is saved to:
```
outputs/<run_id>/agent_monitor.json
```

This file contains:
- Configuration
- Prompts
- All events with timestamps
- Categorized thinking blocks
- Tool calls
- API calls
- Statistics

---

## Troubleshooting

### "Debug data not found"

**Cause**: Monitoring not integrated into agent_service.py
**Fix**: Complete Step 3 above

### Events not appearing

**Cause**: Monitor not recording events
**Fix**: Verify `monitor.record_event(event)` is called in the event loop

### Old data showing

**Cause**: Cached JSON file
**Fix**: Click the "🔄 Refresh" button or reload the page

### Routes not working

**Cause**: Routes not registered
**Fix**: Verify `register_debug_routes()` is called in app.py

---

## Benefits

1. **Deep Visibility**: See exactly what the agent is thinking and doing
2. **Debugging**: Quickly identify where the agent gets stuck
3. **Performance Analysis**: Track tool calls and timing
4. **Error Tracking**: Catch and diagnose errors early
5. **Learning**: Understand how the Claude Agent SDK works

---

## Next Steps

1. ✅ Complete the integration steps above
2. ✅ Restart Flask app
3. ✅ Upload a test file
4. ✅ Open the debug monitor
5. ✅ Watch the agent work in real-time!

---

## Example Output

After uploading a file, you'll see:

```
📊 Agent Debug Monitor
Run ID: 20251019_171509 | Status: running | Started: 2025-10-19T17:15:09

Statistics:
- Total Events: 47
- Thinking Blocks: 12
- Tool Calls: 8
- API Calls: 3
- Errors: 0

Timeline shows:
#1 [17:15:09] MessageEvent
   → Thinking: "I need to analyze this Excel file..."

#2 [17:15:11] MessageEvent
   → Tool: analyze_excel
   → Input: {"file_path": "uploads/merged.xlsx"}

#3 [17:15:15] MessageEvent
   → Result: {"sheets": 3, "columns": 85...}
```

**Your complete monitoring solution is ready! 🎉**
