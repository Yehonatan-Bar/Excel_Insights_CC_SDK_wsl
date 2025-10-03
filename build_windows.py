"""
Build Windows Executable for Excel Insights Dashboard
Creates a standalone Windows package with embedded API key
"""
import os
import sys
import shutil
from pathlib import Path

def build_windows_package():
    """Create Windows standalone package."""

    print("=" * 70)
    print("🚀 Building Windows Standalone Package")
    print("=" * 70)

    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in environment!")
        print("Please set it before building:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-YOUR_KEY_HERE'")
        sys.exit(1)

    print(f"\n✅ API Key found: {api_key[:20]}...")

    # Create build directory
    build_dir = Path("dist/Excel_Insights_Windows")
    if build_dir.exists():
        print(f"\n🗑️  Removing old build: {build_dir}")
        shutil.rmtree(build_dir)

    build_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created build directory: {build_dir}")

    # Copy application files
    print("\n📁 Copying application files...")
    files_to_copy = [
        'app.py',
        'agent_service.py',
        'excel_mcp_tools.py',
        'requirements.txt',
        'README.md'
    ]

    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy(file, build_dir / file)
            print(f"  ✓ {file}")

    # Copy directories
    dirs_to_copy = ['templates', 'static']
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, build_dir / dir_name, dirs_exist_ok=True)
            print(f"  ✓ {dir_name}/")

    # Create .env file with embedded API key
    env_file = build_dir / '.env'
    with open(env_file, 'w') as f:
        f.write(f"ANTHROPIC_API_KEY={api_key}\n")
    print(f"\n✅ Created .env with embedded API key")

    # Create batch launcher for Windows
    launcher_bat = build_dir / 'START_HERE.bat'
    with open(launcher_bat, 'w') as f:
        f.write('''@echo off
echo ========================================
echo Excel Insights Dashboard - AI Powered
echo ========================================
echo.
echo Starting Flask server...
echo Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
call venv\\Scripts\\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv\\Lib\\site-packages\\flask" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the Flask app
echo.
echo ========================================
echo Server starting at http://localhost:5000
echo ========================================
echo.
python app.py

pause
''')
    print(f"✅ Created Windows launcher: START_HERE.bat")

    # Create PowerShell launcher (alternative)
    launcher_ps1 = build_dir / 'START_HERE.ps1'
    with open(launcher_ps1, 'w') as f:
        f.write('''# Excel Insights Dashboard Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Excel Insights Dashboard - AI Powered" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if needed
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\\venv\\Scripts\\Activate.ps1"

# Install dependencies if needed
if (-not (Test-Path "venv\\Lib\\site-packages\\flask")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Run Flask app
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server starting at http://localhost:5000" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python app.py

Read-Host "Press Enter to exit"
''')
    print(f"✅ Created PowerShell launcher: START_HERE.ps1")

    # Create README for Windows users
    readme_windows = build_dir / 'README_WINDOWS.txt'
    with open(readme_windows, 'w') as f:
        f.write('''========================================
Excel Insights Dashboard - AI Powered
========================================

🚀 QUICK START FOR WINDOWS:

1. Make sure Python 3.10+ is installed
   - Download from: https://www.python.org/downloads/
   - IMPORTANT: Check "Add Python to PATH" during installation!

2. Double-click "START_HERE.bat" to launch the app
   - First run will install dependencies (takes ~2 minutes)
   - Browser will NOT open automatically

3. Open your browser and go to:
   http://localhost:5000

4. Upload an Excel file (.xlsx or .xls) and watch the AI work!

========================================
ALTERNATIVE LAUNCHER:
========================================

If the .bat file doesn't work, try:
- Right-click "START_HERE.ps1" → "Run with PowerShell"
- Or run from PowerShell: .\\START_HERE.ps1

========================================
API KEY:
========================================

✅ API key is already embedded in this package (.env file)
   No need to set it manually!

If you need to change it, edit the .env file:
   ANTHROPIC_API_KEY=sk-ant-api03-YOUR_NEW_KEY_HERE

========================================
TROUBLESHOOTING:
========================================

Problem: "Python not found"
Solution: Install Python from https://www.python.org/downloads/
          Make sure to check "Add Python to PATH"!

Problem: "Module not found" errors
Solution: Delete the "venv" folder and run START_HERE.bat again

Problem: Browser shows "Connection refused"
Solution: Wait 10-15 seconds after starting, then refresh browser

Problem: Analysis stuck or failing
Solution: Check that you have API credits at https://console.anthropic.com/

========================================
FEATURES:
========================================

✨ Real-time AI analysis with Claude Sonnet 4.5
📊 Automatic visualization generation
💡 Smart insights and pattern detection
🎨 Interactive dashboards
🧠 Watch the AI think and work in real-time

========================================
SUPPORT:
========================================

Documentation: See README.md
GitHub: https://github.com/Yehonatan-Bar/Excel_Insights_CC_SDK_wsl
Claude API: https://console.anthropic.com/

========================================
Built with ❤️ using Claude Sonnet 4.5
========================================
''')
    print(f"✅ Created Windows README: README_WINDOWS.txt")

    # Create uploads and outputs directories
    (build_dir / 'uploads').mkdir(exist_ok=True)
    (build_dir / 'outputs').mkdir(exist_ok=True)
    print(f"✅ Created uploads/ and outputs/ directories")

    # Create .gitignore for the package
    gitignore = build_dir / '.gitignore'
    with open(gitignore, 'w') as f:
        f.write('''venv/
__pycache__/
*.pyc
uploads/*.xlsx
uploads/*.xls
outputs/
.env
*.log
''')
    print(f"✅ Created .gitignore")

    # Summary
    print("\n" + "=" * 70)
    print("✅ Windows Package Built Successfully!")
    print("=" * 70)
    print(f"\nPackage location: {build_dir.absolute()}")
    print(f"Package size: {get_dir_size(build_dir):.2f} MB")
    print("\n📦 Package contents:")
    print("  • Python source files (app.py, agent_service.py, etc.)")
    print("  • Templates and static files")
    print("  • START_HERE.bat (Windows batch launcher)")
    print("  • START_HERE.ps1 (PowerShell launcher)")
    print("  • .env file with embedded API key")
    print("  • README_WINDOWS.txt (setup instructions)")
    print("\n🎉 Ready to distribute!")
    print("\n📋 To use on Windows:")
    print(f"  1. Copy the entire '{build_dir.name}' folder to a Windows PC")
    print("  2. Double-click 'START_HERE.bat'")
    print("  3. Open browser to http://localhost:5000")
    print("\n⚠️  Requirements on target Windows PC:")
    print("  • Python 3.10+ (with 'Add to PATH' enabled)")
    print("  • Internet connection (for pip install on first run)")
    print("=" * 70)

def get_dir_size(path):
    """Get total size of directory in MB."""
    total = 0
    for entry in Path(path).rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total / (1024 * 1024)

if __name__ == '__main__':
    build_windows_package()
