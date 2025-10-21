"""
Flask App for Excel Insights Dashboard
"""
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import authentication and database modules
from auth import AuthManager, login_required, admin_required, registered_user_required, create_guest_session, is_guest_user, is_authenticated_user
from database import db, User, Analysis, ActivityLog
from email_service import email_service
from chat_service import get_chat_service
from debug_routes import register_debug_routes

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
from large_file_handler import LargeFileAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size (supports large files)
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Large file handling configuration
app.config['LARGE_FILE_THRESHOLD'] = 30 * 1024 * 1024  # 30MB - files above this use incremental processing
app.config['CHUNK_SIZE'] = 1000  # Number of rows to process per chunk
app.config['METADATA_DIR'] = 'metadata'  # Directory for storing file metadata

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)
Path(app.config['METADATA_DIR']).mkdir(exist_ok=True)

# Initialize authentication manager
auth_manager = AuthManager('users.xml')

# Track analysis jobs
analysis_jobs = {}


def persist_job_state(run_id):
    """Persist the current job state to database for session recovery."""
    # NOTE: Job state persistence is disabled - requires job_state column in database
    # Uncomment and add migration when implementing full job persistence
    return

    # if run_id not in analysis_jobs:
    #     return

    # job = analysis_jobs[run_id]
    # user_id = job.get('user_id')

    # # Skip persistence for guest users (no database tracking)
    # if not user_id:
    #     return

    # try:
    #     Analysis.update_job_state(run_id, job)
    # except Exception as e:
    #     print(f"⚠️  Failed to persist job state for {run_id}: {e}")


def restore_jobs_from_database():
    """Restore active jobs from database on server startup."""
    # NOTE: Job state restoration is disabled - requires job_state column in database
    # Jobs will be marked as error if server restarts during analysis
    return

    # try:
    #     active_jobs = Analysis.get_active_jobs()

    #     for job_record in active_jobs:
    #         run_id = job_record['run_id']
    #         job_state = job_record.get('job_state')

    #         if job_state:
    #             # Restore job to in-memory dict
    #             analysis_jobs[run_id] = job_state
    #             print(f"✅ Restored active job: {run_id} (status: {job_state.get('status')})")
    #         else:
    #             # Job exists in DB but has no state - mark as error
    #             analysis_jobs[run_id] = {
    #                 'status': 'error',
    #                 'message': 'Job state lost due to server restart',
    #                 'filename': job_record['filename'],
    #                 'user_id': job_record['user_id'],
    #                 'events': [],
    #                 'event_count': 0,
    #                 'error': 'Server was restarted - job state not recoverable'
    #             }
    #             Analysis.update_status(run_id, 'error', {'error': 'Server restart'})

    #     if len(active_jobs) > 0:
    #         print(f"📦 Restored {len(active_jobs)} active job(s) from database")

    # except Exception as e:
    #     print(f"⚠️  Failed to restore jobs from database: {e}")


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
@login_required
def index():
    """Home page with upload form."""
    return render_template('index.html', user=session.get('user'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('נא להזין שם משתמש וסיסמה', 'error')
            return render_template('login.html')

        # Authenticate user
        user_data = auth_manager.authenticate(username, password)

        if user_data:
            # Set session
            session['user'] = user_data
            session.permanent = True

            # Update/create user in database (optional - gracefully handle if DB unavailable)
            try:
                db_user = User.create_or_update(
                    username=user_data['username'],
                    full_name=user_data['full_name'],
                    email=user_data.get('email')
                )

                # Log login activity
                ActivityLog.log_event(
                    user_id=db_user['id'],
                    analysis_id=None,
                    event_type='login',
                    event_data={'ip': request.remote_addr}
                )

                session['user_id'] = db_user['id']

            except Exception as e:
                # Database unavailable - continue without DB tracking
                print(f"⚠️  Database unavailable during login (continuing without DB tracking): {e}")
                session['user_id'] = None

            flash(f'ברוך הבא, {user_data["full_name"]}!', 'success')

            # Redirect to next page or index
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('שם משתמש או סיסמה שגויים', 'error')
            return render_template('login.html')

    # GET request - show login form
    if 'user' in session:
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/guest-login')
def guest_login():
    """Create guest session and redirect to home."""
    guest_data = create_guest_session()
    session['user'] = guest_data
    session.permanent = True

    # Don't create database user for guests, just set a flag
    session['user_id'] = None  # No database tracking for guests
    session['is_guest'] = True

    flash(f'ברוך הבא, {guest_data["full_name"]}! אתה משתמש במצב אורח.', 'success')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Logout handler."""
    is_guest = session.get('is_guest', False)

    if not is_guest and 'user_id' in session and session['user_id'] is not None:
        try:
            ActivityLog.log_event(
                user_id=session['user_id'],
                analysis_id=None,
                event_type='logout',
                event_data={'ip': request.remote_addr}
            )
        except Exception as e:
            print(f"⚠️  Database unavailable during logout: {e}")

    session.clear()

    if is_guest:
        flash('יצאת ממצב אורח', 'success')
    else:
        flash('התנתקת בהצלחה', 'success')

    return redirect(url_for('login'))


def run_analysis_async(run_id, filepath, output_dir, additional_instructions=None, refinement_prompt=None, original_run_id=None):
    """Run analysis in background thread."""
    try:
        # Check if this is a large file requiring incremental processing
        file_size = os.path.getsize(filepath)
        is_large_file = file_size > app.config['LARGE_FILE_THRESHOLD']

        if refinement_prompt:
            analysis_jobs[run_id]['status'] = 'running'
            analysis_jobs[run_id]['message'] = 'Claude Agent is refining your analysis...'
        else:
            analysis_jobs[run_id]['status'] = 'running'
            if is_large_file:
                analysis_jobs[run_id]['message'] = f'Large file detected ({file_size / (1024*1024):.1f} MB) - Using incremental processing...'
                analysis_jobs[run_id]['is_large_file'] = True
            else:
                analysis_jobs[run_id]['message'] = 'Claude Agent is deeply analyzing your data...'
                analysis_jobs[run_id]['is_large_file'] = False

        # Persist initial running state
        persist_job_state(run_id)
        # Initialize monitoring EARLY (before metadata extraction)
        from agent_monitor import AgentMonitor
        from pathlib import Path as MonitorPath
        
        # Create output directory for this run
        run_output_dir = MonitorPath(output_dir) / run_id
        run_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize monitor
        monitor = AgentMonitor(run_id, output_dir=output_dir)
        monitor.set_configuration({
            'file_size_mb': round(file_size / (1024*1024), 2),
            'is_large_file': is_large_file,
            'additional_instructions': additional_instructions,
            'refinement_prompt': refinement_prompt
        })
        
        print(f"[DEBUG] Monitor initialized for run_id: {run_id}")
        print(f"[DEBUG] Monitor object: {monitor}")
        print(f"[DEBUG] Monitor will save to: {run_output_dir}/agent_monitor.json")


        # Define event callback to receive real-time events
        def event_callback(log_entry):
            """Receive events from agent in real-time."""
            print(f"\n[EVENT-CALLBACK] ========== EVENT RECEIVED ==========")
            print(f"[EVENT-CALLBACK] Flask received event: {log_entry}")
            analysis_jobs[run_id]['events'].append(log_entry)
            analysis_jobs[run_id]['event_count'] += 1
            print(f"[EVENT-CALLBACK] Total events now: {analysis_jobs[run_id]['event_count']}")

            # Also record in monitor for debugging
            print(f"[EVENT-CALLBACK] About to record in monitor...")
            print(f"[EVENT-CALLBACK] Monitor object available: {monitor is not None}")
            print(f"[EVENT-CALLBACK] Monitor type: {type(monitor)}")

            try:
                # Create content block wrapper that mimics Claude SDK TextBlock
                class TextBlockWrapper:
                    def __init__(self, text_content):
                        self.text = text_content  # This is what the parser looks for!

                # Create a mock event for metadata extraction
                class MetadataEvent:
                    def __init__(self, log_entry):
                        # Set event type (for monitor filtering)
                        self.type = "message"  # Recognized type
                        self.role = "assistant"
                        # Wrap string content in a TextBlock-like object
                        text_content = log_entry.get('content', '')
                        self.content = [TextBlockWrapper(text_content)]  # List of blocks!
                        self.timestamp = log_entry.get('timestamp', '')
                        self.event_type = log_entry.get('type', 'metadata')
                        # Store original metadata
                        self.metadata = {
                            'icon': log_entry.get('icon', ''),
                            'source': 'metadata_extraction'
                        }

                print(f"[EVENT-CALLBACK] Creating MetadataEvent wrapper...")
                mock_event = MetadataEvent(log_entry)
                print(f"[EVENT-CALLBACK] Mock event created: {mock_event}")
                print(f"[EVENT-CALLBACK] Mock event.content: {mock_event.content}")
                print(f"[EVENT-CALLBACK] Mock event.content[0].text: {mock_event.content[0].text}")

                print(f"[EVENT-CALLBACK] Calling monitor.record_event()...")
                monitor.record_event(mock_event, event_type='metadata_extraction')
                print(f"[EVENT-CALLBACK] monitor.record_event() completed successfully!")

            except Exception as e:
                import traceback
                print(f"[EVENT-CALLBACK-ERROR] Could not record metadata event in monitor!")
                print(f"[EVENT-CALLBACK-ERROR] Exception: {e}")
                print(f"[EVENT-CALLBACK-ERROR] Traceback:")
                traceback.print_exc()


            # Persist state every 5 events for efficiency
            if analysis_jobs[run_id]['event_count'] % 5 == 0:
                persist_job_state(run_id)

        # Send initial event
        if refinement_prompt:
            event_callback({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'type': 'text',
                'content': f'Refinement started: "{refinement_prompt[:100]}..."',
                'icon': '🔄'
            })
        elif additional_instructions:
            event_callback({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'type': 'text',
                'content': f'Analysis started with custom instructions: "{additional_instructions[:100]}..."',
                'icon': '🚀'
            })
        else:
            event_callback({
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'type': 'text',
                'content': 'Analysis started - initializing Claude Agent SDK...',
                'icon': '🚀'
            })

        # For large files, extract metadata first
        metadata_path = None
        if is_large_file and not refinement_prompt:
            try:
                event_callback({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'type': 'text',
                    'content': '🔍 Phase 1: Extracting file structure and metadata...',
                    'icon': '📊'
                })

                analyzer = LargeFileAnalyzer(
                    filepath,
                    metadata_dir=app.config['METADATA_DIR'],
                    chunk_size=app.config['CHUNK_SIZE']
                )

                metadata_path = analyzer.extract_and_save_metadata(run_id, event_callback)

                event_callback({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'type': 'text',
                    'content': f'✅ Metadata extracted and saved to {os.path.basename(metadata_path)}',
                    'icon': '✨'
                })

                event_callback({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'type': 'text',
                    'content': '🤖 Phase 2: Claude analyzing data with metadata...',
                    'icon': '🚀'
                })

            except Exception as meta_error:
                event_callback({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'type': 'error',
                    'content': f'⚠️ Metadata extraction failed: {str(meta_error)} - Falling back to standard processing',
                    'icon': '❌'
                })
                metadata_path = None

        result = analyze_excel_file(
            file_path=filepath,
            output_dir=output_dir,
            event_callback=event_callback,
            additional_instructions=additional_instructions,
            refinement_prompt=refinement_prompt,
            original_run_id=original_run_id,
            monitor=monitor,  # Pass monitor for continuation
            metadata_path=metadata_path,  # Pass metadata for large files
            is_large_file=is_large_file
        )

        analysis_jobs[run_id]['status'] = 'completed'
        analysis_jobs[run_id]['result'] = result
        analysis_jobs[run_id]['message'] = 'Analysis complete!' if not refinement_prompt else 'Refinement complete!'

        # Update database status (skip for guests)
        user_id = analysis_jobs[run_id].get('user_id')
        if user_id:
            try:
                Analysis.update_status(run_id, 'completed', result)
                print(f"✅ Updated database status to 'completed' for run_id: {run_id}")
            except Exception as db_error:
                print(f"⚠️ Failed to update database status: {db_error}")

        # Persist completed state
        persist_job_state(run_id)

        # Send email notification if requested
        if analysis_jobs[run_id].get('send_email') and analysis_jobs[run_id].get('user_email'):
            try:
                # Build full dashboard URL
                base_url = request.url_root if request else 'http://localhost:5000/'
                dashboard_url = f"{base_url}dashboard/{run_id}"

                email_service.send_analysis_complete(
                    to_email=analysis_jobs[run_id]['user_email'],
                    user_name=analysis_jobs[run_id].get('user_full_name', 'User'),
                    filename=analysis_jobs[run_id].get('filename', 'file.xlsx'),
                    dashboard_url=dashboard_url,
                    run_id=run_id
                )
                print(f"✉️ Email notification sent to {analysis_jobs[run_id]['user_email']}")
            except Exception as email_error:
                print(f"❌ Failed to send email notification: {email_error}")

    except Exception as e:
        analysis_jobs[run_id]['status'] = 'error'
        analysis_jobs[run_id]['error'] = str(e)
        analysis_jobs[run_id]['message'] = f'Error: {str(e)}'

        # Update database status (skip for guests)
        user_id = analysis_jobs[run_id].get('user_id')
        if user_id:
            try:
                Analysis.update_status(run_id, 'error', {'error': str(e)})
                print(f"✅ Updated database status to 'error' for run_id: {run_id}")
            except Exception as db_error:
                print(f"⚠️ Failed to update database status: {db_error}")

        # Persist error state
        persist_job_state(run_id)

        # Send error notification email if requested
        if analysis_jobs[run_id].get('send_email') and analysis_jobs[run_id].get('user_email'):
            try:
                email_service.send_analysis_error(
                    to_email=analysis_jobs[run_id]['user_email'],
                    user_name=analysis_jobs[run_id].get('user_full_name', 'User'),
                    filename=analysis_jobs[run_id].get('filename', 'file.xlsx'),
                    error_message=str(e),
                    run_id=run_id
                )
                print(f"✉️ Error notification sent to {analysis_jobs[run_id]['user_email']}")
            except Exception as email_error:
                print(f"❌ Failed to send error notification: {email_error}")


@app.route('/upload', methods=['POST'])
@login_required
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

        # Create analysis record in database (skip for guests)
        user_id = session.get('user_id')
        is_guest = session.get('is_guest', False)

        if not is_guest and user_id:
            try:
                db_analysis = Analysis.create(
                    user_id=user_id,
                    filename=filename,
                    run_id=run_id
                )

                # Log upload activity
                ActivityLog.log_event(
                    user_id=user_id,
                    analysis_id=db_analysis['id'],
                    event_type='upload',
                    event_data={'filename': filename, 'filesize': os.path.getsize(filepath)}
                )

            except Exception as e:
                print(f"Database error during upload: {e}")

        # Get email notification preference
        send_email = request.form.get('send_email') == 'true'
        user_email = session.get('user', {}).get('email')
        user_full_name = session.get('user', {}).get('full_name', 'User')

        # Get additional instructions if provided
        additional_instructions = request.form.get('additional_instructions', '').strip()

        # Detect if file is large
        file_size = os.path.getsize(filepath)
        is_large_file = file_size > app.config['LARGE_FILE_THRESHOLD']

        # Initialize job tracking
        analysis_jobs[run_id] = {
            'status': 'starting',
            'message': f'Starting analysis... ({file_size / (1024*1024):.1f} MB file)' if is_large_file else 'Starting analysis...',
            'filename': filename,
            'user_id': user_id,
            'events': [],  # Store activity log
            'event_count': 0,  # Track for efficient polling
            'send_email': send_email and user_email is not None,  # Only if user has email
            'user_email': user_email,
            'user_full_name': user_full_name,
            'additional_instructions': additional_instructions,  # Store user instructions
            'is_large_file': is_large_file,
            'file_size_mb': round(file_size / (1024 * 1024), 2)
        }

        # Persist initial job state
        persist_job_state(run_id)

        # Start analysis in background thread (NO TIMEOUT!)
        thread = threading.Thread(
            target=run_analysis_async,
            args=(run_id, filepath, app.config['OUTPUT_FOLDER'], additional_instructions)
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
@login_required
def view_dashboard(run_id):
    """Display the generated dashboard with refinement panel."""
    dashboard_path = Path(app.config['OUTPUT_FOLDER']) / run_id / "dashboard.html"

    if dashboard_path.exists():
        # Log dashboard view (skip for guests)
        user_id = session.get('user_id')
        is_guest = session.get('is_guest', False)

        if not is_guest and user_id:
            try:
                db_analysis = Analysis.get_by_run_id(run_id)
                if db_analysis:
                    ActivityLog.log_event(
                        user_id=user_id,
                        analysis_id=db_analysis['id'],
                        event_type='view_dashboard',
                        event_data={'run_id': run_id}
                    )
            except Exception as e:
                print(f"Error logging dashboard view: {e}")

        # Return wrapper template with refinement form
        return render_template('dashboard_wrapper.html', run_id=run_id, user=session.get('user'))
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
@login_required
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

    # Create refinement analysis record (skip for guests)
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)

    if not is_guest and user_id:
        try:
            db_analysis = Analysis.create(
                user_id=user_id,
                filename=original_filename,
                run_id=new_run_id
            )

            # Log refinement activity
            original_analysis = Analysis.get_by_run_id(run_id)
            ActivityLog.log_event(
                user_id=user_id,
                analysis_id=db_analysis['id'],
                event_type='refine',
                event_data={
                    'refinement_prompt': refinement_prompt,
                    'original_run_id': run_id,
                    'original_analysis_id': original_analysis['id'] if original_analysis else None
                }
            )

        except Exception as e:
            print(f"Database error during refinement: {e}")

    # Initialize job tracking
    analysis_jobs[new_run_id] = {
        'status': 'starting',
        'message': 'Refining analysis based on your feedback...',
        'filename': original_filename,
        'user_id': user_id,
        'events': [],
        'event_count': 0,
        'is_refinement': True,
        'original_run_id': run_id,
        'refinement_prompt': refinement_prompt
    }

    # Persist initial refinement job state
    persist_job_state(new_run_id)

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
@login_required
def check_status(run_id):
    """Check analysis status with detailed progress."""
    if run_id not in analysis_jobs:
        return jsonify({"status": "not_found", "error": "Analysis job not found"}), 404

    job = analysis_jobs[run_id]

    # Update database status (skip for guests)
    is_guest = session.get('is_guest', False)
    if not is_guest:
        try:
            if job['status'] == 'completed':
                Analysis.update_status(run_id, 'completed', job.get('result'))
            elif job['status'] == 'error':
                Analysis.update_status(run_id, 'error', {'error': job.get('error')})
        except Exception as e:
            print(f"Error updating analysis status: {e}")

    response = {
        "status": job.get('status', 'unknown'),
        "message": job.get('message', ''),
        "filename": job.get('filename', ''),
        "events": job.get('events', [])[-100:],  # Return last 100 events to avoid huge payloads
        "event_count": job.get('event_count', 0),
        "is_large_file": job.get('is_large_file', False),
        "file_size_mb": job.get('file_size_mb', 0)
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


# ========== CHAT ROUTES ==========

@app.route('/chat/<run_id>/init', methods=['POST'])
@login_required
def init_chat_session(run_id):
    """Initialize a chat session for an Excel file."""
    # Find the original file path from analysis jobs or database
    file_path = None
    filename = None
    dashboard_path = None

    # First, try to get from in-memory analysis_jobs (for fresh uploads)
    if run_id in analysis_jobs:
        filename = analysis_jobs[run_id].get('filename')
        if filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # If not found, try to get from database (for history access)
    if not file_path:
        try:
            analysis = Analysis.get_by_run_id(run_id)
            if analysis and analysis.get('filename'):
                filename = analysis['filename']
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        except Exception as e:
            print(f"Error looking up analysis from database: {e}")

    # Check if file exists
    if not file_path or not os.path.exists(file_path):
        return jsonify({
            'error': 'Excel file not found for this analysis',
            'success': False
        }), 404

    # Check if dashboard exists (to include analysis context)
    dashboard_file = Path(app.config['OUTPUT_FOLDER']) / run_id / "dashboard.html"
    if dashboard_file.exists():
        dashboard_path = str(dashboard_file)

    try:
        chat_svc = get_chat_service()
        session_info = chat_svc.initialize_session(run_id, file_path, dashboard_path)

        return jsonify({
            'success': True,
            **session_info
        })

    except Exception as e:
        return jsonify({
            'error': f'Failed to initialize chat: {str(e)}',
            'success': False
        }), 500


@app.route('/chat/<run_id>', methods=['GET'])
@login_required
def get_chat_info(run_id):
    """Get chat session info and conversation history."""
    try:
        chat_svc = get_chat_service()
        session_info = chat_svc.get_session_info(run_id)

        if session_info is None:
            return jsonify({
                'error': 'Chat session not found',
                'success': False,
                'initialized': False
            }), 404

        return jsonify({
            'success': True,
            'initialized': True,
            **session_info
        })

    except Exception as e:
        return jsonify({
            'error': f'Failed to get chat info: {str(e)}',
            'success': False
        }), 500


@app.route('/chat/<run_id>/message', methods=['POST'])
@login_required
def send_chat_message(run_id):
    """Send a message in the chat session."""
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({
            'error': 'Message cannot be empty',
            'success': False
        }), 400

    try:
        chat_svc = get_chat_service()
        result = chat_svc.send_message(run_id, user_message)

        if not result.get('success'):
            status_code = 400 if result.get('limit_reached') else 500
            return jsonify(result), status_code

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'Failed to send message: {str(e)}',
            'success': False
        }), 500


@app.route('/chat/<run_id>/clear', methods=['POST'])
@login_required
def clear_chat_session(run_id):
    """Clear a chat session."""
    try:
        chat_svc = get_chat_service()
        success = chat_svc.clear_session(run_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Chat session cleared'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Chat session not found'
            }), 404

    except Exception as e:
        return jsonify({
            'error': f'Failed to clear chat: {str(e)}',
            'success': False
        }), 500


@app.route('/api/active-jobs')
@login_required
def get_active_jobs():
    """Get all active jobs for the current user (for session restoration)."""
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)

    # Guests don't have persistent jobs
    if is_guest or not user_id:
        return jsonify({"active_jobs": []})

    try:
        # Get active jobs from database
        active_jobs = Analysis.get_active_jobs(user_id)

        # Build response with job info
        jobs_list = []
        for job_record in active_jobs:
            run_id = job_record['run_id']
            # Check if job is in memory
            if run_id in analysis_jobs:
                job = analysis_jobs[run_id]
                jobs_list.append({
                    'run_id': run_id,
                    'filename': job.get('filename', ''),
                    'status': job.get('status', 'unknown'),
                    'message': job.get('message', ''),
                    'is_refinement': job.get('is_refinement', False)
                })
            else:
                # Job not in memory - it's a stale job (server restarted)
                # Mark it as error in database so it doesn't show as active anymore
                try:
                    Analysis.update_status(
                        run_id,
                        'error',
                        {'error': 'Server restarted - job state lost'}
                    )
                    print(f"⚠️ Marked stale job {run_id} as error (server restart)")
                except Exception as update_error:
                    print(f"⚠️ Failed to update stale job {run_id}: {update_error}")

                # Don't include in active jobs list since it's stale

        return jsonify({"active_jobs": jobs_list})

    except Exception as e:
        print(f"Error getting active jobs: {e}")
        return jsonify({"active_jobs": [], "error": str(e)})


# ========== USER HISTORY ROUTE ==========

@app.route('/my-history')
@login_required
def my_history():
    """User history page - view past analyses and activity."""
    print(f"📊 /my-history accessed by user: {session.get('user', {}).get('username', 'unknown')}")
    print(f"   Session user_id: {session.get('user_id')}")
    print(f"   Is guest: {session.get('is_guest', False)}")

    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)

    # Guests don't have database history
    if is_guest:
        print(f"📊 Showing empty history for guest user")
        return render_template('history.html',
                             analyses=[],
                             activity_logs=[],
                             is_guest=True,
                             user=session.get('user'))

    # Authenticated user but no database ID (database was unavailable during login)
    if not user_id:
        print(f"📊 Authenticated user but no database ID - database may be unavailable")
        return render_template('history.html',
                             analyses=[],
                             activity_logs=[],
                             is_guest=False,
                             user=session.get('user'),
                             database_unavailable=True)

    try:
        print(f"📊 Fetching analyses for user_id: {user_id}")
        # Get user's analyses
        analyses = Analysis.get_user_analyses(user_id, limit=100)
        print(f"   Found {len(analyses) if analyses else 0} analyses")

        print(f"📊 Fetching activity logs for user_id: {user_id}")
        # Get user's activity logs
        activity_logs = ActivityLog.get_user_activity(user_id, limit=200)
        print(f"   Found {len(activity_logs) if activity_logs else 0} activity logs")

        return render_template('history.html',
                             analyses=analyses,
                             activity_logs=activity_logs,
                             is_guest=False,
                             user=session.get('user'))

    except Exception as e:
        print(f"❌ Error in /my-history route: {str(e)}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

        # Instead of redirecting, show error page with details
        flash(f'שגיאה בטעינת ההיסטוריה: {str(e)}', 'error')

        # Try to render history page with empty data instead of redirecting
        return render_template('history.html',
                             analyses=[],
                             activity_logs=[],
                             is_guest=False,
                             user=session.get('user'),
                             error=str(e))


# ========== ADMIN PANEL ROUTES ==========

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel - user management."""
    try:
        # Get all users from YAML
        yaml_users = auth_manager.get_all_users()

        # Get user activity from database
        users_with_stats = []
        for user in yaml_users:
            try:
                db_user = User.get_by_username(user['username'])
                if db_user:
                    # Get user analyses count
                    analyses = Analysis.get_user_analyses(db_user['id'], limit=1000)
                    analyses_count = len(analyses)

                    # Get recent activity
                    recent_activity = ActivityLog.get_user_activity(db_user['id'], limit=10)

                    users_with_stats.append({
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'email': user.get('email'),
                        'role': user['role'],
                        'last_login': db_user.get('last_login'),
                        'created_at': db_user.get('created_at'),
                        'analyses_count': analyses_count,
                        'recent_activity': recent_activity
                    })
                else:
                    # User exists in YAML but not in DB yet
                    users_with_stats.append({
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'email': user.get('email'),
                        'role': user['role'],
                        'last_login': None,
                        'created_at': None,
                        'analyses_count': 0,
                        'recent_activity': []
                    })
            except Exception as e:
                print(f"Error getting stats for user {user['username']}: {e}")
                users_with_stats.append({
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user.get('email'),
                    'role': user['role'],
                    'last_login': None,
                    'created_at': None,
                    'analyses_count': 0,
                    'recent_activity': []
                })

        return render_template('admin.html', users=users_with_stats, user=session.get('user'))

    except Exception as e:
        flash(f'שגיאה בטעינת פאנל הניהול: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/admin/add-user', methods=['POST'])
@admin_required
def admin_add_user():
    """Add new user (admin only)."""
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify({"success": False, "error": "שם משתמש וסיסמה נדרשים"}), 400

    if role not in ['admin', 'user']:
        return jsonify({"success": False, "error": "תפקיד לא חוקי"}), 400

    try:
        success = auth_manager.add_user(username, password, full_name, email, role)

        if success:
            # Log activity
            ActivityLog.log_event(
                user_id=session.get('user_id'),
                analysis_id=None,
                event_type='admin_add_user',
                event_data={'new_username': username, 'role': role}
            )

            return jsonify({"success": True, "message": f"משתמש {username} נוסף בהצלחה"})
        else:
            return jsonify({"success": False, "error": "שם משתמש כבר קיים"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/admin/update-user', methods=['POST'])
@admin_required
def admin_update_user():
    """Update existing user (admin only)."""
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip() if data.get('email') else None
    role = data.get('role')

    if not username:
        return jsonify({"success": False, "error": "שם משתמש נדרש"}), 400

    try:
        success = auth_manager.update_user(
            username=username,
            password=password if password else None,
            full_name=full_name if full_name else None,
            email=email,
            role=role if role else None
        )

        if success:
            # Log activity
            ActivityLog.log_event(
                user_id=session.get('user_id'),
                analysis_id=None,
                event_type='admin_update_user',
                event_data={'updated_username': username}
            )

            return jsonify({"success": True, "message": f"משתמש {username} עודכן בהצלחה"})
        else:
            return jsonify({"success": False, "error": "משתמש לא נמצא"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/admin/delete-user', methods=['POST'])
@admin_required
def admin_delete_user():
    """Delete user (admin only)."""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        return jsonify({"success": False, "error": "שם משתמש נדרש"}), 400

    # Prevent deleting yourself
    if username == session.get('user', {}).get('username'):
        return jsonify({"success": False, "error": "לא ניתן למחוק את המשתמש שלך"}), 400

    try:
        success = auth_manager.delete_user(username)

        if success:
            # Log activity
            ActivityLog.log_event(
                user_id=session.get('user_id'),
                analysis_id=None,
                event_type='admin_delete_user',
                event_data={'deleted_username': username}
            )

            return jsonify({"success": True, "message": f"משתמש {username} נמחק בהצלחה"})
        else:
            return jsonify({"success": False, "error": "לא ניתן למחוק משתמש זה"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# Register debug monitoring routes
register_debug_routes(app, analysis_jobs, login_required)

if __name__ == '__main__':
    # Restore any active jobs from database on startup
    print("🔄 Checking for active jobs to restore...")
    restore_jobs_from_database()

    # Disable reloader to prevent Flask from restarting when agent creates/edits files
    # Keep debug=True for error messages, but use_reloader=False to prevent auto-restart
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
