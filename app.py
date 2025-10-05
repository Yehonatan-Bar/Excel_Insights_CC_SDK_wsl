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
from auth import AuthManager, login_required, admin_required
from database import db, User, Analysis, ActivityLog

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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

# Initialize authentication manager
auth_manager = AuthManager('users.yaml')

# Track analysis jobs
analysis_jobs = {}


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

            # Update/create user in database
            try:
                db_user = User.create_or_update(
                    username=user_data['username'],
                    full_name=user_data['full_name']
                )

                # Log login activity
                ActivityLog.log_event(
                    user_id=db_user['id'],
                    analysis_id=None,
                    event_type='login',
                    event_data={'ip': request.remote_addr}
                )

                session['user_id'] = db_user['id']

                flash(f'ברוך הבא, {user_data["full_name"]}!', 'success')

                # Redirect to next page or index
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))

            except Exception as e:
                print(f"Database error during login: {e}")
                flash('שגיאה בהתחברות למערכת', 'error')
                return render_template('login.html')
        else:
            flash('שם משתמש או סיסמה שגויים', 'error')
            return render_template('login.html')

    # GET request - show login form
    if 'user' in session:
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout handler."""
    if 'user_id' in session:
        try:
            ActivityLog.log_event(
                user_id=session['user_id'],
                analysis_id=None,
                event_type='logout',
                event_data={'ip': request.remote_addr}
            )
        except Exception as e:
            print(f"Error logging logout: {e}")

    session.clear()
    flash('התנתקת בהצלחה', 'success')
    return redirect(url_for('login'))


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

        # Create analysis record in database
        user_id = session.get('user_id')
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

        # Initialize job tracking
        analysis_jobs[run_id] = {
            'status': 'starting',
            'message': 'Starting analysis...',
            'filename': filename,
            'user_id': user_id,
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
@login_required
def view_dashboard(run_id):
    """Display the generated dashboard with refinement panel."""
    dashboard_path = Path(app.config['OUTPUT_FOLDER']) / run_id / "dashboard.html"

    if dashboard_path.exists():
        # Log dashboard view
        user_id = session.get('user_id')
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

    # Create refinement analysis record
    user_id = session.get('user_id')
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

    # Update database status
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
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify({"success": False, "error": "שם משתמש וסיסמה נדרשים"}), 400

    if role not in ['admin', 'user']:
        return jsonify({"success": False, "error": "תפקיד לא חוקי"}), 400

    try:
        success = auth_manager.add_user(username, password, full_name, role)

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
    role = data.get('role')

    if not username:
        return jsonify({"success": False, "error": "שם משתמש נדרש"}), 400

    try:
        success = auth_manager.update_user(
            username=username,
            password=password if password else None,
            full_name=full_name if full_name else None,
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


if __name__ == '__main__':
    # Disable reloader to prevent Flask from restarting when agent creates/edits files
    # Keep debug=True for error messages, but use_reloader=False to prevent auto-restart
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
