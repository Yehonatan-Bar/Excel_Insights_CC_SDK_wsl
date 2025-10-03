"""
Custom MCP Tools for Excel Analysis and Visualization
"""
import json
from pathlib import Path
from typing import Any, Dict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from claude_agent_sdk import tool


@tool(
    "analyze_excel",
    "Load and analyze Excel file, return summary statistics and data overview",
    {"file_path": str}
)
async def analyze_excel(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze Excel file and return comprehensive statistics."""
    file_path = args["file_path"]

    try:
        # Read Excel file
        df = pd.read_excel(file_path)

        # Generate analysis
        analysis = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if not df.select_dtypes(include='number').empty else {},
            "sample_data": df.head(5).to_dict(orient='records')
        }

        return {
            "content": [{
                "type": "text",
                "text": f"Analyzed Excel file: {len(df)} rows, {len(df.columns)} columns\nColumns: {', '.join(df.columns.tolist())}"
            }],
            "result": analysis
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error analyzing Excel: {str(e)}"}],
            "is_error": True
        }


@tool(
    "create_visualization",
    "Create Plotly visualization from Excel data and save as HTML",
    {"file_path": str, "chart_type": str, "x_column": str, "y_column": str, "output_path": str}
)
async def create_visualization(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create Plotly chart from Excel data."""
    file_path = args["file_path"]
    chart_type = args["chart_type"]  # 'bar', 'line', 'scatter', 'pie'
    x_column = args.get("x_column")
    y_column = args.get("y_column")
    output_path = args["output_path"]

    try:
        df = pd.read_excel(file_path)

        # Create chart based on type
        if chart_type == "bar":
            fig = px.bar(df, x=x_column, y=y_column, title=f"{y_column} by {x_column}")
        elif chart_type == "line":
            fig = px.line(df, x=x_column, y=y_column, title=f"{y_column} over {x_column}")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
        elif chart_type == "pie":
            fig = px.pie(df, names=x_column, values=y_column, title=f"{y_column} Distribution")
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        # Save as HTML
        fig.write_html(output_path)

        return {
            "content": [{
                "type": "text",
                "text": f"Created {chart_type} chart: {output_path}"
            }],
            "result": {"chart_path": output_path, "chart_type": chart_type}
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error creating visualization: {str(e)}"}],
            "is_error": True
        }


@tool(
    "generate_insights",
    "Analyze data patterns and generate insights from Excel data",
    {"file_path": str}
)
async def generate_insights(args: Dict[str, Any]) -> Dict[str, Any]:
    """Generate data insights automatically."""
    file_path = args["file_path"]

    try:
        df = pd.read_excel(file_path)
        insights = []

        # Numeric column insights
        numeric_cols = df.select_dtypes(include='number').columns
        for col in numeric_cols:
            insights.append({
                "column": col,
                "type": "numeric",
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max())
            })

        # Categorical insights
        categorical_cols = df.select_dtypes(include='object').columns
        for col in categorical_cols:
            value_counts = df[col].value_counts().head(5).to_dict()
            insights.append({
                "column": col,
                "type": "categorical",
                "unique_values": int(df[col].nunique()),
                "top_values": value_counts
            })

        return {
            "content": [{
                "type": "text",
                "text": f"Generated {len(insights)} insights from {len(df.columns)} columns"
            }],
            "result": {"insights": insights}
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error generating insights: {str(e)}"}],
            "is_error": True
        }


@tool(
    "create_dashboard",
    "Create HTML dashboard combining multiple visualizations and insights",
    {"charts": list, "insights": dict, "output_path": str}
)
async def create_dashboard(args: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete HTML dashboard."""
    charts = args.get("charts", [])
    insights = args.get("insights", {})
    output_path = args["output_path"]

    try:
        # Create dashboard HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Excel Insights Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .insight-card {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .chart {{ margin: 20px 0; }}
        iframe {{ width: 100%; height: 500px; border: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Excel Data Insights Dashboard</h1>

        <h2>Key Insights</h2>
        <div class="insights">
            {_generate_insight_html(insights)}
        </div>

        <h2>Visualizations</h2>
        <div class="charts">
            {_generate_chart_html(charts)}
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html_content)

        return {
            "content": [{
                "type": "text",
                "text": f"Dashboard created: {output_path}"
            }],
            "result": {"dashboard_path": output_path}
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error creating dashboard: {str(e)}"}],
            "is_error": True
        }


def _generate_insight_html(insights: dict) -> str:
    """Helper to generate insights HTML."""
    html = ""
    for insight in insights.get("insights", []):
        col = insight.get("column")
        if insight.get("type") == "numeric":
            html += f"""
            <div class="insight-card">
                <h3>{col}</h3>
                <p>Mean: {insight.get('mean', 0):.2f} | Median: {insight.get('median', 0):.2f}</p>
                <p>Range: {insight.get('min', 0):.2f} - {insight.get('max', 0):.2f}</p>
            </div>
            """
        elif insight.get("type") == "categorical":
            html += f"""
            <div class="insight-card">
                <h3>{col}</h3>
                <p>Unique values: {insight.get('unique_values', 0)}</p>
            </div>
            """
    return html


def _generate_chart_html(charts: list) -> str:
    """Helper to generate chart iframes."""
    html = ""
    for chart in charts:
        html += f'<div class="chart"><iframe src="{chart}"></iframe></div>'
    return html


@tool(
    "correlation_analysis",
    "Analyze correlations between numeric columns and create correlation matrix visualization",
    {"file_path": str, "output_path": str}
)
async def correlation_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Generate correlation analysis and heatmap."""
    file_path = args["file_path"]
    output_path = args["output_path"]

    try:
        df = pd.read_excel(file_path)
        numeric_df = df.select_dtypes(include='number')

        if numeric_df.empty:
            return {
                "content": [{"type": "text", "text": "No numeric columns found for correlation analysis"}],
                "result": {}
            }

        # Calculate correlations
        corr_matrix = numeric_df.corr()

        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
        ))
        fig.update_layout(title="Correlation Matrix Heatmap", width=800, height=800)
        fig.write_html(output_path)

        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.5:  # Strong correlation threshold
                    strong_corr.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": float(val)
                    })

        return {
            "content": [{
                "type": "text",
                "text": f"Correlation analysis complete. Found {len(strong_corr)} strong correlations. Heatmap saved to {output_path}"
            }],
            "result": {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_corr,
                "chart_path": output_path
            }
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error in correlation analysis: {str(e)}"}],
            "is_error": True
        }


@tool(
    "detect_outliers",
    "Detect outliers in numeric columns using IQR method",
    {"file_path": str, "column": str}
)
async def detect_outliers(args: Dict[str, Any]) -> Dict[str, Any]:
    """Detect outliers in a specific column."""
    file_path = args["file_path"]
    column = args["column"]

    try:
        df = pd.read_excel(file_path)

        if column not in df.columns:
            return {
                "content": [{"type": "text", "text": f"Column '{column}' not found"}],
                "is_error": True
            }

        if not pd.api.types.is_numeric_dtype(df[column]):
            return {
                "content": [{"type": "text", "text": f"Column '{column}' is not numeric"}],
                "is_error": True
            }

        # IQR method
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        outlier_count = len(outliers)

        return {
            "content": [{
                "type": "text",
                "text": f"Found {outlier_count} outliers in '{column}' (bounds: {lower_bound:.2f} - {upper_bound:.2f})"
            }],
            "result": {
                "column": column,
                "outlier_count": outlier_count,
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_values": outliers[column].tolist()
            }
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error detecting outliers: {str(e)}"}],
            "is_error": True
        }


@tool(
    "group_comparison",
    "Compare statistics across groups for a numeric column",
    {"file_path": str, "group_column": str, "value_column": str, "output_path": str}
)
async def group_comparison(args: Dict[str, Any]) -> Dict[str, Any]:
    """Compare groups and create visualization."""
    file_path = args["file_path"]
    group_column = args["group_column"]
    value_column = args["value_column"]
    output_path = args["output_path"]

    try:
        df = pd.read_excel(file_path)

        # Group by and aggregate
        grouped = df.groupby(group_column)[value_column].agg(['mean', 'median', 'std', 'count'])

        # Create grouped bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Mean', x=grouped.index, y=grouped['mean']))
        fig.add_trace(go.Bar(name='Median', x=grouped.index, y=grouped['median']))
        fig.update_layout(
            title=f"{value_column} by {group_column}",
            xaxis_title=group_column,
            yaxis_title=value_column,
            barmode='group'
        )
        fig.write_html(output_path)

        return {
            "content": [{
                "type": "text",
                "text": f"Group comparison complete. Analyzed {len(grouped)} groups. Chart saved to {output_path}"
            }],
            "result": {
                "group_stats": grouped.to_dict(),
                "chart_path": output_path
            }
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error in group comparison: {str(e)}"}],
            "is_error": True
        }


@tool(
    "trend_analysis",
    "Analyze trends over time for a numeric column",
    {"file_path": str, "date_column": str, "value_column": str, "output_path": str}
)
async def trend_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze trends with moving average."""
    file_path = args["file_path"]
    date_column = args["date_column"]
    value_column = args["value_column"]
    output_path = args["output_path"]

    try:
        df = pd.read_excel(file_path)
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
        df = df.sort_values(date_column)

        # Calculate moving average
        df['MA_7'] = df[value_column].rolling(window=min(7, len(df))).mean()

        # Create trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_column], y=df[value_column], mode='lines', name='Actual'))
        fig.add_trace(go.Scatter(x=df[date_column], y=df['MA_7'], mode='lines', name='Moving Avg', line=dict(dash='dash')))
        fig.update_layout(title=f"{value_column} Trend Over Time", xaxis_title=date_column, yaxis_title=value_column)
        fig.write_html(output_path)

        # Calculate trend direction
        first_half_avg = df[value_column].iloc[:len(df)//2].mean()
        second_half_avg = df[value_column].iloc[len(df)//2:].mean()
        trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing"

        return {
            "content": [{
                "type": "text",
                "text": f"Trend analysis complete. Overall trend: {trend_direction}. Chart saved to {output_path}"
            }],
            "result": {
                "trend_direction": trend_direction,
                "first_half_avg": float(first_half_avg),
                "second_half_avg": float(second_half_avg),
                "chart_path": output_path
            }
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error in trend analysis: {str(e)}"}],
            "is_error": True
        }
