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
            dict with timestamp, type, content, icon for UI display
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Handle different event types
        event_type = getattr(event, 'type', None)

        # Check for content blocks
        if hasattr(event, 'content'):
            content_items = event.content if isinstance(event.content, list) else [event.content]

            for item in content_items:
                # Thinking block
                if hasattr(item, 'type') and item.type == 'thinking':
                    thinking_text = getattr(item, 'thinking', '') or getattr(item, 'text', '')
                    if thinking_text:
                        # Truncate long thinking blocks
                        preview = thinking_text[:200] + '...' if len(thinking_text) > 200 else thinking_text
                        return {
                            'timestamp': timestamp,
                            'type': 'thinking',
                            'content': preview,
                            'icon': '💭'
                        }

                # Tool use (ToolUseBlock)
                elif hasattr(item, 'type') and item.type == 'tool_use':
                    tool_name = getattr(item, 'name', 'unknown_tool')
                    tool_input = getattr(item, 'input', {})
                    # Format tool call nicely based on tool type
                    if tool_name == 'Edit':
                        file_path = tool_input.get('file_path', '?')
                        content_preview = f"Editing {file_path}"
                    elif tool_name == 'Bash':
                        command = tool_input.get('command', '?')[:100]
                        content_preview = f"Running: {command}"
                    elif tool_name == 'Write':
                        file_path = tool_input.get('file_path', '?')
                        content_preview = f"Writing {file_path}"
                    elif tool_name == 'Read':
                        file_path = tool_input.get('file_path', '?')
                        content_preview = f"Reading {file_path}"
                    else:
                        input_str = json.dumps(tool_input, indent=2)[:100]
                        content_preview = f"{tool_name}({input_str}...)"

                    return {
                        'timestamp': timestamp,
                        'type': 'tool',
                        'content': content_preview,
                        'icon': '🔧'
                    }

                # Also check for ToolUseBlock class directly
                elif type(item).__name__ == 'ToolUseBlock':
                    tool_name = getattr(item, 'name', 'unknown_tool')
                    tool_input = getattr(item, 'input', {})
                    if tool_name == 'Edit':
                        file_path = tool_input.get('file_path', '?')
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Editing {file_path}",
                            'icon': '✏️'
                        }
                    elif tool_name == 'Bash':
                        command = tool_input.get('command', '?')[:100]
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Running: {command}",
                            'icon': '⚙️'
                        }
                    elif tool_name == 'Write':
                        file_path = tool_input.get('file_path', '?')
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"Writing {file_path}",
                            'icon': '📝'
                        }
                    else:
                        return {
                            'timestamp': timestamp,
                            'type': 'tool',
                            'content': f"{tool_name}(...)",
                            'icon': '🔧'
                        }

                # Tool result
                elif hasattr(item, 'type') and item.type == 'tool_result':
                    tool_id = getattr(item, 'tool_use_id', 'unknown')
                    result_content = getattr(item, 'content', '')
                    # Extract useful info from result
                    if isinstance(result_content, list) and len(result_content) > 0:
                        first_item = result_content[0]
                        if hasattr(first_item, 'text'):
                            result_preview = first_item.text[:150] + '...' if len(first_item.text) > 150 else first_item.text
                        else:
                            result_preview = str(result_content)[:150]
                    else:
                        result_preview = str(result_content)[:150]

                    return {
                        'timestamp': timestamp,
                        'type': 'result',
                        'content': f"Result: {result_preview}",
                        'icon': '✅'
                    }

                # Text output
                elif hasattr(item, 'type') and item.type == 'text':
                    text_content = getattr(item, 'text', '')
                    if text_content:
                        preview = text_content[:200] + '...' if len(text_content) > 200 else text_content
                        return {
                            'timestamp': timestamp,
                            'type': 'text',
                            'content': preview,
                            'icon': '💬'
                        }

        # Error events
        if hasattr(event, 'error'):
            return {
                'timestamp': timestamp,
                'type': 'error',
                'content': str(event.error),
                'icon': '❌'
            }

        # Skip events we don't recognize
        return None

    async def analyze_file(self, file_path: str, event_callback=None, refinement_prompt=None, original_run_id=None) -> dict:
        """
        Analyze Excel file using Claude Agent SDK.

        Args:
            file_path: Path to uploaded Excel file
            event_callback: Optional callback function to receive real-time events
            refinement_prompt: Optional user feedback/refinement request
            original_run_id: Optional ID of original analysis (for refinement context)

        Returns:
            dict with dashboard_path, insights, and execution log
        """
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # System prompt for the agent - COMPREHENSIVE ANALYSIS MODE
        system_prompt = """You are a world-class data scientist and analyst with unlimited time and resources.

🎯 YOUR MISSION: Perform DEEP, EXHAUSTIVE analysis of the Excel file and create a stunning interactive dashboard.

✨ YOU HAVE COMPLETE FREEDOM:
- Use MCP tools (convenient for common tasks)
  * Excel analysis tools (analyze_excel, create_visualization, etc.)
- Write Python code (more flexible and powerful)
- Run bash commands
- Use ANY approach that produces the best results
- Combine methods as needed

📋 DELIVERABLES (REQUIRED):
1. **Single Self-Contained HTML Dashboard** saved as `dashboard.html` with:
   - 5-10+ interactive Plotly visualizations EMBEDDED INLINE (NOT as separate iframe files)
   - Use Plotly's to_html(include_plotlyjs='cdn', full_html=False, div_id='unique_id')
   - Embed each chart in a <div> element directly in the HTML
   - DO NOT create separate .html files for each visualization
   - DO NOT use iframes - embed all charts inline in ONE file
   - Statistical insights and key findings
   - Professional styling and layout with CSS
   - Executive summary
   - Organized sections with tabs/navigation using JavaScript

2. **Comprehensive Analysis** including:
   - Data structure and quality assessment
   - Descriptive statistics for all columns
   - Correlation analysis with heatmaps
   - Outlier detection
   - Trend analysis (if time series data)
   - Group comparisons (if categorical data)
   - Business insights and recommendations

📊 SUGGESTED WORKFLOW (but you're free to improvise!):

1. **Explore the data**
   - Use analyze_excel tool OR write pandas code to understand structure
   - Identify column types, missing values, distributions

2. **Generate insights**
   - Use generate_insights tool OR write statistical analysis code
   - Calculate means, medians, correlations, etc.

3. **Create visualizations**
   - Write Plotly code directly in Python (DO NOT use create_visualization tool)
   - Create 5-10+ charts: bar, line, scatter, pie, heatmaps, box plots
   - Convert to inline HTML using: fig.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart1')
   - Store the HTML strings in variables, NOT separate files

4. **Build single-file dashboard**
   - Create ONE complete HTML file with all charts embedded inline
   - Combine all chart HTML strings into <div> sections
   - Add professional CSS styling for layout and design
   - Include insights, metrics, and commentary
   - Use JavaScript for tabs/interactivity if needed
   - CRITICAL: Everything must be in ONE dashboard.html file

⏰ TIME: Take 3-5 minutes. Quality and depth over speed.
🔧 APPROACH: Whatever works best! Be creative and thorough.
💡 GOAL: Impress the user with deep insights and beautiful visualizations."""

        # Build user prompt based on whether this is a refinement or initial analysis
        if refinement_prompt and original_run_id:
            # Refinement mode - reference previous work
            original_dir = self.output_dir / original_run_id
            user_prompt = f"""ANALYSIS REFINEMENT REQUEST:

📁 Excel File: {file_path}
📂 Output Directory: {run_dir}
🎯 Final Dashboard: {run_dir}/dashboard.html
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

✅ REQUIREMENTS:
- Create ONE self-contained `dashboard.html` with 5-10+ interactive Plotly visualizations EMBEDDED INLINE
- Use fig.to_html(include_plotlyjs='cdn', full_html=False) - NO separate files or iframes
- Address ALL points in the user's feedback
- Include statistical insights and key findings
- Professional styling and clear organization
- CRITICAL: All charts inline in ONE file

💡 APPROACH:
- Use any tools or methods that work best
- MCP tools, Python code, or combination
- Be thorough and creative

⏰ TIME: Take 3-5 minutes to create an excellent refined analysis.
🎯 GOAL: Deliver exactly what the user asked for!

Begin your refinement now!"""
        else:
            # Initial analysis mode
            user_prompt = f"""DEEP ANALYSIS REQUEST:

📁 Excel File: {file_path}
📂 Output Directory: {run_dir}
🎯 Final Dashboard: {run_dir}/dashboard.html

🚀 YOUR TASK:
Analyze this Excel file comprehensively and create a stunning interactive HTML dashboard.

✅ REQUIREMENTS:
1. Create ONE self-contained `dashboard.html` file in the output directory
2. Include 5-10+ interactive Plotly visualizations EMBEDDED INLINE (not as separate files)
3. Use fig.to_html(include_plotlyjs='cdn', full_html=False) to embed charts
4. Add statistical insights and key findings
5. Make it visually impressive with professional styling
6. Organize into clear sections (Overview, Visualizations, Insights, Recommendations)
7. CRITICAL: All charts must be inline in dashboard.html - do NOT create separate viz files

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
        """Create a fallback dashboard if agent fails."""
        dashboard_path = run_dir / "dashboard.html"
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Excel Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Excel Analysis Results</h1>
        <pre>{json.dumps(data, indent=2)}</pre>
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
                       refinement_prompt=None, original_run_id=None) -> dict:
    """Synchronous wrapper for Flask route."""
    agent = ExcelAnalysisAgent(output_dir)
    return asyncio.run(agent.analyze_file(
        file_path,
        event_callback=event_callback,
        refinement_prompt=refinement_prompt,
        original_run_id=original_run_id
    ))
