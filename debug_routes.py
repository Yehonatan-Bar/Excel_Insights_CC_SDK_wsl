"""
Debug Monitoring Routes for Flask App

Provides detailed SDK event monitoring and debugging interfaces.
"""

from flask import render_template, jsonify
from pathlib import Path
import json


def register_debug_routes(app, analysis_jobs, login_required):
    """Register debug monitoring routes with the Flask app."""

    @app.route('/debug/<run_id>')
    @login_required
    def debug_monitor(run_id):
        """Debug monitoring interface - shows detailed SDK events and agent behavior."""
        # Load monitoring data
        monitor_file = Path(app.config['OUTPUT_FOLDER']) / run_id / "agent_monitor.json"

        if not monitor_file.exists():
            # No monitoring data yet - check if job exists
            if run_id in analysis_jobs:
                # Job exists but no monitor data yet
                return render_template('debug_monitor.html',
                                     run_id=run_id,
                                     data={
                                         'run_id': run_id,
                                         'status': analysis_jobs[run_id].get('status', 'unknown'),
                                         'start_time': 'Unknown',
                                         'end_time': None,
                                         'configuration': {},
                                         'prompts': {},
                                         'events': [],
                                         'thinking_blocks': [],
                                         'tool_calls': [],
                                         'api_calls': [],
                                         'responses': [],
                                         'errors': [],
                                         'statistics': {
                                             'total_events': 0,
                                             'thinking_count': 0,
                                             'tool_call_count': 0,
                                             'api_call_count': 0,
                                             'error_count': 0
                                         }
                                     })
            else:
                return "Debug data not found for this run_id", 404

        # Load monitoring data
        try:
            with open(monitor_file, 'r', encoding='utf-8') as f:
                monitoring_data = json.load(f)

            return render_template('debug_monitor.html',
                                 run_id=run_id,
                                 data=monitoring_data)
        except Exception as e:
            return f"Error loading debug data: {str(e)}", 500

    @app.route('/api/debug/<run_id>')
    @login_required
    def api_debug_monitor(run_id):
        """API endpoint to get debug monitoring data as JSON."""
        monitor_file = Path(app.config['OUTPUT_FOLDER']) / run_id / "agent_monitor.json"

        if not monitor_file.exists():
            return jsonify({"error": "Debug data not found"}), 404

        try:
            with open(monitor_file, 'r', encoding='utf-8') as f:
                monitoring_data = json.load(f)
            return jsonify(monitoring_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    print("✅ Debug monitoring routes registered")
