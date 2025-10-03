"""
Flask App for Excel Insights Dashboard
"""
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Validate API key is set
if not os.environ.get('ANTHROPIC_API_KEY'):
    print("\n" + "="*70)
    print("❌ ERROR: ANTHROPIC_API_KEY not found!")
    print("="*70)
    print("\nThe Claude Agent SDK requires an API key to function.")
    print("\nPlease set your API key using ONE of these methods:\n")
    print("1. Create a .env file with:")
    print("   ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE\n")
    print("2. Export it in your terminal:")
    print("   export ANTHROPIC_API_KEY='sk-ant-api03-YOUR_KEY_HERE'\n")
    print("3. Set it permanently (Linux/Mac):")
    print("   echo 'export ANTHROPIC_API_KEY=\"sk-ant-api03-YOUR_KEY_HERE\"' >> ~/.bashrc")
    print("   source ~/.bashrc\n")
    print("Get your API key at: https://console.anthropic.com/")
    print("="*70 + "\n")
    sys.exit(1)
else:
    key_preview = os.environ.get('ANTHROPIC_API_KEY')[:20] + "..."
    print(f"✅ API Key loaded: {key_preview}")

from agent_service import analyze_excel_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size (increased)
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

# Track analysis jobs
analysis_jobs = {}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Home page with upload form."""
    return render_template('index.html')


def run_analysis_async(run_id, filepath, output_dir, refinement_prompt=None, original_run_id=None):
    """Run analysis in background thread."""
    try:
        if refinement_prompt:
            analysis_jobs[run_id]['status'] = 'running'
            analysis_jobs[run_id]['message'] = 'Claude Agent is refining your analysis...'
        else:
            analysis_jobs[run_id]['status'] = 'running'
            analysis_jobs[run_id]['message'] = 'Claude Agent is deeply analyzing your data...'

        # Define event callback to receive real-time events
        def event_callback(log_entry):
            """Receive events from agent in real-time."""
            print(f"Flask received event: {log_entry}")
            analysis_jobs[run_id]['events'].append(log_entry)
            analysis_jobs[run_id]['event_count'] += 1
            print(f"Total events now: {analysis_jobs[run_id]['event_count']}")

        # Send initial event
        if refinement_prompt:
            event_callback({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'type': 'text',
                'content': f'Refinement started: "{refinement_prompt[:100]}..."',
                'icon': '🔄'
            })
        else:
            event_callback({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'type': 'text',
                'content': 'Analysis started - initializing Claude Agent SDK...',
                'icon': '🚀'
            })

        result = analyze_excel_file(
            file_path=filepath,
            output_dir=output_dir,
            event_callback=event_callback,
            refinement_prompt=refinement_prompt,
            original_run_id=original_run_id
        )

        analysis_jobs[run_id]['status'] = 'completed'
        analysis_jobs[run_id]['result'] = result
        analysis_jobs[run_id]['message'] = 'Analysis complete!' if not refinement_prompt else 'Refinement complete!'

    except Exception as e:
        analysis_jobs[run_id]['status'] = 'error'
        analysis_jobs[run_id]['error'] = str(e)
        analysis_jobs[run_id]['message'] = f'Error: {str(e)}'


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and trigger BACKGROUND analysis (no timeout)."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Generate run_id
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize job tracking
        analysis_jobs[run_id] = {
            'status': 'starting',
            'message': 'Starting analysis...',
            'filename': filename,
            'events': [],  # Store activity log
            'event_count': 0  # Track for efficient polling
        }

        # Start analysis in background thread (NO TIMEOUT!)
        thread = threading.Thread(
            target=run_analysis_async,
            args=(run_id, filepath, app.config['OUTPUT_FOLDER'])
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "run_id": run_id,
            "status_url": f"/status/{run_id}"
        })

    return jsonify({"error": "Invalid file type. Only .xlsx and .xls allowed"}), 400


@app.route('/dashboard/<run_id>')
def view_dashboard(run_id):
    """Display the generated dashboard with refinement panel."""
    dashboard_path = Path(app.config['OUTPUT_FOLDER']) / run_id / "dashboard.html"

    if dashboard_path.exists():
        # Return wrapper template with refinement form
        return render_template('dashboard_wrapper.html', run_id=run_id)
    else:
        return "Dashboard not found", 404


@app.route('/dashboard-content/<run_id>')
def view_dashboard_content(run_id):
    """Serve the raw dashboard HTML (for iframe)."""
    dashboard_path = Path(app.config['OUTPUT_FOLDER']) / run_id / "dashboard.html"

    if dashboard_path.exists():
        return send_file(dashboard_path)
    else:
        return "Dashboard not found", 404


@app.route('/dashboard-content/<run_id>/<filename>')
def serve_visualization_file(run_id, filename):
    """Serve individual visualization files from session directory (safety net for multi-file dashboards)."""
    # Security: Only allow .html, .json files
    if not (filename.endswith('.html') or filename.endswith('.json')):
        return "Invalid file type", 400

    file_path = Path(app.config['OUTPUT_FOLDER']) / run_id / filename

    if file_path.exists() and file_path.is_file():
        return send_file(file_path)
    else:
        return f"File not found: {filename}", 404


@app.route('/refine/<run_id>', methods=['POST'])
def refine_analysis(run_id):
    """Refine existing analysis based on user feedback."""
    if run_id not in analysis_jobs:
        return jsonify({"error": "Original analysis not found"}), 404

    data = request.get_json()
    refinement_prompt = data.get('refinement_prompt', '').strip()

    if not refinement_prompt:
        return jsonify({"error": "Refinement prompt is required"}), 400

    original_job = analysis_jobs[run_id]
    original_filename = original_job.get('filename', 'unknown')
    original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)

    # Check if original file still exists
    if not os.path.exists(original_filepath):
        return jsonify({"error": "Original Excel file not found"}), 404

    # Generate new run_id for refinement
    new_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize job tracking
    analysis_jobs[new_run_id] = {
        'status': 'starting',
        'message': 'Refining analysis based on your feedback...',
        'filename': original_filename,
        'events': [],
        'event_count': 0,
        'is_refinement': True,
        'original_run_id': run_id,
        'refinement_prompt': refinement_prompt
    }

    # Start refinement in background thread
    thread = threading.Thread(
        target=run_analysis_async,
        args=(new_run_id, original_filepath, app.config['OUTPUT_FOLDER'], refinement_prompt, run_id)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        "success": True,
        "new_run_id": new_run_id,
        "status_url": f"/status/{new_run_id}"
    })


@app.route('/status/<run_id>')
def check_status(run_id):
    """Check analysis status with detailed progress."""
    if run_id not in analysis_jobs:
        return jsonify({"status": "not_found", "error": "Analysis job not found"}), 404

    job = analysis_jobs[run_id]

    response = {
        "status": job.get('status', 'unknown'),
        "message": job.get('message', ''),
        "filename": job.get('filename', ''),
        "events": job.get('events', [])[-100:],  # Return last 100 events to avoid huge payloads
        "event_count": job.get('event_count', 0)
    }

    if job['status'] == 'completed':
        result = job.get('result', {})
        response['dashboard_url'] = f"/dashboard/{result.get('run_id', run_id)}"
        response['ready'] = True
    elif job['status'] == 'error':
        response['error'] = job.get('error', 'Unknown error')
        response['ready'] = False
    else:
        response['ready'] = False

    return jsonify(response)


if __name__ == '__main__':
    # Disable reloader to prevent Flask from restarting when agent creates/edits files
    # Keep debug=True for error messages, but use_reloader=False to prevent auto-restart
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
