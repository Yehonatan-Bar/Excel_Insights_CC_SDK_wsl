#!/usr/bin/env python3
"""
Integrate Debug Monitor into Flask App
Run this script to automatically add debug monitoring to your app.

Usage:
    python integrate_debug_monitor.py
"""

import os
import shutil
from datetime import datetime


def backup_file(filepath):
    """Create a backup of the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def integrate_app_py():
    """Add debug routes to app.py"""
    print("\n🔧 Integrating debug routes into app.py...")

    # Backup first
    backup_file('app.py')

    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already integrated
    if 'from debug_routes import register_debug_routes' in content:
        print("⚠️  app.py already has debug_routes import - skipping")
        return True

    # Add import after chat_service import
    import_marker = 'from chat_service import get_chat_service'
    if import_marker in content:
        content = content.replace(
            import_marker,
            import_marker + '\nfrom debug_routes import register_debug_routes'
        )
        print("✅ Added import statement")
    else:
        print("❌ Could not find import marker in app.py")
        return False

    # Add route registration before if __name__
    main_marker = "if __name__ == '__main__':"
    if main_marker in content:
        content = content.replace(
            main_marker,
            '\n# Register debug monitoring routes\nregister_debug_routes(app, analysis_jobs, login_required)\n\n' + main_marker
        )
        print("✅ Added route registration")
    else:
        print("❌ Could not find main block in app.py")
        return False

    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ app.py integration complete")
    return True


def integrate_agent_service():
    """Add monitoring to agent_service.py"""
    print("\n🔧 Integrating monitoring into agent_service.py...")

    # Backup first
    backup_file('agent_service.py')

    with open('agent_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if already integrated
    content_str = ''.join(lines)
    if 'from agent_monitor import AgentMonitor' in content_str:
        print("⚠️  agent_service.py already has AgentMonitor import - skipping")
        return True

    # Add import at top (after other imports)
    import_idx = None
    for i, line in enumerate(lines):
        if 'from excel_mcp_tools import' in line:
            # Find the end of this import block
            j = i
            while j < len(lines) and (lines[j].strip().endswith(',') or lines[j].strip().endswith(')')):
                j += 1
            import_idx = j + 1
            break

    if import_idx is None:
        print("❌ Could not find import location in agent_service.py")
        return False

    lines.insert(import_idx, 'from agent_monitor import AgentMonitor\n')
    print("✅ Added AgentMonitor import")

    # Find where to initialize monitor (after run_dir.mkdir)
    init_idx = None
    for i, line in enumerate(lines):
        if 'run_dir.mkdir(parents=True, exist_ok=True)' in line:
            init_idx = i + 1
            break

    if init_idx:
        monitor_init_code = '''
        # Initialize monitoring for debugging
        monitor = AgentMonitor(run_id, output_dir=self.output_dir)
        monitor.set_configuration({
            'model': options.model,
            'permission_mode': options.permission_mode,
            'max_turns': options.max_turns,
            'mcp_servers': list(options.mcp_servers.keys()) if hasattr(options, 'mcp_servers') else []
        })
        monitor.set_prompts(system_prompt, user_prompt)

'''
        lines.insert(init_idx, monitor_init_code)
        print("✅ Added monitor initialization")
    else:
        print("⚠️  Could not find monitor initialization location")

    # Find event loop to add monitoring
    event_idx = None
    for i, line in enumerate(lines):
        if 'async for event in client.receive_response():' in line:
            event_idx = i + 1
            # Find the first print statement in the loop
            for j in range(i + 1, min(i + 10, len(lines))):
                if 'print(f"DEBUG: Received event' in lines[j]:
                    event_idx = j
                    break
            break

    if event_idx:
        lines.insert(event_idx, '                    # Record event in monitor\n')
        lines.insert(event_idx + 1, '                    monitor.record_event(event)\n\n')
        print("✅ Added event monitoring")
    else:
        print("⚠️  Could not find event loop location")

    # Find return statement to add finalization
    return_idx = None
    for i in range(len(lines) - 1, 0, -1):
        if 'return {' in lines[i] and '"dashboard_path"' in lines[i + 1]:
            return_idx = i
            break

    if return_idx:
        lines.insert(return_idx, '\n        # Finalize monitoring\n')
        lines.insert(return_idx + 1, '        monitor.finalize(status=\'completed\' if dashboard_path.exists() else \'partial\')\n\n')
        print("✅ Added monitor finalization")
    else:
        print("⚠️  Could not find return statement location")

    # Write back
    with open('agent_service.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("✅ agent_service.py integration complete")
    return True


def create_test_monitor():
    """Create a test monitoring file to verify the system works."""
    print("\n🧪 Creating test monitoring data...")

    from agent_monitor import AgentMonitor

    # Create test monitor
    test_monitor = AgentMonitor('test_monitor', output_dir='outputs')
    test_monitor.set_configuration({
        'model': 'sonnet',
        'permission_mode': 'bypassPermissions',
        'max_turns': 100
    })
    test_monitor.set_prompts(
        'You are a helpful assistant.',
        'Please analyze this test data.'
    )

    # Add some test events
    class MockEvent:
        def __init__(self, content_text):
            self.content = [MockContent(content_text)]

    class MockContent:
        def __init__(self, text):
            self.text = text

    test_monitor.record_event(MockEvent("Test thinking process"), event_type="ThinkingEvent")
    test_monitor.record_event(MockEvent("Test response"), event_type="ResponseEvent")

    test_monitor.finalize('completed')

    print("✅ Test monitoring data created at outputs/test_monitor/agent_monitor.json")
    print("   Visit http://localhost:5000/debug/test_monitor to view it")


def main():
    """Main integration process."""
    print("=" * 70)
    print("🔍 Debug Monitor Integration Script")
    print("=" * 70)

    # Check required files exist
    required_files = [
        'app.py',
        'agent_service.py',
        'debug_routes.py',
        'agent_monitor.py',
        'templates/debug_monitor.html'
    ]

    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        print("   Please ensure all files are in the current directory.")
        return

    print("\n✅ All required files found")

    # Integrate app.py
    if not integrate_app_py():
        print("\n❌ app.py integration failed")
        return

    # Integrate agent_service.py
    if not integrate_agent_service():
        print("\n❌ agent_service.py integration failed - you may need to do this manually")
        print("   See DEBUG_MONITOR_SETUP.md for manual integration steps")

    # Create test data
    try:
        create_test_monitor()
    except Exception as e:
        print(f"\n⚠️  Could not create test data: {e}")

    print("\n" + "=" * 70)
    print("✅ Integration Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart your Flask app:")
    print("   python app.py")
    print("\n2. Upload a file for analysis")
    print("\n3. Access the debug monitor:")
    print("   http://localhost:5000/debug/<run_id>")
    print("\n4. Or test with sample data:")
    print("   http://localhost:5000/debug/test_monitor")
    print("\nFor more info, see DEBUG_MONITOR_SETUP.md")
    print("=" * 70)


if __name__ == '__main__':
    main()
