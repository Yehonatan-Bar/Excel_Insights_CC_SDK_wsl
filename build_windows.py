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

    # Create FIRST-TIME SETUP script for Windows
    setup_bat = build_dir / 'SETUP_FIRST_TIME.bat'
    with open(setup_bat, 'w') as f:
        f.write('''@echo off
echo ========================================
echo Excel Insights - FIRST TIME SETUP
echo ========================================
echo.
echo This script will:
echo   1. Check if Python is installed
echo   2. Create virtual environment (venv)
echo   3. Download and install all dependencies
echo.
echo After setup, you can run START_HERE.bat anytime
echo (No internet needed after this setup!)
echo.
echo This may take 2-5 minutes...
echo.
pause

REM Check if Python is installed
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/3] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Deleting old one...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

REM Install dependencies
echo [3/3] Installing dependencies (this may take a few minutes)...
call venv\\Scripts\\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Make sure you have internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Setup Complete!
echo ========================================
echo.
echo All dependencies are now installed in the 'venv' folder.
echo You can now run START_HERE.bat anytime - no internet needed!
echo.
echo Next step: Double-click START_HERE.bat to launch the app
echo.
pause
''')
    print(f"✅ Created first-time setup: SETUP_FIRST_TIME.bat")

    # Create batch launcher for Windows (assumes venv already exists)
    launcher_bat = build_dir / 'START_HERE.bat'
    with open(launcher_bat, 'w') as f:
        f.write('''@echo off
echo ========================================
echo Excel Insights Dashboard - AI Powered
echo ========================================
echo.

REM Check if setup was run
if not exist "venv" (
    echo.
    echo ERROR: Setup not completed!
    echo.
    echo Please run SETUP_FIRST_TIME.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Try running SETUP_FIRST_TIME.bat again
    pause
    exit /b 1
)

REM Run the Flask app
echo Starting Flask server...
echo.
echo ========================================
echo Server running at: http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
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

STEP 1: ONE-TIME SETUP (First time only)
----------------------------------------
1. Make sure Python 3.10+ is installed
   - Download from: https://www.python.org/downloads/
   - IMPORTANT: Check "Add Python to PATH" during installation!

2. Double-click "SETUP_FIRST_TIME.bat"
   - This creates a virtual environment (venv folder)
   - Downloads and installs all dependencies
   - Takes 2-5 minutes (needs internet connection)
   - You only need to do this ONCE!

STEP 2: DAILY USE (After setup)
--------------------------------
1. Double-click "START_HERE.bat" to launch the app
   - No internet needed!
   - Starts immediately (uses pre-installed venv)
   - Browser will NOT open automatically

2. Open your browser and go to:
   http://localhost:5000

3. Upload an Excel file (.xlsx or .xls) and watch the AI work!

========================================
IMPORTANT NOTES:
========================================

✅ After running SETUP_FIRST_TIME.bat once, the 'venv' folder contains
   all dependencies. You can copy this entire folder to another Windows
   PC and use START_HERE.bat directly (no internet needed!)

✅ The venv folder is ~100-200 MB but makes the package fully portable

✅ If you move this folder to another PC, just run START_HERE.bat
   (skip SETUP_FIRST_TIME.bat if venv folder already exists)

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

Problem: "Setup not completed" when running START_HERE.bat
Solution: Run SETUP_FIRST_TIME.bat first to create the venv folder

Problem: "Python not found"
Solution: Install Python from https://www.python.org/downloads/
          Make sure to check "Add Python to PATH"!

Problem: "Module not found" errors
Solution: Delete the "venv" folder and run SETUP_FIRST_TIME.bat again

Problem: Browser shows "Connection refused"
Solution: Wait 10-15 seconds after starting, then refresh browser

Problem: Analysis stuck or failing
Solution: Check that you have API credits at https://console.anthropic.com/

Problem: Want to update dependencies
Solution: Delete "venv" folder and run SETUP_FIRST_TIME.bat again

========================================
FOLDER STRUCTURE AFTER SETUP:
========================================

Excel_Insights_Windows/
├── SETUP_FIRST_TIME.bat   ← Run this once
├── START_HERE.bat         ← Run this daily
├── venv/                  ← Created by setup (100-200 MB)
│   └── (all dependencies installed here)
├── .env                   ← Your API key
├── app.py                 ← Application files
└── ...

========================================
FEATURES:
========================================

✨ Real-time AI analysis with Claude Sonnet 4.5
📊 Automatic visualization generation
💡 Smart insights and pattern detection
🎨 Interactive dashboards
🧠 Watch the AI think and work in real-time
🎨 Color-coded activity monitor with expand/collapse
📱 Works offline after initial setup!

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

    # Ask if user wants to pre-install venv (only works if building on Windows)
    print("\n" + "=" * 70)
    if sys.platform == 'win32':
        print("🪟 Windows detected! Do you want to pre-install dependencies?")
        print("This will create a fully self-contained package.")
        response = input("Pre-install dependencies now? (y/n): ").strip().lower()

        if response == 'y':
            print("\n📦 Creating virtual environment and installing dependencies...")
            print("This may take 2-5 minutes...\n")

            # Create venv
            import subprocess
            venv_path = build_dir / 'venv'
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)

            # Install dependencies
            pip_path = venv_path / 'Scripts' / 'pip.exe'
            subprocess.run([
                str(pip_path), 'install', '-r', str(build_dir / 'requirements.txt')
            ], check=True)

            print("✅ Dependencies pre-installed! Package is fully self-contained.")
            print("📦 Package size with venv:", f"{get_dir_size(build_dir):.2f} MB")
        else:
            print("📋 Dependencies will be installed on first run on target PC")
    else:
        print("ℹ️  Building on Linux/WSL - venv cannot be pre-created for Windows")
        print("📋 Dependencies will be installed when SETUP_FIRST_TIME.bat is run on Windows PC")

    # Summary
    print("\n" + "=" * 70)
    print("✅ Windows Package Built Successfully!")
    print("=" * 70)
    print(f"\nPackage location: {build_dir.absolute()}")
    print(f"Package size: {get_dir_size(build_dir):.2f} MB")
    print("\n📦 Package contents:")
    print("  • Python source files (app.py, agent_service.py, etc.)")
    print("  • Templates and static files")
    print("  • SETUP_FIRST_TIME.bat (one-time dependency installer)")
    print("  • START_HERE.bat (daily launcher)")
    print("  • START_HERE.ps1 (PowerShell launcher)")
    print("  • .env file with embedded API key")
    print("  • README_WINDOWS.txt (setup instructions)")
    if (build_dir / 'venv').exists():
        print("  • venv/ folder (all dependencies pre-installed!)")
    print("\n🎉 Ready to distribute!")
    print("\n📋 To use on Windows:")
    print(f"  1. Copy the entire '{build_dir.name}' folder to a Windows PC")
    if (build_dir / 'venv').exists():
        print("  2. Double-click 'START_HERE.bat' (dependencies already installed!)")
        print("  3. Open browser to http://localhost:5000")
        print("\n✅ NO INTERNET NEEDED - fully self-contained!")
    else:
        print("  2. Double-click 'SETUP_FIRST_TIME.bat' (one-time, needs internet)")
        print("  3. Then run 'START_HERE.bat' anytime (no internet needed)")
        print("  4. Open browser to http://localhost:5000")
        print("\n⚠️  Requirements on target Windows PC:")
        print("  • Python 3.10+ (with 'Add to PATH' enabled)")
        print("  • Internet connection (for SETUP_FIRST_TIME.bat only)")
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
