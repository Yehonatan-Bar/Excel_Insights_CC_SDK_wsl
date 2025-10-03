# 📊 Excel Insights Dashboard - AI Powered (UNLIMITED MODE)

**Deep, comprehensive Excel analysis using Claude Agent SDK (Sonnet 4.5) with NO TIME LIMITS**

---

## 🎯 What This Does

1. **Upload** an Excel file (.xlsx, .xls) via web interface
2. **Claude Agent SDK** performs **DEEP, EXHAUSTIVE analysis** (3-5+ minutes)
3. **AI reasoning** with **unlimited tools and capabilities**
4. **8 Advanced MCP Tools** for comprehensive analysis:
   - Data exploration & statistics
   - Correlation analysis with heatmaps
   - Outlier detection (IQR method)
   - Group comparisons
   - Trend analysis with moving averages
   - 5-10+ visualizations (bar, line, scatter, pie, heatmaps)
   - Professional dashboard generation
5. **No timeouts** - Agent works as long as needed
6. **Real-time progress tracking** with elapsed time

---

## 🏗️ Architecture

```
User Upload → Flask App → Claude Agent SDK → MCP Tools → Dashboard
                                ↓
                    ┌───────────────────────┐
                    │   Custom MCP Tools    │
                    ├───────────────────────┤
                    │ • analyze_excel       │
                    │ • create_visualization│
                    │ • generate_insights   │
                    │ • create_dashboard    │
                    └───────────────────────┘
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

Create `.env` file with your Anthropic API key:

```bash
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY
```

**Or export it directly:**

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

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
- Click **"Analyze with AI"**

### Step 3: Wait for Deep Analysis (3-5 minutes)
- **Real-time progress tracking** shows elapsed time
- Claude Agent SDK performs **comprehensive analysis**:
  - Explores ALL data relationships
  - Creates correlation matrix & heatmap
  - Detects outliers in every numeric column
  - Compares groups and segments
  - Analyzes trends over time
  - Generates 5-10+ visualizations
  - Builds professional dashboard
- **No timeouts** - agent works until complete

### Step 4: View Dashboard
- Automatically redirected to interactive dashboard
- See charts, insights, and statistics

---

## 🛠️ Project Structure

```
Excel_Insights_CC_SDK_wsl/
├── app.py                  # Flask web application
├── agent_service.py        # Claude Agent SDK integration
├── excel_mcp_tools.py      # Custom MCP tools for Excel analysis
├── requirements.txt        # Python dependencies
├── .env                    # API key configuration
├── templates/
│   └── index.html         # Upload page UI
├── uploads/               # Uploaded Excel files
├── outputs/               # Generated dashboards (by run_id)
│   └── 20251003_123456/
│       ├── dashboard.html
│       ├── chart1.html
│       └── chart2.html
└── README.md              # This file
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

## 🤖 How the Agent Works (UNLIMITED MODE)

The Claude Agent SDK runs with **NO RESTRICTIONS**:

### System Prompt (Deep Analysis Mode):
```
🎯 YOUR MISSION: Perform DEEP, EXHAUSTIVE analysis. Take 3-5 minutes.

📊 COMPREHENSIVE WORKFLOW:
1. DEEP DATA EXPLORATION - Understand ALL columns and relationships
2. ADVANCED STATISTICAL INSIGHTS - Correlations, patterns, anomalies
3. COMPREHENSIVE VISUALIZATIONS - Create 5-10+ charts from different angles
4. MULTI-LAYERED INSIGHTS - Business, statistical, predictive insights
5. PROFESSIONAL DASHBOARD - Combine ALL into stunning output

⏰ TIME: 3-5 minutes EXPECTED
🔧 TOOLS: ALL tools available - use extensively!
💡 CREATIVITY: This is your masterpiece.
```

### Execution Flow:
1. **Receives prompt**: "DEEP ANALYSIS REQUEST - Take your time (3-5 min)"
2. **Unlimited tool access**: Agent can use ANY available tool
3. **Max 100 turns**: Allows extensive analysis
4. **No timeouts**: Background threading in Flask
5. **Real-time progress**: Status polling every 2 seconds
6. **Autonomous reasoning**: Agent decides which tools to use and when

### Typical Tool Usage Pattern:
```
analyze_excel → generate_insights → correlation_analysis →
detect_outliers (for each numeric column) →
create_visualization × 5-10 (different perspectives) →
group_comparison (if categorical data exists) →
trend_analysis (if time series exists) →
create_dashboard (combine everything)
```

---

## 📊 Example Flow

```
User uploads: sales_data.xlsx
           ↓
Claude Agent SDK:
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

---

## 🔍 Troubleshooting

### Error: "No module named 'claude_agent_sdk'"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "ANTHROPIC_API_KEY not set"
```bash
# Export API key
export ANTHROPIC_API_KEY="sk-ant-..."
# Or add to .env file
```

### Error: "Claude CLI not found"
```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code
```

### Dashboard not generating
- Check `outputs/<run_id>/` for error logs
- Ensure Excel file is valid (not corrupted)
- Check API key has credits

---

## 💰 Cost Estimation

- **Per analysis**: ~$0.20 - $0.50 (deep analysis mode, 3-5 minutes)
- **Model**: Claude Sonnet 4.5
- **Many tool calls**: 10-20+ tool uses per analysis
- **Caching**: Reduces cost on repeated runs
- **Worth it**: Comprehensive insights vs basic analysis

---

## 🚀 Next Steps

### Extend with More Tools:
1. **Statistical tests** (t-test, ANOVA)
2. **Machine learning** (clustering, regression)
3. **Export to PDF/PowerPoint**
4. **Email reports**
5. **Real-time streaming** updates

### Example: Add Correlation Analysis
```python
@tool("correlation_analysis", ...)
async def correlation_analysis(args: Dict[str, Any]):
    df = pd.read_excel(args["file_path"])
    corr = df.corr()
    # Create heatmap...
    return {"content": [...], "result": {...}}
```

---

## 📝 API Endpoints

- `GET /` - Upload page
- `POST /upload` - Upload and analyze Excel file
- `GET /dashboard/<run_id>` - View generated dashboard
- `GET /status/<run_id>` - Check analysis status

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

## 🆘 Support

- **Claude Agent SDK Docs**: [Coming soon]
- **Issues**: Check Flask logs and `outputs/<run_id>/` for errors
- **API Key Issues**: https://console.anthropic.com/

---

**Built with ❤️ using Claude Sonnet 4.5 and Claude Agent SDK**
