import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load the data
print("🔄 Loading data...")
df = pd.read_excel('uploads/routesTEST.xlsx')
print(f"✅ Loaded {df.shape[0]:,} rows and {df.shape[1]} columns")

# Data preprocessing
print("🔄 Processing data...")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['time_parsed'] = pd.to_datetime(df['time'], errors='coerce')
df['hour'] = df['time_parsed'].dt.hour
df['day_of_week'] = df['date'].dt.day_name()
df['month'] = df['date'].dt.month_name()
df['date_only'] = df['date'].dt.date

# Create visualizations as inline HTML strings
chart_htmls = []
print("🔄 Creating visualizations...")

# 1. Route Distribution by Status
print("  📊 Chart 1: Status distribution...")
status_counts = df['status'].value_counts().reset_index()
status_counts.columns = ['status', 'count']
fig1 = px.bar(status_counts,
              x='status', y='count',
              title='<b>Route Distribution by Status</b>',
              labels={'status': 'Status Code', 'count': 'Number of Records'},
              color='count',
              color_continuous_scale='viridis',
              text='count')
fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
fig1.update_layout(template='plotly_white', height=450, showlegend=False)
chart_htmls.append(fig1.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart1'))

# 2. Routes per City (Top 15)
print("  📊 Chart 2: Top cities...")
city_counts = df['citysmbl'].value_counts().head(15).reset_index()
city_counts.columns = ['citysmbl', 'count']
fig2 = px.bar(city_counts, x='citysmbl', y='count',
              title='<b>Top 15 Cities by Route Count</b>',
              labels={'citysmbl': 'City Code', 'count': 'Number of Routes'},
              color='count',
              color_continuous_scale='Blues',
              text='count')
fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
fig2.update_layout(template='plotly_white', height=450, showlegend=False)
chart_htmls.append(fig2.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart2'))

# 3. Geographic Scatter Plot
print("  📊 Chart 3: Geographic distribution...")
sample_df = df[df['latitude'].notna() & df['longtitude'].notna()].sample(min(2000, len(df)))
fig3 = px.scatter_mapbox(sample_df,
                          lat='latitude',
                          lon='longtitude',
                          color='status',
                          size_max=10,
                          zoom=5,
                          title='<b>Geographic Distribution of Routes</b>',
                          mapbox_style='open-street-map',
                          height=550)
fig3.update_layout(template='plotly_white')
chart_htmls.append(fig3.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart3'))

# 4. Hourly Activity Pattern
print("  📊 Chart 4: Hourly patterns...")
hourly_data = df.groupby('hour').size().reset_index(name='count')
fig4 = px.area(hourly_data, x='hour', y='count',
               title='<b>Hourly Route Activity Pattern</b>',
               labels={'hour': 'Hour of Day (24h)', 'count': 'Number of Routes'})
fig4.update_traces(line_color='#FF6B6B', fill='tozeroy', fillcolor='rgba(255, 107, 107, 0.3)')
fig4.update_layout(template='plotly_white', height=400, showlegend=False)
chart_htmls.append(fig4.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart4'))

# 5. Day of Week Distribution
print("  📊 Chart 5: Weekly patterns...")
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_data = df['day_of_week'].value_counts().reindex(dow_order, fill_value=0).reset_index()
dow_data.columns = ['day_of_week', 'count']
fig5 = px.bar(dow_data, x='day_of_week', y='count',
              title='<b>Route Distribution by Day of Week</b>',
              labels={'day_of_week': 'Day', 'count': 'Number of Routes'},
              color='count',
              color_continuous_scale='Teal',
              text='count')
fig5.update_traces(texttemplate='%{text:,}', textposition='outside')
fig5.update_layout(template='plotly_white', height=400, showlegend=False)
chart_htmls.append(fig5.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart5'))

# 6. Routes by Route ID (Top 20)
print("  📊 Chart 6: Top routes...")
route_counts = df['routeid'].value_counts().head(20).reset_index()
route_counts.columns = ['routeid', 'count']
fig6 = px.bar(route_counts, x='routeid', y='count',
              title='<b>Top 20 Routes by Frequency</b>',
              labels={'routeid': 'Route ID', 'count': 'Number of Records'},
              color='count',
              color_continuous_scale='Purples',
              text='count')
fig6.update_traces(texttemplate='%{text:,}', textposition='outside')
fig6.update_layout(template='plotly_white', height=450, xaxis_tickangle=-45, showlegend=False)
chart_htmls.append(fig6.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart6'))

# 7. Street Distribution (Top 15)
print("  📊 Chart 7: Top streets...")
street_counts = df['streetsmbl'].value_counts().head(15).reset_index()
street_counts.columns = ['streetsmbl', 'count']
fig7 = px.bar(street_counts, x='count', y='streetsmbl',
              title='<b>Top 15 Streets by Route Count</b>',
              labels={'streetsmbl': 'Street Code', 'count': 'Number of Routes'},
              orientation='h',
              color='count',
              color_continuous_scale='Greens',
              text='count')
fig7.update_traces(texttemplate='%{text:,}', textposition='outside')
fig7.update_layout(template='plotly_white', height=500, showlegend=False)
chart_htmls.append(fig7.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart7'))

# 8. Device (IMEI) Usage Distribution
print("  📊 Chart 8: Device usage...")
imei_counts = df['IMEI'].value_counts().head(10).reset_index()
imei_counts.columns = ['IMEI', 'count']
fig8 = px.pie(imei_counts, values='count', names='IMEI',
              title='<b>Top 10 Devices (IMEI) by Usage</b>',
              hole=0.4)
fig8.update_traces(textposition='inside', textinfo='percent+label')
fig8.update_layout(template='plotly_white', height=450)
chart_htmls.append(fig8.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart8'))

# 9. Daily Trends
print("  📊 Chart 9: Daily trends...")
daily_data = df.groupby('date_only').size().reset_index(name='count')
daily_data.columns = ['date', 'count']
fig9 = px.line(daily_data, x='date', y='count',
               title='<b>Daily Route Trends</b>',
               labels={'date': 'Date', 'count': 'Number of Routes'},
               markers=True)
fig9.update_traces(line_color='#4ECDC4', line_width=3, marker_size=6)
fig9.update_layout(template='plotly_white', height=400)
chart_htmls.append(fig9.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart9'))

# 10. Latitude Distribution
print("  📊 Chart 10: Latitude distribution...")
fig10 = px.histogram(df, x='latitude', nbins=50,
                     title='<b>Latitude Distribution</b>',
                     labels={'latitude': 'Latitude', 'count': 'Frequency'},
                     color_discrete_sequence=['#95E1D3'])
fig10.update_layout(template='plotly_white', height=400, showlegend=False)
chart_htmls.append(fig10.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart10'))

# 11. Longitude Distribution
print("  📊 Chart 11: Longitude distribution...")
fig11 = px.histogram(df, x='longtitude', nbins=50,
                     title='<b>Longitude Distribution</b>',
                     labels={'longtitude': 'Longitude', 'count': 'Frequency'},
                     color_discrete_sequence=['#F38181'])
fig11.update_layout(template='plotly_white', height=400, showlegend=False)
chart_htmls.append(fig11.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart11'))

# Calculate key insights
print("🔄 Calculating insights...")
total_routes = len(df)
unique_routes = df['routeid'].nunique()
unique_devices = df['IMEI'].nunique()
unique_cities = df['citysmbl'].nunique()
unique_streets = df['streetsmbl'].nunique()
date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
most_common_status = int(df['status'].mode()[0]) if not df['status'].mode().empty else 'N/A'
peak_hour = int(df['hour'].mode()[0]) if not df['hour'].mode().empty else 'N/A'
most_active_city = int(df['citysmbl'].value_counts().index[0]) if not df['citysmbl'].empty else 'N/A'
busiest_day = df['day_of_week'].value_counts().index[0] if len(df['day_of_week'].value_counts()) > 0 else 'N/A'

# Statistical insights
lat_mean = df['latitude'].mean()
lat_std = df['latitude'].std()
lon_mean = df['longtitude'].mean()
lon_std = df['longtitude'].std()

# Missing data analysis
missing_summary = df.isnull().sum()
missing_pct = (missing_summary / len(df) * 100).round(2)

# Top statistics
top_route = df['routeid'].value_counts().iloc[0]
top_route_id = df['routeid'].value_counts().index[0]
avg_records_per_route = total_routes / unique_routes
data_completeness = ((1 - df.isnull().sum().sum()/(len(df)*len(df.columns)))*100)

# Create the comprehensive dashboard HTML
print("🔄 Building dashboard HTML...")
dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Route Analytics Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .nav-tabs {{
            background: #f8f9fa;
            padding: 0;
            display: flex;
            border-bottom: 3px solid #667eea;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .nav-tab {{
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            background: #f8f9fa;
            border: none;
            font-size: 1.1em;
            font-weight: 600;
            color: #555;
            transition: all 0.3s ease;
        }}

        .nav-tab:hover {{
            background: #e9ecef;
            color: #667eea;
        }}

        .nav-tab.active {{
            background: #667eea;
            color: white;
        }}

        .tab-content {{
            display: none;
            padding: 40px;
            animation: fadeIn 0.5s;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}

        .metric-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
        }}

        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .insights-section {{
            margin-top: 30px;
        }}

        .insight-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }}

        .insight-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}

        .insight-card ul {{
            padding-left: 20px;
        }}

        .insight-card li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}

        .recommendation {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        .recommendation h3 {{
            margin-bottom: 15px;
            font-size: 1.3em;
        }}

        .recommendation ul {{
            padding-left: 20px;
        }}

        .recommendation li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .footer {{
            background: #2d3436;
            color: white;
            text-align: center;
            padding: 20px;
        }}

        .stat-highlight {{
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: 600;
            color: #2d3436;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Route Analytics Dashboard</h1>
            <p>Comprehensive Analysis of Route Data | Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab(event, 'overview')">📊 Overview</button>
            <button class="nav-tab" onclick="showTab(event, 'visualizations')">📈 Visualizations</button>
            <button class="nav-tab" onclick="showTab(event, 'insights')">💡 Insights</button>
            <button class="nav-tab" onclick="showTab(event, 'recommendations')">🎯 Recommendations</button>
        </div>

        <!-- OVERVIEW TAB -->
        <div id="overview" class="tab-content active">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">📊 Executive Summary</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Records</h3>
                    <div class="value">{total_routes:,}</div>
                </div>
                <div class="metric-card">
                    <h3>Unique Routes</h3>
                    <div class="value">{unique_routes:,}</div>
                </div>
                <div class="metric-card">
                    <h3>Unique Devices</h3>
                    <div class="value">{unique_devices}</div>
                </div>
                <div class="metric-card">
                    <h3>Cities Covered</h3>
                    <div class="value">{unique_cities}</div>
                </div>
                <div class="metric-card">
                    <h3>Streets Tracked</h3>
                    <div class="value">{unique_streets}</div>
                </div>
                <div class="metric-card">
                    <h3>Most Common Status</h3>
                    <div class="value">{most_common_status}</div>
                </div>
                <div class="metric-card">
                    <h3>Peak Hour</h3>
                    <div class="value">{peak_hour}:00</div>
                </div>
                <div class="metric-card">
                    <h3>Busiest Day</h3>
                    <div class="value" style="font-size: 1.5em;">{busiest_day[:3]}</div>
                </div>
            </div>

            <div class="stat-highlight">
                📅 <strong>Date Range:</strong> {date_range} ({(df['date'].max() - df['date'].min()).days} days)
            </div>

            <div class="stat-highlight">
                🏆 <strong>Most Active City:</strong> {most_active_city} with {df[df['citysmbl'] == most_active_city].shape[0]:,} routes ({(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}%)
            </div>

            <div class="stat-highlight">
                🔥 <strong>Top Route:</strong> Route {top_route_id} appears {top_route:,} times (most frequent)
            </div>

            <div class="insight-card">
                <h3>📋 Data Quality Summary</h3>
                <p><strong>Overall Completeness:</strong> {data_completeness:.2f}%</p>
                <table>
                    <tr>
                        <th>Column</th>
                        <th>Missing Values</th>
                        <th>Missing %</th>
                        <th>Status</th>
                    </tr>
                    {''.join([f'<tr><td>{col}</td><td>{missing_summary[col]}</td><td>{missing_pct[col]}%</td><td>{"✅ Good" if missing_pct[col] < 5 else "⚠️ Check" if missing_pct[col] < 20 else "❌ Poor"}</td></tr>' for col in df.columns])}
                </table>
            </div>

            <div class="insight-card">
                <h3>📍 Geographic Coverage</h3>
                <ul>
                    <li><strong>Center Latitude:</strong> {lat_mean:.6f} (±{lat_std:.6f})</li>
                    <li><strong>Center Longitude:</strong> {lon_mean:.6f} (±{lon_std:.6f})</li>
                    <li><strong>Geographic Spread:</strong> Data covers {unique_cities} unique cities and {unique_streets} unique streets</li>
                    <li><strong>Average Records per Route:</strong> {avg_records_per_route:.2f}</li>
                </ul>
            </div>
        </div>

        <!-- VISUALIZATIONS TAB -->
        <div id="visualizations" class="tab-content">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">📈 Interactive Visualizations</h2>

            <div class="chart-container">
                {chart_htmls[0]}
            </div>

            <div class="chart-container">
                {chart_htmls[1]}
            </div>

            <div class="chart-container">
                {chart_htmls[2]}
            </div>

            <div class="chart-container">
                {chart_htmls[3]}
            </div>

            <div class="chart-container">
                {chart_htmls[4]}
            </div>

            <div class="chart-container">
                {chart_htmls[5]}
            </div>

            <div class="chart-container">
                {chart_htmls[6]}
            </div>

            <div class="chart-container">
                {chart_htmls[7]}
            </div>

            <div class="chart-container">
                {chart_htmls[8]}
            </div>

            <div class="chart-container">
                {chart_htmls[9]}
            </div>

            <div class="chart-container">
                {chart_htmls[10]}
            </div>
        </div>

        <!-- INSIGHTS TAB -->
        <div id="insights" class="tab-content">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">💡 Key Insights & Findings</h2>

            <div class="insight-card">
                <h3>🔍 Status Distribution Analysis</h3>
                <ul>
                    <li>The dataset contains <strong>{df['status'].nunique()} unique status values</strong></li>
                    <li>Most common status is <strong>{most_common_status}</strong> with {df['status'].value_counts().iloc[0]:,} occurrences ({(df['status'].value_counts().iloc[0]/len(df)*100):.1f}%)</li>
                    <li>Status codes range from {df['status'].min()} to {df['status'].max()}</li>
                    <li>{'Status distribution is concentrated' if df['status'].value_counts().iloc[0]/len(df) > 0.5 else 'Status distribution is fairly distributed'}</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🌆 Geographic Distribution</h3>
                <ul>
                    <li><strong>Most Active City:</strong> City {most_active_city} leads with {df[df['citysmbl'] == most_active_city].shape[0]:,} routes ({(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}% of total)</li>
                    <li><strong>Top 10 Cities:</strong> Account for {(df['citysmbl'].value_counts().head(10).sum()/len(df)*100):.1f}% of all routes</li>
                    <li><strong>Coverage Span:</strong> {unique_cities} cities, indicating {'widespread' if unique_cities > 20 else 'concentrated'} geographic distribution</li>
                    <li><strong>Street Network:</strong> {unique_streets} unique streets tracked across the network</li>
                    <li><strong>Geographic Concentration:</strong> {'High concentration in top cities suggests focused operations' if (df['citysmbl'].value_counts().head(3).sum()/len(df)) > 0.5 else 'Distributed across multiple cities indicating broad coverage'}</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>⏰ Temporal Patterns</h3>
                <ul>
                    <li><strong>Peak Activity Hour:</strong> {peak_hour}:00 hours shows maximum route activity</li>
                    <li><strong>Busiest Day:</strong> {busiest_day} with {df[df['day_of_week'] == busiest_day].shape[0]:,} routes</li>
                    <li><strong>Daily Variation:</strong> Routes range from {df.groupby('date_only').size().min()} to {df.groupby('date_only').size().max()} per day (mean: {df.groupby('date_only').size().mean():.1f})</li>
                    <li><strong>Hour Distribution:</strong> Activity spans {df['hour'].nunique()} hours, {'suggesting 24/7 operations' if df['hour'].nunique() >= 20 else 'concentrated in specific hours'}</li>
                    <li><strong>Weekly Pattern:</strong> {'Consistent distribution across weekdays' if df['day_of_week'].value_counts().std() < df['day_of_week'].value_counts().mean() * 0.3 else 'Varied distribution shows peak/off-peak days'}</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🚛 Route & Device Analytics</h3>
                <ul>
                    <li><strong>Route Efficiency:</strong> Average of {avg_records_per_route:.2f} records per unique route</li>
                    <li><strong>Device Fleet:</strong> {unique_devices} unique devices (IMEI) actively tracked</li>
                    <li><strong>Top Route Frequency:</strong> Route {top_route_id} appears {top_route:,} times (highest frequency)</li>
                    <li><strong>Route Concentration:</strong> Top 20 routes account for {(df['routeid'].value_counts().head(20).sum()/len(df)*100):.1f}% of all data</li>
                    <li><strong>Device Utilization:</strong> Average of {(total_routes/unique_devices):.1f} records per device</li>
                    <li><strong>Route Diversity:</strong> {unique_routes} unique routes across {unique_cities} cities (avg {(unique_routes/unique_cities):.1f} routes/city)</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>📊 Data Quality Observations</h3>
                <ul>
                    <li><strong>Dataset Completeness:</strong> {data_completeness:.2f}% complete overall</li>
                    <li><strong>Critical Fields:</strong> Latitude, longitude, and routeid have {'minimal' if df[['latitude', 'longtitude', 'routeid']].isnull().sum().max() < len(df)*0.01 else 'some'} missing data</li>
                    <li><strong>Time Coverage:</strong> {(df['date'].max() - df['date'].min()).days} days of data</li>
                    <li><strong>Data Density:</strong> {(total_routes/max(1, (df['date'].max() - df['date'].min()).days)):.1f} records per day on average</li>
                    <li><strong>Missing Data Impact:</strong> {len([col for col in df.columns if missing_pct[col] > 5])} columns have > 5% missing values</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🎯 Performance Metrics</h3>
                <ul>
                    <li><strong>Top City Performance:</strong> City {most_active_city} dominates with {(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}% market share</li>
                    <li><strong>Route Reuse Rate:</strong> Average route is tracked {avg_records_per_route:.2f} times</li>
                    <li><strong>Peak Hour Concentration:</strong> Hour {peak_hour} accounts for {(df[df['hour'] == peak_hour].shape[0]/len(df)*100):.1f}% of daily activity</li>
                    <li><strong>Weekday vs All Days:</strong> Weekdays represent {(df[df['day_of_week'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])].shape[0]/len(df)*100):.1f}% of routes</li>
                </ul>
            </div>
        </div>

        <!-- RECOMMENDATIONS TAB -->
        <div id="recommendations" class="tab-content">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">🎯 Strategic Recommendations</h2>

            <div class="recommendation">
                <h3>🎯 Operational Optimization</h3>
                <ul>
                    <li><strong>Peak Hour Staffing:</strong> Allocate 30-40% more resources during hour {peak_hour}:00 when activity peaks at {(df[df['hour'] == peak_hour].shape[0]/len(df)*100):.1f}% of daily volume</li>
                    <li><strong>Route Consolidation:</strong> Focus optimization on top 20 routes representing {(df['routeid'].value_counts().head(20).sum()/len(df)*100):.1f}% of operations for maximum impact</li>
                    <li><strong>Device Reallocation:</strong> Analyze utilization patterns across {unique_devices} devices to balance load (current avg: {(total_routes/unique_devices):.1f} records/device)</li>
                    <li><strong>Status Code Management:</strong> Monitor status {most_common_status} which accounts for {(df['status'].value_counts().iloc[0]/len(df)*100):.1f}% of routes for quality assurance</li>
                    <li><strong>Day-of-Week Planning:</strong> Prepare enhanced resources for {busiest_day} (busiest day) to handle peak demand</li>
                </ul>
            </div>

            <div class="recommendation">
                <h3>🌍 Geographic Strategy</h3>
                <ul>
                    <li><strong>Leverage Top Performer:</strong> Use City {most_active_city}'s successful model ({(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}% market share) as template for expansion</li>
                    <li><strong>Market Penetration:</strong> Top 10 cities drive {(df['citysmbl'].value_counts().head(10).sum()/len(df)*100):.1f}% of volume - consider deepening services here before expanding</li>
                    <li><strong>Underserved Markets:</strong> Identify growth opportunities in cities below median route count for expansion</li>
                    <li><strong>Regional Clustering:</strong> Group {unique_cities} cities into regional hubs for operational efficiency</li>
                    <li><strong>Street-Level Optimization:</strong> Analyze top streets (currently tracking {unique_streets}) for micro-route optimization</li>
                </ul>
            </div>

            <div class="recommendation">
                <h3>📈 Data & Analytics Initiatives</h3>
                <ul>
                    <li><strong>Data Quality Enhancement:</strong> Address {len([col for col in df.columns if missing_pct[col] > 0])} columns with missing values to improve analysis accuracy from {data_completeness:.2f}% to 100%</li>
                    <li><strong>Real-time Dashboards:</strong> Deploy live monitoring for route status, device performance, and geographic coverage</li>
                    <li><strong>Predictive Analytics:</strong> Build ML models using {total_routes:,} historical records to forecast demand by hour/day/city</li>
                    <li><strong>KPI Framework:</strong> Establish metrics for route efficiency (current: {avg_records_per_route:.2f} records/route), device utilization, and city coverage</li>
                    <li><strong>Anomaly Detection:</strong> Implement alerts for unusual patterns in status codes, timing, or geographic anomalies</li>
                </ul>
            </div>

            <div class="recommendation">
                <h3>⚡ Quick Wins (30-Day Actions)</h3>
                <ul>
                    <li><strong>Status Monitoring:</strong> Set up automated alerts for non-standard status codes (currently {df['status'].nunique()} unique statuses)</li>
                    <li><strong>Peak Hour Response:</strong> Immediately increase hour {peak_hour} capacity by {(df[df['hour'] == peak_hour].shape[0]/df['hour'].value_counts().mean() - 1)*100:.0f}% vs average hour</li>
                    <li><strong>Route Audit:</strong> Review top 20 routes ({(df['routeid'].value_counts().head(20).sum()/len(df)*100):.1f}% of volume) for optimization opportunities</li>
                    <li><strong>Device Maintenance:</strong> Schedule preventive maintenance for devices with highest usage (top 10 devices handle significant load)</li>
                    <li><strong>Geographic Focus:</strong> Deploy additional resources to City {most_active_city} to capitalize on market leadership</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🔮 Future Analysis Opportunities</h3>
                <ul>
                    <li><strong>Machine Learning:</strong> Implement route optimization algorithms using historical patterns from {(df['date'].max() - df['date'].min()).days} days of data</li>
                    <li><strong>Time Series Forecasting:</strong> Predict future demand by analyzing {df.groupby('date_only').size().count()} days of daily trends</li>
                    <li><strong>Clustering Analysis:</strong> Segment routes into operational clusters based on {unique_cities} cities, {unique_streets} streets, and usage patterns</li>
                    <li><strong>Device Lifecycle:</strong> Build predictive maintenance models for {unique_devices} devices based on usage intensity</li>
                    <li><strong>Customer Segmentation:</strong> Analyze address patterns to identify customer segments and service needs</li>
                    <li><strong>Network Optimization:</strong> Use geographic data (lat/lon) to optimize route paths and reduce travel time</li>
                    <li><strong>Capacity Planning:</strong> Model future capacity needs using current growth trends and seasonality</li>
                </ul>
            </div>

            <div class="stat-highlight">
                💡 <strong>Priority Action:</strong> Focus on the top 20 routes and City {most_active_city} for immediate impact - this combination represents over {((df['routeid'].value_counts().head(20).sum() + df[df['citysmbl'] == most_active_city].shape[0])/len(df)/2*100):.0f}% of your operational footprint!
            </div>
        </div>

        <div class="footer">
            <p>📊 Dashboard Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 📈 Data Points: {total_routes:,} | 🎯 Routes: {unique_routes} | 📱 Devices: {unique_devices} | 🌆 Cities: {unique_cities}</p>
            <p style="margin-top: 10px; opacity: 0.8;">Powered by Python, Pandas & Plotly | All visualizations are interactive - hover, zoom, and pan!</p>
        </div>
    </div>

    <script>
        function showTab(evt, tabName) {{
            // Hide all tabs
            var tabs = document.getElementsByClassName('tab-content');
            for (var i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove('active');
            }}

            // Remove active class from all nav buttons
            var navTabs = document.getElementsByClassName('nav-tab');
            for (var i = 0; i < navTabs.length; i++) {{
                navTabs[i].classList.remove('active');
            }}

            // Show selected tab
            document.getElementById(tabName).classList.add('active');

            // Add active class to clicked button
            evt.currentTarget.classList.add('active');
        }}
    </script>
</body>
</html>
"""

# Save the dashboard
output_path = 'outputs/20251005_090914/dashboard.html'
print(f"🔄 Saving dashboard to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

print(f"\n✅ SUCCESS! Dashboard created at: {output_path}")
print(f"📊 Total visualizations: {len(chart_htmls)}")
print(f"🎨 All {len(chart_htmls)} charts embedded inline in a single HTML file")
print(f"📁 File size: {len(dashboard_html)/1024:.1f} KB")
print(f"\n🚀 Open the dashboard in your browser to explore the data!")
