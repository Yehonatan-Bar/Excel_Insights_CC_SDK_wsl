#!/usr/bin/env python3
"""
Real-Time Analysis Monitor
Run this script to monitor the progress of your Excel analysis in real-time.

Usage:
    python monitor_analysis.py
    python monitor_analysis.py --run-id 20251019_171509
"""

import argparse
import requests
import time
import sys
from datetime import datetime


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def print_header(run_id, status_data):
    """Print monitoring header."""
    print("=" * 80)
    print(f"📊 EXCEL INSIGHTS MONITOR - Run ID: {run_id}")
    print(f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    print()

    status = status_data.get('status', 'unknown')
    filename = status_data.get('filename', 'unknown')
    file_size_mb = status_data.get('file_size_mb', 0)
    is_large = status_data.get('is_large_file', False)

    print(f"📁 File: {filename} ({file_size_mb:.1f} MB)")
    print(f"📏 Large File Mode: {'✅ YES' if is_large else '❌ NO'}")
    print(f"🔄 Status: {status.upper()}")
    print()


def print_events(events, max_events=30):
    """Print recent events."""
    print(f"📋 RECENT ACTIVITY (Last {min(len(events), max_events)} events):")
    print("-" * 80)

    # Show last N events
    recent_events = events[-max_events:]

    for event in recent_events:
        timestamp = event.get('timestamp', '??:??:??')
        icon = event.get('icon', '•')
        content = event.get('content', 'No content')
        event_type = event.get('type', 'text')

        # Color code by type
        if event_type == 'error':
            color = '\033[91m'  # Red
        elif event_type == 'thinking':
            color = '\033[94m'  # Blue
        elif event_type == 'tool':
            color = '\033[93m'  # Yellow
        elif event_type == 'result':
            color = '\033[92m'  # Green
        else:
            color = '\033[0m'  # Default

        reset = '\033[0m'

        # Truncate long content
        if len(content) > 100:
            content = content[:97] + "..."

        print(f"{color}[{timestamp}] {icon} {content}{reset}")

    print("-" * 80)
    print()


def print_statistics(status_data):
    """Print progress statistics."""
    event_count = status_data.get('event_count', 0)
    message = status_data.get('message', 'No message')

    print(f"📈 STATISTICS:")
    print(f"   Total Events: {event_count}")
    print(f"   Current Status: {message}")
    print()


def monitor_analysis(run_id, base_url="http://127.0.0.1:5000", refresh_interval=2):
    """
    Monitor analysis progress in real-time.

    Args:
        run_id: Analysis run ID to monitor
        base_url: Flask server base URL
        refresh_interval: Seconds between refreshes
    """
    status_url = f"{base_url}/status/{run_id}"

    print(f"🔍 Monitoring analysis: {run_id}")
    print(f"📡 Status URL: {status_url}")
    print(f"⏱️  Refresh: Every {refresh_interval} seconds")
    print(f"⌨️  Press Ctrl+C to exit")
    print()
    print("Starting in 2 seconds...")
    time.sleep(2)

    last_event_count = 0
    no_change_count = 0

    try:
        while True:
            try:
                # Fetch status
                response = requests.get(status_url, timeout=10)

                if response.status_code == 404:
                    print(f"\n❌ Error: Analysis {run_id} not found!")
                    print("   Check if the run_id is correct or if the Flask server is running.")
                    sys.exit(1)
                elif response.status_code != 200:
                    print(f"\n⚠️  HTTP Error: {response.status_code}")
                    time.sleep(refresh_interval)
                    continue

                status_data = response.json()
                status = status_data.get('status', 'unknown')
                events = status_data.get('events', [])
                event_count = status_data.get('event_count', 0)

                # Clear screen and redraw
                clear_screen()
                print_header(run_id, status_data)
                print_statistics(status_data)
                print_events(events, max_events=30)

                # Check for completion
                if status == 'completed':
                    print("✅ ANALYSIS COMPLETED!")
                    dashboard_url = status_data.get('dashboard_url')
                    if dashboard_url:
                        print(f"🎉 Dashboard available at: {base_url}{dashboard_url}")
                    print("\nMonitoring complete. Press Ctrl+C to exit or wait...")
                    time.sleep(10)
                    break
                elif status == 'error':
                    print("❌ ANALYSIS FAILED!")
                    error = status_data.get('error', 'Unknown error')
                    print(f"Error: {error}")
                    print("\nMonitoring stopped. Press Ctrl+C to exit or wait...")
                    time.sleep(10)
                    break

                # Detect if stuck (no new events)
                if event_count == last_event_count:
                    no_change_count += 1
                else:
                    no_change_count = 0

                if no_change_count > 30:  # No change for 60 seconds
                    print(f"\n⚠️  WARNING: No new events for {no_change_count * refresh_interval} seconds!")
                    print("   The analysis might be stuck. Check Task Manager for CPU usage.")

                last_event_count = event_count

                # Footer
                print(f"⏰ Next refresh in {refresh_interval}s... (Events: {event_count}, No change: {no_change_count})")

            except requests.ConnectionError:
                clear_screen()
                print("❌ CONNECTION ERROR: Cannot connect to Flask server!")
                print(f"   Make sure Flask is running at {base_url}")
                print(f"\n⏰ Retrying in {refresh_interval} seconds...")
            except requests.Timeout:
                clear_screen()
                print("⏱️  TIMEOUT: Server took too long to respond")
                print(f"\n⏰ Retrying in {refresh_interval} seconds...")
            except Exception as e:
                clear_screen()
                print(f"❌ ERROR: {str(e)}")
                print(f"\n⏰ Retrying in {refresh_interval} seconds...")

            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user. Goodbye!")
        sys.exit(0)


def list_active_jobs(base_url="http://127.0.0.1:5000"):
    """List all active jobs."""
    try:
        response = requests.get(f"{base_url}/api/active-jobs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('active_jobs', [])

            if not jobs:
                print("No active jobs found.")
                return None

            print(f"\n📋 Found {len(jobs)} active job(s):")
            print("-" * 80)
            for idx, job in enumerate(jobs, 1):
                run_id = job.get('run_id', 'unknown')
                filename = job.get('filename', 'unknown')
                status = job.get('status', 'unknown')
                print(f"{idx}. {run_id} - {filename} ({status})")
            print("-" * 80)

            return jobs
        else:
            print(f"Error fetching active jobs: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Excel Insights analysis in real-time")
    parser.add_argument(
        '--run-id',
        type=str,
        help="Run ID to monitor (if not provided, will list active jobs)"
    )
    parser.add_argument(
        '--url',
        type=str,
        default="http://127.0.0.1:5000",
        help="Flask server base URL (default: http://127.0.0.1:5000)"
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=2,
        help="Refresh interval in seconds (default: 2)"
    )

    args = parser.parse_args()

    if args.run_id:
        # Monitor specific run
        monitor_analysis(args.run_id, base_url=args.url, refresh_interval=args.interval)
    else:
        # List active jobs and prompt user
        print("🔍 Fetching active jobs...")
        jobs = list_active_jobs(base_url=args.url)

        if jobs:
            print("\nEnter the run_id to monitor (or Ctrl+C to exit):")
            run_id = input("> ").strip()
            if run_id:
                monitor_analysis(run_id, base_url=args.url, refresh_interval=args.interval)
        else:
            print("\nNo active jobs to monitor.")
            print("\nUsage: python monitor_analysis.py --run-id 20251019_171509")
