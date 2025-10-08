"""
Claude Agent SDK Service for Excel Analysis
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    create_sdk_mcp_server
)
from excel_mcp_tools import (
    analyze_excel,
    create_visualization,
    generate_insights,
    create_dashboard,
    correlation_analysis,
    detect_outliers,
    group_comparison,
    trend_analysis
)

# Verify API key is set
if not os.environ.get('ANTHROPIC_API_KEY'):
    raise RuntimeError(
        "ANTHROPIC_API_KEY environment variable not set. "
        "Please set it before importing agent_service."
    )


class ExcelAnalysisAgent:
    """Wrapper for Claude Agent SDK to analyze Excel files."""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create MCP server with ALL Excel analysis tools
        self.tools = [
            analyze_excel,
            create_visualization,
            generate_insights,
            create_dashboard,
            correlation_analysis,
            detect_outliers,
            group_comparison,
            trend_analysis
        ]

        self.mcp_server = create_sdk_mcp_server(
            name="excel_tools",
            version="1.0.0",
            tools=self.tools
        )

        print(f"DEBUG: MCP Server created with {len(self.tools)} tools")
        tool_names = []
        for t in self.tools:
            if hasattr(t, 'name'):
                tool_names.append(t.name)
            elif hasattr(t, '__name__'):
                tool_names.append(t.__name__)
            else:
                tool_names.append(str(t))
        print(f"DEBUG: Available tools: {tool_names}")

    def _parse_event_to_log(self, event) -> dict:
        """
        Extract displayable information from SDK event for activity log.

        Returns:
            dict with timestamp, type, content, icon, and optional full_content for expansion
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Handle different event types
        event_type = getattr(event, 'type', None)

        # Check for content blocks
        if hasattr(event, 'content'):
            content_items = event.content if isinstance(event.content, list) else [event.content]

            for item in content_items:
                item_class_name = type(item).__name__

                # THINKING BLOCK - Check by class name
                if item_class_name == 'ThinkingBlock' or (hasattr(item, 'type') and item.type == 'thinking'):
                    thinking_text = getattr(item, 'thinking', '') or getattr(item, 'text', '')
                    if thinking_text:
                        preview = thinking_text[:300] + '...' if len(thinking_text) > 300 else thinking_text
                        return {
                            'timestamp': timestamp,
                            'type': 'thinking',
                            'content': preview,
                            'full_content': thinking_text,
                            'icon': '🧠',
                            'expandable': len(thinking_text) > 300
                        }

                # TEXT BLOCK - Agent talking (check by class name first, then by attribute)
                elif item_class_name == 'TextBlock':
                    text_content = getattr(item, 'text', '')
                    if text_content and text_content.strip():
                        preview = text_content[:300] + '...' if len(text_content) > 300 else text_content
                        return {
                            'timestamp': timestamp,
                            'type': 'text',
                            'content': preview,
                            'full_content': text_content,
                            'icon': '💬',
                            'expandable': len(text_content) > 300
                        }

                # TOOL USE BLOCK - Check by class name
                elif item_class_name == 'ToolUseBlock':
                    tool_name = getattr(item, 'name', 'unknown_tool')
                    tool_input = getattr(item, 'input', {})

                    # Format tool call nicely based on tool type
                    if tool_name == 'Bash':
                        command = tool_input.get('command', '?')
                        preview = command[:150] + '...' if len(command) > 150 else command
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Running: {preview}",
                            'full_content': f"Running bash command:\n{command}",
                            'icon': '⚙️',
                            'expandable': len(command) > 150
                        }
                    elif tool_name == 'Edit':
                        file_path = tool_input.get('file_path', '?')
                        old_string = tool_input.get('old_string', '')[:100]
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Editing {file_path}",
                            'full_content': f"Editing file: {file_path}\nReplacing: {old_string}...",
                            'icon': '✏️',
                            'expandable': False
                        }
                    elif tool_name == 'Write':
                        file_path = tool_input.get('file_path', '?')
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Writing {file_path}",
                            'full_content': f"Writing file: {file_path}",
                            'icon': '📝',
                            'expandable': False
                        }
                    elif tool_name == 'Read':
                        file_path = tool_input.get('file_path', '?')
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Reading {file_path}",
                            'full_content': f"Reading file: {file_path}",
                            'icon': '📖',
                            'expandable': False
                        }
                    else:
                        input_str = json.dumps(tool_input, indent=2)
                        preview = input_str[:150] + '...' if len(input_str) > 150 else input_str
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"{tool_name}(...)",
                            'full_content': f"{tool_name}:\n{input_str}",
                            'icon': '🔧',
                            'expandable': len(input_str) > 150
                        }

                # TOOL RESULT BLOCK - Check by class name
                elif item_class_name == 'ToolResultBlock':
                    tool_id = getattr(item, 'tool_use_id', 'unknown')
                    result_content = getattr(item, 'content', '')
                    is_error = getattr(item, 'is_error', False)

                    # Extract useful info from result
                    if isinstance(result_content, str):
                        result_str = result_content
                    elif isinstance(result_content, list) and len(result_content) > 0:
                        first_item = result_content[0]
                        if hasattr(first_item, 'text'):
                            result_str = first_item.text
                        else:
                            result_str = str(result_content)
                    else:
                        result_str = str(result_content)

                    preview = result_str[:200] + '...' if len(result_str) > 200 else result_str

                    if is_error:
                        return {
                            'timestamp': timestamp,
                            'type': 'error',
                            'content': f"Error: {preview}",
                            'full_content': f"Error:\n{result_str}",
                            'icon': '❌',
                            'expandable': len(result_str) > 200
                        }
                    else:
                        return {
                            'timestamp': timestamp,
                            'type': 'result',
                            'content': f"✓ {preview}",
                            'full_content': result_str,
                            'icon': '✅',
                            'expandable': len(result_str) > 200
                        }

        # Error events
        if hasattr(event, 'error'):
            error_str = str(event.error)
            return {
                'timestamp': timestamp,
                'type': 'error',
                'content': error_str,
                'full_content': error_str,
                'icon': '❌',
                'expandable': False
            }

        # Skip events we don't recognize
        return None

    async def analyze_file(self, file_path: str, event_callback=None, additional_instructions=None,
                          refinement_prompt=None, original_run_id=None, language="hebrew") -> dict:
        """
        Analyze Excel file using Claude Agent SDK.

        Args:
            file_path: Path to uploaded Excel file
            event_callback: Optional callback function to receive real-time events
            additional_instructions: Optional user instructions for initial analysis
            refinement_prompt: Optional user feedback/refinement request
            original_run_id: Optional ID of original analysis (for refinement context)
            language: Output language (default: "hebrew"). Only changes if user explicitly requests

        Returns:
            dict with dashboard_path, insights, and execution log
        """
        # Check if user explicitly requested a different language
        language_override = False
        if additional_instructions:
            lower_instructions = additional_instructions.lower()
            if "english" in lower_instructions or "in english" in lower_instructions:
                language = "english"
                language_override = True
            elif "arabic" in lower_instructions or "בערבית" in lower_instructions:
                language = "arabic"
                language_override = True
            # Hebrew remains default unless explicitly changed
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # System prompt for the agent - COMPREHENSIVE ANALYSIS MODE
        # Adjust language requirements based on user preference
        if language_override and language == "english":
            language_instruction = """
🌐 LANGUAGE REQUIREMENT:
The user has explicitly requested ENGLISH output. Use English for all dashboard content."""
            html_dir = 'ltr'
            html_lang = 'en'
        elif language_override and language == "arabic":
            language_instruction = """
🌐 LANGUAGE REQUIREMENT - ARABIC:
The user has explicitly requested ARABIC output. Use Arabic for all dashboard content.
- Use RTL (Right-to-Left) direction for Arabic text in HTML"""
            html_dir = 'rtl'
            html_lang = 'ar'
        else:  # Default to Hebrew
            language_instruction = """
🌐 CRITICAL DEFAULT LANGUAGE - HEBREW (עברית):
⚠️ ALWAYS use HEBREW for ALL outputs - THIS IS THE DEFAULT!
- ALL dashboard text, titles, labels MUST be in Hebrew
- ALL insights and analysis MUST be in Hebrew
- ALL chart titles, axis labels, legends MUST be in Hebrew
- ALL HTML content MUST be in Hebrew
- Use RTL (Right-to-Left) direction
- IGNORE input file language - OUTPUT HEBREW
- This is the DEFAULT - do not use English unless explicitly requested!"""
            html_dir = 'rtl'
            html_lang = 'he'

        system_prompt = f"""You are a world-class data scientist and analyst with unlimited time and resources.
{language_instruction}

🎯 YOUR MISSION: Perform DEEP, EXHAUSTIVE analysis of the Excel file and create a stunning interactive dashboard.

✨ YOU HAVE COMPLETE FREEDOM:
- Use MCP tools (convenient for common tasks)
  * Excel analysis tools (analyze_excel, create_visualization, etc.)
- Write Python code (more flexible and powerful)
- Run bash commands
- Use ANY approach that produces the best results
- Combine methods as needed

📋 DELIVERABLES (REQUIRED) - ALL IN HEBREW:
1. **Single Self-Contained HTML Dashboard** saved as `dashboard.html` with:
   - 🇮🇱 HEBREW LANGUAGE for ALL text content
   - Add <html dir="rtl" lang="he"> for proper Hebrew display
   - 5-10+ interactive Plotly visualizations EMBEDDED INLINE (NOT as separate iframe files)
   - Use Plotly's to_html(include_plotlyjs='cdn', full_html=False, div_id='unique_id')
   - Chart titles in Hebrew (e.g., "התפלגות מכירות" not "Sales Distribution")
   - Axis labels in Hebrew (e.g., "חודש", "סכום", "כמות")
   - Embed each chart in a <div> element directly in the HTML
   - DO NOT create separate .html files for each visualization
   - DO NOT use iframes - embed all charts inline in ONE file
   - Statistical insights and key findings IN HEBREW
   - Professional styling with Hebrew fonts (e.g., font-family: 'Segoe UI', 'Arial Hebrew', sans-serif)
   - Executive summary IN HEBREW (e.g., "סיכום מנהלים")
   - Organized sections with Hebrew navigation (e.g., "ניתוח נתונים", "תובנות", "המלצות")

2. **Comprehensive Analysis** including:
   - Data structure and quality assessment
   - Descriptive statistics for all columns
   - Correlation analysis with heatmaps
   - Outlier detection
   - Trend analysis (if time series data)
   - Group comparisons (if categorical data)
   - Business insights and recommendations

📊 SUGGESTED WORKFLOW (ALL OUTPUT IN HEBREW):

1. **Explore the data** (חקירת הנתונים)
   - Use analyze_excel tool OR write pandas code to understand structure
   - Identify column types, missing values, distributions
   - REMEMBER: Your analysis output must be in HEBREW

2. **Generate insights** (יצירת תובנות)
   - Use generate_insights tool OR write statistical analysis code
   - Calculate means, medians, correlations, etc.
   - Write all insights in HEBREW (e.g., "הממוצע של המכירות הוא...")

3. **Create visualizations** (יצירת תרשימים)
   - Write Plotly code directly in Python
   - Set all titles and labels in HEBREW: fig.update_layout(title="כותרת בעברית", xaxis_title="ציר X", yaxis_title="ציר Y")
   - Create 5-10+ charts with Hebrew labels
   - Convert to inline HTML using: fig.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart1')
   - Store the HTML strings in variables, NOT separate files

4. **Build single-file dashboard IN HEBREW** (בניית דשבורד בעברית)
   - Create ONE complete HTML file with Hebrew content
   - Set HTML attributes: <html dir="rtl" lang="he">
   - Use Hebrew headings: <h1>ניתוח נתונים מקיף</h1>
   - Combine all chart HTML strings into Hebrew-labeled sections
   - Add CSS with Hebrew-friendly fonts
   - Write all text, insights, and commentary in HEBREW
   - CRITICAL: Everything must be in ONE dashboard.html file IN HEBREW

⏰ TIME: Take 3-5 minutes. Quality and depth over speed.
🔧 APPROACH: Whatever works best! Be creative and thorough.
💡 GOAL: Impress the user with deep insights and beautiful visualizations."""

        # Build user prompt based on whether this is a refinement or initial analysis
        if refinement_prompt and original_run_id:
            # Refinement mode - reference previous work
            original_dir = self.output_dir / original_run_id
            user_prompt = f"""ANALYSIS REFINEMENT REQUEST - HEBREW OUTPUT REQUIRED:

🇮🇱 חשוב: כל הפלט חייב להיות בעברית!
⚠️ LANGUAGE: ALL OUTPUT MUST BE IN HEBREW

📁 Excel File: {file_path}
📂 Output Directory: {run_dir}
🎯 Final Dashboard: {run_dir}/dashboard.html (בעברית!)
📋 Previous Analysis: {original_dir}

🔄 USER FEEDBACK:
{refinement_prompt}

🚀 YOUR TASK:
The user has reviewed your previous analysis and provided feedback above. Your job is to:

1. **Review the previous analysis** (if it exists in {original_dir})
   - Check what dashboards, charts, and insights were already created
   - Understand what was done well and what was missing

2. **Address the user's feedback**
   - Fix any errors they pointed out
   - Add any missing analysis they requested
   - Improve visualizations based on their suggestions
   - Focus on their specific requests

3. **Create an IMPROVED dashboard** at {run_dir}/dashboard.html
   - Include everything from before (if applicable)
   - Add the new analysis/visualizations requested
   - Make it better based on their feedback

✅ REQUIREMENTS - חובה בעברית:
- 🇮🇱 ALL TEXT IN HEBREW - כל הטקסט בעברית!
- Create ONE `dashboard.html` with <html dir="rtl" lang="he">
- 5-10+ Plotly visualizations with HEBREW titles/labels
- Use fig.update_layout(title="עברית", font=dict(family="Arial Hebrew"))
- Address ALL user feedback IN HEBREW
- Statistical insights IN HEBREW (תובנות בעברית)
- Professional RTL Hebrew styling
- CRITICAL: Everything in HEBREW regardless of input language!

💡 APPROACH:
- Use any tools or methods that work best
- MCP tools, Python code, or combination
- Be thorough and creative

⏰ TIME: Take 3-5 minutes to create an excellent refined analysis.
🎯 GOAL: Deliver exactly what the user asked for!

Begin your refinement now!"""
        else:
            # Initial analysis mode
            # Build base prompt with appropriate language emphasis
            if not language_override:  # Hebrew is default
                base_prompt = f"""DEEP ANALYSIS REQUEST - DEFAULT LANGUAGE: HEBREW:

🇮🇱 ברירת מחדל: עברית!
⚠️ DEFAULT OUTPUT LANGUAGE: HEBREW (עברית)
- זו ברירת המחדל - תמיד עברית אלא אם המשתמש ביקש אחרת
- Dashboard language: HEBREW
- ALL text, labels, insights: HEBREW
- Ignore input file language - USE HEBREW

📁 Excel File: {file_path}
📂 Output Directory: {run_dir}
🎯 Final Dashboard: {run_dir}/dashboard.html

🚀 YOUR TASK:
Analyze this Excel file and create dashboard IN HEBREW (ברירת המחדל)."""
            else:  # User explicitly requested different language
                lang_name = language.upper()
                base_prompt = f"""DEEP ANALYSIS REQUEST - USER REQUESTED {lang_name}:

📁 Excel File: {file_path}
📂 Output Directory: {run_dir}
🎯 Final Dashboard: {run_dir}/dashboard.html

🚀 YOUR TASK:
Analyze this Excel file and create dashboard in {lang_name} as requested."""

            # Add user's custom instructions if provided
            if additional_instructions:
                base_prompt += f"""

📝 USER'S SPECIFIC INSTRUCTIONS:
{additional_instructions}

Make sure to incorporate these specific instructions into your analysis!"""

            # Complete the prompt with requirements
            user_prompt = base_prompt + """

✅ REQUIREMENTS - כל הדרישות בעברית:
1. 🇮🇱 חובה: כל התוכן בעברית - כותרות, תוויות, טקסט, הכל!
2. Create ONE self-contained `dashboard.html` file with <html dir="rtl" lang="he">
3. Include 5-10+ Plotly visualizations with HEBREW titles and labels
4. Use fig.update_layout(title="כותרת עברית", font=dict(family="Arial Hebrew"))
5. Add statistical insights IN HEBREW (תובנות סטטיסטיות בעברית)
6. Professional Hebrew styling with RTL support
7. Hebrew sections: סקירה כללית, תרשימים, תובנות, המלצות
8. CRITICAL: Everything in HEBREW - ignore input file language!

💡 APPROACH OPTIONS:
- Use the MCP tools (analyze_excel, create_visualization, create_dashboard, etc.)
- OR write Python code with pandas, plotly, numpy, scipy
- OR combine both approaches
- OR any other method that works!

🎨 VISUALIZATION IDEAS:
- Distribution plots for numeric columns
- Bar charts for categorical comparisons
- Correlation heatmaps
- Time series trends (if dates exist)
- Box plots for outliers
- Scatter plots for relationships
- Pie charts for proportions
- Multi-panel dashboards

⏰ TIME: Take 3-5 minutes for deep, thorough analysis.
🎯 GOAL: Deliver an impressive dashboard that tells the data story!

Begin your analysis now!"""

        # Verify API key is in environment (SDK reads it automatically)
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not found in environment")

        print(f"DEBUG: API Key in environment: {api_key[:20]}... (length: {len(api_key)})")

        # Configure MCP servers
        # Note: Only using custom Excel tools for now
        # Playwright MCP requires different configuration approach
        mcp_servers = {
            "excel_tools": self.mcp_server
        }

        # Configure agent options - SDK will auto-detect API key from environment
        options = ClaudeAgentOptions(
            model="sonnet",
            system_prompt=system_prompt,
            mcp_servers=mcp_servers,
            permission_mode="bypassPermissions",  # Valid options: acceptEdits, bypassPermissions, default, plan
            cwd=str(run_dir),
            setting_sources=[],
            max_turns=100,
        )

        print(f"DEBUG: Agent configured:")
        print(f"  - Model: {options.model}")
        print(f"  - MCP servers: {list(options.mcp_servers.keys())}")
        print(f"  - Permission mode: {options.permission_mode}")
        print(f"  - Working directory: {options.cwd}")
        print(f"  - API key from env: ANTHROPIC_API_KEY={api_key[:15]}...")

        # Execute analysis
        events = []
        result_data = {}

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(user_prompt)

                # Collect events
                async for event in client.receive_response():
                    # DEBUG: Print event to see what we're getting
                    print(f"DEBUG: Received event type: {type(event)}, hasattr content: {hasattr(event, 'content')}")
                    if hasattr(event, 'content'):
                        print(f"DEBUG: Event content: {event.content}")

                    # Parse event to displayable log entry
                    log_entry = self._parse_event_to_log(event)
                    if log_entry:
                        print(f"DEBUG: Parsed log entry: {log_entry}")
                        if event_callback:
                            event_callback(log_entry)  # Stream to Flask in real-time
                    else:
                        print(f"DEBUG: No log entry parsed from event")

                    events.append(self._serialize_event(event))

                    # Extract tool results
                    if hasattr(event, 'content'):
                        for item in event.content if isinstance(event.content, list) else []:
                            if hasattr(item, 'result'):
                                result_data.update(item.result if isinstance(item.result, dict) else {})

        except TimeoutError as e:
            error_msg = (
                "Control request timeout - API key may be invalid or not set correctly. "
                f"Error: {str(e)}"
            )
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            print(f"ERROR: {error_msg}")
            raise

        # Find dashboard file
        dashboard_path = run_dir / "dashboard.html"
        if not dashboard_path.exists():
            # If agent didn't create dashboard, create a simple one
            dashboard_path = await self._create_fallback_dashboard(run_dir, result_data)

        return {
            "dashboard_path": str(dashboard_path),
            "insights": result_data.get("insights", {}),
            "events": events,
            "run_id": run_id
        }

    async def _create_fallback_dashboard(self, run_dir: Path, data: dict) -> Path:
        """Create a fallback dashboard if agent fails - IN HEBREW."""
        dashboard_path = run_dir / "dashboard.html"
        html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>ניתוח נתוני Excel</title>
    <style>
        body {{
            font-family: 'Segoe UI', 'Arial Hebrew', Arial, sans-serif;
            margin: 20px;
            direction: rtl;
            text-align: right;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>תוצאות ניתוח Excel</h1>
        <h2>נתונים שנותחו:</h2>
        <pre style="direction: ltr; text-align: left;">{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>
"""
        with open(dashboard_path, 'w') as f:
            f.write(html)
        return dashboard_path

    def _serialize_event(self, event):
        """Convert event to JSON-serializable dict."""
        if hasattr(event, "__dict__"):
            return {k: self._serialize_event(v) for k, v in event.__dict__.items() if not k.startswith("_")}
        elif isinstance(event, dict):
            return {k: self._serialize_event(v) for k, v in event.items()}
        elif isinstance(event, (list, tuple)):
            return [self._serialize_event(item) for item in event]
        else:
            return str(event) if not isinstance(event, (str, int, float, bool, type(None))) else event


# Synchronous wrapper for Flask
def analyze_excel_file(file_path: str, output_dir: str = "outputs", event_callback=None,
                       additional_instructions=None, refinement_prompt=None, original_run_id=None,
                       language="hebrew") -> dict:
    """Synchronous wrapper for Flask route. Default language is Hebrew."""
    agent = ExcelAnalysisAgent(output_dir)
    return asyncio.run(agent.analyze_file(
        file_path,
        event_callback=event_callback,
        additional_instructions=additional_instructions,
        refinement_prompt=refinement_prompt,
        original_run_id=original_run_id,
        language=language
    ))
