# 📊 Excel Insights Dashboard - AI Powered

**Deep, comprehensive Excel analysis using Claude Agent SDK (Sonnet 4.5) with real-time activity monitoring**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Sonnet 4.5](https://img.shields.io/badge/Claude-Sonnet%204.5-orange.svg)](https://www.anthropic.com/claude)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd Excel_Insights_CC_SDK_wsl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set API key
echo "ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE" > .env

# 3. Verify setup
python test_api_key.py        # Should show ✅
python test_sdk_connection.py # Should show ✅

# 4. Run!
python app.py

# 5. Open http://localhost:5000 and upload Excel file
```

---

## 🎯 What This Does

1. **Upload** an Excel file (.xlsx, .xls) via web interface
2. **💡 Customize Analysis** - Add optional custom instructions to guide the AI:
   - "Focus on monthly trends analysis"
   - "Compare performance between regions"
   - "Create pie charts and line graphs"
   - "Identify outliers and explain them"
3. **Claude Agent SDK** performs **DEEP, EXHAUSTIVE analysis** (3-5+ minutes)
4. **Full AI Freedom** - Agent uses MCP tools, Python code, bash commands, or any combination
5. **🤖 Real-Time Activity Monitor** - Watch the agent think and work:
   - 💭 See agent's reasoning and thoughts
   - 🔧 Monitor tool executions (MCP tools, Edit, Bash, Write, Read)
   - ✅ View tool results in real-time
   - 📊 Track progress with timestamps
6. **8 Advanced MCP Tools** for comprehensive analysis:
   - Data exploration & statistics
   - Correlation analysis with heatmaps
   - Outlier detection (IQR method)
   - Group comparisons
   - Trend analysis with moving averages
   - 5-10+ visualizations (bar, line, scatter, pie, heatmaps)
   - Professional dashboard generation
7. **🌐 Multi-Language Support** - Default Hebrew output, with English/Arabic on request
8. **🔄 Dashboard Refinement** - Request improvements and modifications after viewing results
9. **💬 Interactive Chat** - Chat directly with Claude about your Excel file and analysis
10. **No timeouts** - Agent works as long as needed
11. **Real-time progress tracking** with elapsed time

---

## ✨ Key Features

### 🤖 Real-Time Activity Monitor (NEW!)
Watch the AI agent work in real-time with a beautiful live activity log:
- **🧠 Thinking blocks** - See the agent's reasoning process (expandable)
- **💬 Agent talking** - Read agent's commentary and explanations
- **⚙️ Tool executions** - Track MCP tools, file edits, bash commands
- **📝 Code writing** - Watch Python scripts being created
- **✅ Results** - View tool outputs and data (expandable if long)
- **⏰ Timestamps** - Know exactly when each action occurred
- **🎨 Color-coded** - Different colors for different event types
- **📖 Expandable** - Click `[expand]` to see full content of long entries

### 💬 Interactive Chat with Claude (NEW!)
Chat directly with Claude about your Excel file and analysis:
- **Ask Questions**: Get instant answers about your data
- **Explore Insights**: Dive deeper into analysis findings
- **Context-Aware**: Claude knows both the raw data and dashboard analysis
- **15 Message Limit**: Have extended conversations about your file
- **Reset Anytime**: Start fresh conversations whenever needed
- **Persistent Context**: Data remains accessible even after page refresh
- **Bilingual**: Responds in Hebrew or English based on your question
- **Examples**:
  - "מה הממצאים העיקריים?" (What are the main findings?)
  - "Can you explain the correlation you found?"
  - "What should I focus on based on this analysis?"
  - "Show me the top 5 products by revenue"

### 💡 Custom Instructions
Guide the AI agent with your specific analysis needs:
- **Initial Upload**: Add custom instructions when uploading your Excel file
- **Targeted Analysis**: Request specific chart types, comparisons, or insights
- **Language Control**: Request output in English or Arabic (default: Hebrew)
- **Dashboard Refinement**: Request improvements after viewing initial results
- **Examples**:
  - "Focus on analyzing quarterly sales trends"
  - "Compare performance between North and South regions"
  - "Identify outliers and provide explanations"
  - "Create scatter plots showing correlations"
  - "Analyze in English" for English output

### 🚀 Full AI Freedom
The agent is **not restricted** to specific tools or methods:
- Can write custom Python analysis code
- Can use bash commands
- Can combine MCP tools with custom scripts
- Chooses the best approach for each dataset
- **Adapts to your custom instructions** while maintaining quality standards

### 📊 Comprehensive Analysis
- 5-10+ interactive Plotly visualizations
- Statistical analysis (mean, median, correlations, outliers)
- Correlation heatmaps
- Trend detection and time series analysis
- Group comparisons and segmentation
- Professional HTML dashboard output

### 🔐 User Management & Authentication
- **Guest Mode**: Analyze files without registration (session-based)
- **User Accounts**: Register for persistent analysis history
- **Admin Panel**: User management and system monitoring
- **Email Notifications**: Get notified when analysis completes (SendGrid integration)
- **Analysis History**: Review past analyses (registered users only)
- **Role-Based Access**: Admin vs regular user permissions

### ⚡ Production Ready
- Background processing (no request timeouts)
- Auto-reload disabled (prevents crashes during file operations)
- Error handling and fallback dashboards
- API key validation on startup
- Test scripts for verification
- Database persistence (SQLite) for users and analysis history
- Session management and authentication

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interface                            │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────┐ │
│  │  Login/  │  │ File Upload  │  │ Dashboard  │  │  History   │ │
│  │ Register │  │ + Custom     │  │  Viewer    │  │   Panel    │ │
│  │  /Guest  │  │ Instructions │  │ + Refine   │  │            │ │
│  └──────────┘  └──────────────┘  └────────────┘  └────────────┘ │
└─────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Application                           │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────┐│
│  │   Auth      │  │  Database   │  │  Background Processing   ││
│  │  System     │  │   (SQLite)  │  │  (Threading, No Timeout) ││
│  │ ─────────── │  │ ─────────── │  │ ──────────────────────── ││
│  │ • Users     │  │ • Users     │  │ • Job Tracking           ││
│  │ • Sessions  │  │ • Analyses  │  │ • Event Streaming        ││
│  │ • Roles     │  │ • Logs      │  │ • State Persistence      ││
│  └─────────────┘  └─────────────┘  └──────────────────────────┘│
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Claude Agent SDK (Sonnet 4.5)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  System Prompt: Deep Analysis + Language Config (Hebrew)   │ │
│  │  User Prompt: File Path + Custom Instructions (optional)   │ │
│  │  Or: Refinement Request + Previous Analysis Context        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Agent Tool Access (Full Freedom)               │ │
│  │  ┌──────────────┐  ┌──────────┐  ┌────────┐  ┌─────────┐  │ │
│  │  │  MCP Tools   │  │  Python  │  │  Bash  │  │  File   │  │ │
│  │  │  ──────────  │  │  Code    │  │  Cmds  │  │  Ops    │  │ │
│  │  │ • analyze_   │  │ • pandas │  │        │  │ • Write │  │ │
│  │  │   excel      │  │ • plotly │  │        │  │ • Edit  │  │ │
│  │  │ • visualize  │  │ • scipy  │  │        │  │ • Read  │  │ │
│  │  │ • insights   │  │ • numpy  │  │        │  │         │  │ │
│  │  └──────────────┘  └──────────┘  └────────┘  └─────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Output Generation                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Hebrew Dashboard (RTL) with:                               │ │
│  │  • 5-10+ Interactive Plotly Charts (embedded inline)        │ │
│  │  • Statistical Insights & Recommendations                   │ │
│  │  • Professional CSS Styling                                 │ │
│  │  • Customized based on user instructions                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                Optional: Email Notification                      │
│  SendGrid → User Email: "Your analysis is ready! [View]"        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

- **Python 3.10+** (Ubuntu/WSL)
- **Node.js 18+** (for Claude Code CLI)
- **Anthropic API Key** ([Get it here](https://console.anthropic.com/))

---

## 🚀 Setup Instructions

### 1. Install Claude Agent SDK

First, create a virtual environment and install the SDK:

```bash
cd /home/adminuser/projects/Excel_Insights_CC_SDK_wsl

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

**IMPORTANT:** The API key must be set for the SDK to work.

**Option 1: Use .env file (Recommended)**
```bash
# Create .env file
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY
```

Your `.env` file should contain:
```
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE

# Optional: Email notifications via SendGrid
SENDGRID_API_KEY=SG.YOUR_SENDGRID_API_KEY_HERE
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
APP_BASE_URL=http://localhost:5000
```

**Note**: Email notifications are optional. If SendGrid is not configured, the app will work fine but users won't receive email notifications when analysis completes.

**Option 2: Export it directly (Temporary)**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_ACTUAL_KEY_HERE"
```

**Verify API key is set:**
```bash
python test_api_key.py
```

You should see: ✅ ANTHROPIC_API_KEY is set!

### 3. Install Claude Code CLI (if not already installed)

The Claude Agent SDK requires the Claude Code CLI:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify installation:

```bash
claude --version
```

### 4. Run the Flask App

```bash
# Make sure venv is activated
source venv/bin/activate

# Run Flask app
python app.py
```

The app will start at: **http://localhost:5000**

---

## 📖 How to Use

### Step 1: Access Web Interface
- Open browser: `http://localhost:5000`
- You'll see the upload page

### Step 2: Upload Excel File
- Click or drag-drop your `.xlsx` or `.xls` file
- The upload form will expand to show additional options

### Step 3: Add Custom Instructions (Optional)
- **💡 Additional Instructions** section appears after selecting a file
- Enter specific requests to guide the AI analysis:
  - "Focus on analyzing monthly trends"
  - "Compare performance between different regions"
  - "Identify outliers and explain them"
  - "Create pie charts and line graphs"
  - "Analyze growth rates"
- Leave blank for standard comprehensive analysis
- **Language Selection**: By default, dashboards are in Hebrew. To request a different language:
  - Add "in English" or "in Arabic" to your instructions
  - Example: "Focus on sales trends in English"

### Step 4: Configure Email Notifications (Registered Users)
- If you have an email configured, choose whether to receive completion notifications
- Guest users skip this step

### Step 5: Start Analysis
- Click **"Analyze with AI"** button
- Analysis begins immediately

### Step 6: Watch the Agent Work (3-5 minutes)
- **🤖 Activity Monitor** appears showing real-time agent activity:
  - 💭 **Thinking** - Agent's reasoning process
  - ✏️ **Editing** - Code modifications
  - ⚙️ **Running** - Bash commands and scripts
  - 📝 **Writing** - File creation
  - 🔧 **Tool Use** - MCP tool calls
  - ✅ **Results** - Tool outputs and data
- **Progress tracker** shows elapsed time
- Claude Agent SDK performs **comprehensive analysis**:
  - Explores ALL data relationships
  - Creates correlation matrix & heatmap
  - Detects outliers in every numeric column
  - Compares groups and segments
  - Analyzes trends over time
  - Generates 5-10+ visualizations
  - Builds professional dashboard
- **No timeouts** - agent works until complete

### Step 7: View Dashboard
- Automatically redirected to interactive dashboard
- See charts, insights, and statistics
- Professional HTML output with embedded Plotly visualizations
- Dashboard includes all requested analyses from your custom instructions

### Step 8: Chat with Claude About Your Data (NEW!)
- Click the **"💬 Chat with Claude about the file"** button (bottom-left)
- Interactive chat panel opens with your Excel file loaded
- Ask questions about your data in Hebrew or English:
  - "מה הנתונים בקובץ הזה?" (What's in this file?)
  - "What are the main insights?"
  - "Can you explain the trends you found?"
  - "Show me the top performers"
- Claude has access to:
  - ✅ Your full Excel data (converted to CSV format)
  - ✅ The dashboard analysis that was already performed
  - ✅ Complete conversation history (up to 15 messages)
- Features:
  - **Reset button** (🔄) - Start a fresh conversation
  - **Message counter** - See how many questions you have left
  - **Persistent context** - Data stays accessible even after page refresh
- The chat remembers everything from the conversation
- Use it to explore your data interactively!

### Step 9: Refine Your Analysis (Optional)
- Use the **"Refine your analysis"** panel at the bottom of the dashboard page
- Request improvements, additional visualizations, or corrections:
  - "Add a comparison between region A and region B"
  - "The correlation matrix is missing - please add it"
  - "Analyze trends for the last 6 months only"
  - "Add box plots to show outliers in sales data"
- Click **"Refine Analysis"** button
- The AI agent will create an improved version incorporating your feedback
- You can toggle the refinement panel on/off with the floating button

---

## 🛠️ Project Structure

```
Excel_Insights_CC_SDK_wsl/
├── app.py                      # Flask web application with authentication
├── agent_service.py            # Claude Agent SDK integration (Hebrew-first, multi-language)
├── chat_service.py             # Interactive chat with Claude about Excel files
├── excel_mcp_tools.py          # Custom MCP tools for Excel analysis
├── database.py                 # SQLite database models (User, Analysis, ActivityLog)
├── auth.py                     # Authentication and authorization decorators
├── email_service.py            # SendGrid email notification integration
├── requirements.txt            # Python dependencies
├── .env                        # API key configuration (create this!)
├── .env.example                # Example .env template
├── test_api_key.py            # Test script to verify API key is set
├── test_sdk_connection.py     # Test script to verify SDK connection
├── users.xml                   # User configuration file
├── templates/
│   ├── index.html             # Upload page with custom instructions & activity monitor
│   ├── login.html             # User login page
│   ├── dashboard_wrapper.html # Dashboard view with refinement panel
│   ├── history.html           # Analysis history for registered users
│   └── admin_panel.html       # Admin user management panel
├── static/                     # Static assets (CSS, JS)
├── uploads/                    # Uploaded Excel files (auto-created)
├── outputs/                    # Generated dashboards by run_id (auto-created)
│   └── 20251003_123456/
│       ├── dashboard.html     # Final interactive dashboard (Hebrew by default)
│       ├── chart1.html        # Individual Plotly charts
│       ├── chart2.html
│       └── *.py               # Python scripts created by agent
├── migrations/                 # Database migration scripts
├── job_states/                 # Persistent job state for session restoration
└── README.md                   # This file
```

---

## 🔧 8 Advanced MCP Tools Explained

### 1. **analyze_excel** - Core Data Analysis
- Loads Excel file using pandas
- Returns: row count, columns, data types, missing values, statistics, sample data

### 2. **create_visualization** - Standard Charts
- Creates Plotly charts (bar, line, scatter, pie)
- Saves as interactive HTML
- Agent creates 5-10+ visualizations per analysis

### 3. **generate_insights** - Statistical Insights
- Analyzes numeric columns: mean, median, std, min, max
- Analyzes categorical columns: unique values, top values
- Returns: structured insights

### 4. **correlation_analysis** - Relationship Discovery
- Calculates correlation matrix for all numeric columns
- Creates interactive heatmap visualization
- Identifies strong correlations (|r| > 0.5)
- Returns: correlation matrix + strong correlations list

### 5. **detect_outliers** - Anomaly Detection
- Uses IQR (Interquartile Range) method
- Detects outliers in numeric columns
- Returns: outlier count, bounds, outlier values

### 6. **group_comparison** - Segment Analysis
- Compares statistics across groups
- Creates grouped bar charts (mean, median)
- Returns: group statistics

### 7. **trend_analysis** - Time Series Insights
- Analyzes trends over time
- Calculates moving averages
- Detects trend direction (increasing/decreasing)
- Creates trend visualization

### 8. **create_dashboard** - Professional Output
- Combines ALL charts and insights
- Generates responsive HTML dashboard
- Organized by themes/categories

---

## 🤖 How the Agent Works (FULL FREEDOM MODE)

The Claude Agent SDK runs with **COMPLETE FREEDOM**:

### Agent Capabilities:
✅ **Use MCP Tools** - Convenient pre-built analysis functions
✅ **Write Python Code** - Create custom analysis scripts with pandas, plotly, scipy
✅ **Run Bash Commands** - Execute system commands
✅ **Edit Files** - Modify code and configurations
✅ **Combine Approaches** - Mix tools, code, and commands for best results

The agent **chooses the most effective approach** for each task!

### System Prompt (Deep Analysis Mode):
```
🎯 YOUR MISSION: Create stunning interactive HTML dashboard with deep insights

✨ YOU HAVE COMPLETE FREEDOM:
- Use MCP tools (convenient for common tasks)
- Write Python code (more flexible and powerful)
- Run bash commands
- Use ANY approach that produces the best results

📋 DELIVERABLES:
- 5-10+ interactive Plotly visualizations
- Statistical insights and findings
- Professional HTML dashboard
- Executive summary

⏰ TIME: 3-5 minutes for quality analysis
🎯 GOAL: Impress with deep insights and beautiful visualizations
```

### Execution Flow:
1. **Receives prompt**: "DEEP ANALYSIS REQUEST - Take your time"
2. **Full tool access**: MCP tools + Edit + Bash + Write + Read
3. **Max 100 turns**: Allows extensive analysis
4. **No timeouts**: Background threading in Flask (auto-reloader disabled)
5. **Real-time activity streaming**: Events sent to frontend every 2 seconds
6. **Autonomous reasoning**: Agent decides optimal approach

### Typical Execution Pattern:
```
💭 Thinking: "I'll analyze this data comprehensively..."
📝 Writing: comprehensive_analysis.py (pandas + plotly code)
⚙️ Running: python comprehensive_analysis.py
💭 Thinking: "Great! Now I'll create visualizations..."
🔧 Tool: create_visualization(type="bar", ...)
🔧 Tool: create_visualization(type="scatter", ...)
📝 Writing: dashboard.html (combining all charts)
✅ Complete!
```

---

## 📊 Example Flow

### Standard Analysis (No Custom Instructions)
```
User uploads: sales_data.xlsx
           ↓
Claude Agent SDK performs comprehensive analysis:
  1. analyze_excel("sales_data.xlsx")
     → Returns: 1000 rows, columns [Date, Product, Sales, Region]

  2. generate_insights("sales_data.xlsx")
     → Returns: Sales mean=$5,234, top Product=Widget A

  3. create_visualization(type="bar", x="Product", y="Sales")
     → Creates: outputs/20251003_123456/chart1.html

  4. create_visualization(type="line", x="Date", y="Sales")
     → Creates: outputs/20251003_123456/chart2.html

  5. create_dashboard(charts=[...], insights={...})
     → Creates: outputs/20251003_123456/dashboard.html
           ↓
Flask returns: http://localhost:5000/dashboard/20251003_123456
```

### Custom Instructions Analysis
```
User uploads: sales_data.xlsx
Custom instructions: "Focus on regional comparisons and monthly trends.
                      Create pie charts showing market share by region."
           ↓
Claude Agent SDK receives:
  📝 USER'S SPECIFIC INSTRUCTIONS:
  Focus on regional comparisons and monthly trends.
  Create pie charts showing market share by region.
           ↓
Agent tailors analysis to user's requests:
  1. Analyzes regional sales distribution
  2. Creates regional comparison bar charts
  3. Generates pie charts for market share
  4. Analyzes monthly trends over time
  5. Builds dashboard with focus on regional insights
           ↓
Dashboard with customized analysis: http://localhost:5000/dashboard/20251003_123456
```

### Dashboard Refinement Flow
```
User views dashboard → Requests refinement:
"Add a correlation heatmap between Sales and Revenue"
           ↓
Claude Agent SDK receives refinement request:
  🔄 USER FEEDBACK:
  Add a correlation heatmap between Sales and Revenue
           ↓
Agent creates improved version:
  1. Reviews previous analysis
  2. Adds correlation analysis
  3. Creates heatmap visualization
  4. Integrates into new dashboard
           ↓
New dashboard: http://localhost:5000/dashboard/20251003_145623
```

---

## 🔍 Troubleshooting

### Error: "No module named 'claude_agent_sdk'"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "ANTHROPIC_API_KEY not set" or "Control request timeout: initialize"
**This is the most common error!** The SDK can't find your API key.

**Solution:**
```bash
# 1. Test if API key is set
python test_api_key.py

# 2. If NOT set, create .env file:
echo "ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE" > .env

# 3. Or export it:
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY_HERE"

# 4. Verify again:
python test_api_key.py
# Should show: ✅ ANTHROPIC_API_KEY is set!

# 5. Test SDK connection:
python test_sdk_connection.py
# Should show: ✅ SUCCESS! SDK is working correctly.
```

**Important:** The API key must be in the environment when you run `python app.py`

### Error: "Claude CLI not found"
```bash
# Install Claude Code CLI (required by SDK)
npm install -g @anthropic-ai/claude-code

# Verify:
claude --version
```

### Error: "Permission mode 'acceptAll' is invalid"
This was fixed in the code. Valid modes are:
- `bypassPermissions` (used by default - full freedom)
- `acceptEdits` (accept file edits)
- `default` (default behavior)
- `plan` (plan mode)

### Error: "Error: write EPIPE" or Flask keeps restarting
**Fixed!** Flask auto-reloader is now disabled (`use_reloader=False`). This prevents Flask from restarting when the agent creates/edits files.

### Dashboard not generating
- Check `outputs/<run_id>/` for Python scripts and error logs
- Look at Flask terminal for error messages
- Ensure Excel file is valid (not corrupted)
- Check API key has credits at https://console.anthropic.com/
- Verify uploads/ directory is writable

### Activity Monitor not showing events
- Open browser console (F12) and check for JavaScript errors
- Verify Flask is running without auto-reloader
- Check that events are being received in `/status/<run_id>` response

---

## 💰 Cost Estimation

- **Per analysis**: ~$0.20 - $0.50 (deep analysis mode, 3-5 minutes)
- **Model**: Claude Sonnet 4.5
- **Many tool calls**: 10-20+ tool uses per analysis
- **Caching**: Reduces cost on repeated runs
- **Worth it**: Comprehensive insights vs basic analysis

---

## 🚀 Enhancement Ideas

Want to extend the capabilities? Here are some ideas:

### Additional Analysis Features:
1. **Statistical tests** - Add t-tests, ANOVA, chi-square tests
2. **Machine learning** - Clustering, regression, predictions
3. **Advanced visualizations** - 3D plots, animated charts, Sankey diagrams
4. **Data quality reports** - Detailed data profiling and quality scores
5. **Comparative analysis** - Compare multiple Excel files

### Export & Sharing:
1. **PDF export** - Convert dashboard to PDF reports
2. **PowerPoint export** - Auto-generate presentation slides
3. **Email integration** - Send reports via email
4. **Scheduled analysis** - Cron jobs for recurring analysis
5. **API endpoints** - REST API for programmatic access

### Performance Improvements:
1. **Caching** - Cache analysis results for faster re-runs
2. **Parallel processing** - Analyze multiple files simultaneously
3. **Incremental analysis** - Only analyze changed data
4. **Database storage** - Store results in PostgreSQL/MongoDB

### Example: Adding a Custom MCP Tool
```python
# In excel_mcp_tools.py
@tool(
    name="statistical_tests",
    description="Perform statistical hypothesis tests on data"
)
async def statistical_tests(args: Dict[str, Any]):
    from scipy import stats
    df = pd.read_excel(args["file_path"])

    # Perform t-test, ANOVA, etc.
    results = {
        "t_test": stats.ttest_ind(...),
        "anova": stats.f_oneway(...)
    }

    return {"content": [...], "result": results}
```

---

## 📝 API Endpoints

### Public Routes
- `GET /` - Main upload page (requires authentication or creates guest session)
- `GET /login` - User login page
- `GET /register` - User registration page (if enabled)
- `POST /login` - Process login credentials
- `POST /register` - Create new user account
- `POST /guest-login` - Create guest session for anonymous access
- `GET /logout` - Log out and clear session

### Authenticated Routes
- `POST /upload` - Upload and analyze Excel file (accepts `file` and optional `additional_instructions`)
- `GET /dashboard/<run_id>` - View generated dashboard with refinement panel
- `GET /dashboard-content/<run_id>` - Dashboard iframe content
- `GET /status/<run_id>` - Check analysis status and get real-time events
- `POST /refine/<run_id>` - Submit refinement request for existing analysis
- `GET /my-history` - View analysis history (registered users only)

### Admin Routes
- `GET /admin` - Admin panel for user management
- `POST /admin/user/<user_id>/update-role` - Update user role
- `POST /admin/user/<user_id>/toggle-status` - Enable/disable user account
- `POST /admin/user/<user_id>/delete` - Delete user account

### API Routes
- `GET /api/active-jobs` - Get active analysis jobs for current user (session restoration)

### Chat Routes
- `POST /chat/<run_id>/init` - Initialize chat session with Excel file
- `GET /chat/<run_id>` - Get chat session info and conversation history
- `POST /chat/<run_id>/message` - Send message to Claude about the file
- `POST /chat/<run_id>/clear` - Reset conversation (clear history)

---

## 🧪 Testing

Create a test Excel file:

```python
import pandas as pd

# Create sample data
data = {
    'Date': pd.date_range('2024-01-01', periods=100),
    'Product': ['Widget A', 'Widget B', 'Widget C'] * 33 + ['Widget A'],
    'Sales': [100 + i*10 for i in range(100)],
    'Region': ['North', 'South', 'East', 'West'] * 25
}

df = pd.DataFrame(data)
df.to_excel('test_data.xlsx', index=False)
```

Then upload to the dashboard!

---

## 📄 License

MIT License - Feel free to modify and extend!

---

## 🆘 Support & Resources

### Documentation
- **Claude Agent SDK**: https://docs.claude.com/en/api/agent-sdk/overview
- **Python SDK Reference**: https://docs.claude.com/en/api/agent-sdk/python
- **MCP Protocol**: https://modelcontextprotocol.io/

### Debugging
- Check Flask terminal for detailed logs
- Look in `outputs/<run_id>/` for generated files and error logs
- Use browser console (F12) to see frontend JavaScript logs
- Run test scripts: `test_api_key.py` and `test_sdk_connection.py`

### Common Issues
- **API Key**: https://console.anthropic.com/ (check credits and validity)
- **Permission errors**: Make sure `uploads/` and `outputs/` directories are writable
- **Browser issues**: Try hard refresh (Ctrl+Shift+R) or different browser

### Contributing
Have improvements or bug fixes? Contributions welcome!

---

## 📸 Example Activity Monitor Output

```
🚀 [02:56:11] Analysis started - initializing Claude Agent SDK...
💭 [02:56:15] I'll perform a comprehensive analysis of this Excel data...
🔧 [02:56:17] analyze_excel(file_path="uploads/sales_data.xlsx")
✅ [02:56:18] Result: 1000 rows, 5 columns [Date, Product, Sales, Region, Revenue]
💭 [02:56:20] I notice potential correlations between Sales and Revenue...
🔧 [02:56:22] correlation_analysis(file_path="uploads/sales_data.xlsx", ...)
✅ [02:56:24] Result: Found 3 strong correlations (|r| > 0.7)
📝 [02:56:26] Writing comprehensive_analysis.py
⚙️ [02:56:28] Running: python comprehensive_analysis.py
✅ [02:56:35] Result: Created 8 visualizations successfully
📝 [02:56:37] Writing dashboard.html
✅ [02:56:39] Analysis complete! Dashboard ready.
```

---

---

## 🆕 Recent Updates

### Version 2.1 - Interactive Chat Feature
- **💬 Chat with Claude**: Interactive Q&A about your Excel file and analysis
  - Chat directly with Claude Sonnet 4.5 about your data
  - 15 message conversation limit with reset functionality
  - Context-aware: knows both raw data and dashboard analysis
  - Persistent across page refreshes
  - Database-backed for access from history
  - Bilingual support (Hebrew/English auto-detected)
- **🔄 Smart Context Management**: Excel data sent as CSV text for compatibility
- **🎨 Beautiful Chat UI**: Typing indicators, message bubbles, reset button
- **📊 Analysis-Aware Conversations**: Claude references previous insights

### Version 2.0 - Feature-Complete Release
- **💡 Custom Instructions**: Guide AI analysis with your specific requirements at upload time
- **🔄 Dashboard Refinement**: Request improvements and modifications after viewing results
- **🔐 Authentication System**: Guest mode, user accounts, admin panel, role-based access
- **🌐 Multi-Language Support**: Default Hebrew (RTL), with English/Arabic on request
- **📧 Email Notifications**: SendGrid integration for completion alerts (optional)
- **📊 Analysis History**: Review past analyses for registered users
- **🎨 Improved UX**: Collapsible refinement panel, simplified progress indicators
- **💾 Session Persistence**: Resume active jobs after page refresh
- **🗄️ Database Backend**: SQLite for user management and activity tracking

---

**Built with ❤️ using Claude Sonnet 4.5 and Claude Agent SDK**

**Star ⭐ this repo if you find it useful!**
