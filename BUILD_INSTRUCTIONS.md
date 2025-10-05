# 🏗️ Building Windows Standalone Package

This document explains how to create a Windows-ready package with embedded API key.

## 📦 What Gets Created

The build process creates a **portable Windows package** that includes:
- ✅ All application source code
- ✅ Embedded API key (in `.env` file)
- ✅ Automatic launcher scripts (`.bat` and `.ps1`)
- ✅ Easy setup instructions
- ✅ Ready-to-run package (just needs Python on target PC)

## 🚀 Building the Package

### Step 1: Set Your API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY_HERE"
```

### Step 2: Run Build Script

```bash
python3 build_windows.py
```

### Step 3: Package Ready!

The package will be created at:
```
dist/Excel_Insights_Windows/
```

And a compressed archive:
```
dist/Excel_Insights_Windows.tar.gz
```

## 📁 Package Structure

```
Excel_Insights_Windows/
├── START_HERE.bat          # ← Double-click this on Windows!
├── START_HERE.ps1          # ← Alternative PowerShell launcher
├── README_WINDOWS.txt      # ← Setup instructions
├── .env                    # ← Embedded API key
├── app.py                  # Application files
├── agent_service.py
├── excel_mcp_tools.py
├── requirements.txt
├── templates/              # Web templates
├── static/                 # Static files
├── uploads/                # Created on first run
└── outputs/                # Created on first run
```

## 🎯 Using the Package on Windows

### Requirements on Target Windows PC:
- **Python 3.10+** (from https://www.python.org/downloads/)
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation!
- **Node.js 18+** (from https://nodejs.org/)
  - ⚠️ **REQUIRED**: Use LTS version and check "Add to PATH" during installation!
  - ⚠️ **WHY**: Claude Agent SDK requires Node.js and Claude Code CLI to function
- Internet connection (for first-run dependency installation)

### Setup Steps:

1. **Copy** the entire `Excel_Insights_Windows` folder to Windows PC

2. **Double-click** `SETUP_FIRST_TIME.bat`
   - Checks Python and Node.js installations
   - Installs Claude Code CLI (required for AI features)
   - Creates virtual environment with all dependencies
   - Takes 5-10 minutes (needs internet connection)
   - You only need to do this ONCE!

3. **Double-click** `START_HERE.bat` to launch the app
   - Subsequent runs: Starts immediately (no internet needed)

4. **Open browser** to http://localhost:5000

5. **Upload Excel file** and watch AI work!

## 🔧 Alternative Launchers

If `.bat` doesn't work:

**PowerShell:**
```powershell
Right-click START_HERE.ps1 → Run with PowerShell
```

**Command Prompt:**
```cmd
cd Excel_Insights_Windows
venv\Scripts\activate
python app.py
```

## 🔑 API Key Management

### Where is the API key?
The API key is embedded in the `.env` file within the package.

### To change the API key:
Edit `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_NEW_KEY_HERE
```

### Security Note:
⚠️ The `.env` file contains your API key in plain text. Only share this package with trusted users or create separate builds for different users with their own API keys.

## 📊 Package Size

- **Uncompressed**: ~100 KB (source code only)
- **With venv (after first run)**: ~100-200 MB
- **Compressed archive**: ~26 KB

## 🚀 Distribution Options

### Option 1: Share the Folder
Copy the `Excel_Insights_Windows` folder to USB drive or network share

### Option 2: Share the Archive
Send `Excel_Insights_Windows.tar.gz` via email/file sharing
- Windows users: Extract using 7-Zip or WinRAR
- Smaller file size for transfer

### Option 3: Cloud Distribution
Upload to Google Drive, Dropbox, OneDrive, etc.

## 🛠️ Customizing the Build

Edit `build_windows.py` to:
- Change package name
- Add/remove files
- Modify launcher scripts
- Customize README

## ⚠️ Limitations

### What's Included:
✅ All Python source code
✅ Templates and static files
✅ Embedded API key
✅ Auto-setup scripts

### What's NOT Included (must be pre-installed or installed on first run):
❌ Python runtime (must be pre-installed on Windows)
❌ Node.js runtime (must be pre-installed on Windows)
❌ Python dependencies (Flask, pandas, plotly, etc.) - installed by SETUP_FIRST_TIME.bat
❌ Claude Code CLI - installed by SETUP_FIRST_TIME.bat

This keeps the package small and portable while ensuring compatibility with different Windows environments.

## 🧪 Testing Before Distribution

Test the package on a clean Windows VM or PC:

1. Make sure Python 3.10+ is installed (with PATH)
2. Make sure Node.js 18+ is installed (with PATH)
3. Copy `Excel_Insights_Windows` folder to test PC
4. Double-click `SETUP_FIRST_TIME.bat`
5. Verify it checks Python/Node.js, installs Claude Code CLI, and creates venv
6. Double-click `START_HERE.bat`
7. Verify server starts without errors
8. Test uploading an Excel file and watch for "Control request timeout" error

## 📝 Troubleshooting

### Build fails: "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY_HERE"
python3 build_windows.py
```

### Package won't run on Windows: "Python not found"
Make sure Python is installed and in PATH:
```cmd
python --version
```

Should show: `Python 3.10.x` or higher

### Package won't run: "Node.js not found"
Make sure Node.js is installed and in PATH:
```cmd
node --version
```

Should show: `v18.0.0` or higher

### Analysis fails: "Control request timeout: initialize"
This means the Claude Agent SDK cannot connect to the Claude Code CLI.

**Solution:**
1. Make sure Node.js is installed: `node --version`
2. Install Claude Code CLI: `npm install -g @anthropics/claude-code`
3. Verify: `claude-code --version`
4. Delete `venv` folder and run `SETUP_FIRST_TIME.bat` again

### Dependencies fail to install on Windows
Delete `venv` folder and run `SETUP_FIRST_TIME.bat` again

## 🎉 Success!

Once built, you have a **portable, ready-to-use** Excel Insights Dashboard that works on any Windows PC with Python and Node.js installed!

---

**Built with ❤️ using Claude Sonnet 4.5**
