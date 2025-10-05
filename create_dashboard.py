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
              title='<b>התפלגות מסלולים לפי סטטוס</b>',
              labels={'status': 'קוד סטטוס', 'count': 'מספר רשומות'},
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
              title='<b>15 הערים המובילות לפי מספר מסלולים</b>',
              labels={'citysmbl': 'קוד עיר', 'count': 'מספר מסלולים'},
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
                          title='<b>התפלגות גיאוגרפית של מסלולים</b>',
                          mapbox_style='open-street-map',
                          height=550)
fig3.update_layout(template='plotly_white')
chart_htmls.append(fig3.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart3'))

# 4. Hourly Activity Pattern
print("  📊 Chart 4: Hourly patterns...")
hourly_data = df.groupby('hour').size().reset_index(name='count')
fig4 = px.area(hourly_data, x='hour', y='count',
               title='<b>דפוס פעילות לפי שעות</b>',
               labels={'hour': 'שעה ביום (24 שעות)', 'count': 'מספר מסלולים'})
fig4.update_traces(line_color='#FF6B6B', fill='tozeroy', fillcolor='rgba(255, 107, 107, 0.3)')
fig4.update_layout(template='plotly_white', height=400, showlegend=False)
chart_htmls.append(fig4.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart4'))

# 5. Day of Week Distribution
print("  📊 Chart 5: Weekly patterns...")
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_data = df['day_of_week'].value_counts().reindex(dow_order, fill_value=0).reset_index()
dow_data.columns = ['day_of_week', 'count']
fig5 = px.bar(dow_data, x='day_of_week', y='count',
              title='<b>התפלגות מסלולים לפי יום בשבוע</b>',
              labels={'day_of_week': 'יום', 'count': 'מספר מסלולים'},
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
              title='<b>20 המסלולים המובילים לפי תדירות</b>',
              labels={'routeid': 'מזהה מסלול', 'count': 'מספר רשומות'},
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
              title='<b>15 הרחובות המובילים לפי מספר מסלולים</b>',
              labels={'streetsmbl': 'קוד רחוב', 'count': 'מספר מסלולים'},
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
              title='<b>10 המכשירים המובילים (IMEI) לפי שימוש</b>',
              hole=0.4)
fig8.update_traces(textposition='inside', textinfo='percent+label')
fig8.update_layout(template='plotly_white', height=450)
chart_htmls.append(fig8.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart8'))

# 9. Daily Trends
print("  📊 Chart 9: Daily trends...")
daily_data = df.groupby('date_only').size().reset_index(name='count')
daily_data.columns = ['date', 'count']
fig9 = px.line(daily_data, x='date', y='count',
               title='<b>מגמות יומיות של מסלולים</b>',
               labels={'date': 'תאריך', 'count': 'מספר מסלולים'},
               markers=True)
fig9.update_traces(line_color='#4ECDC4', line_width=3, marker_size=6)
fig9.update_layout(template='plotly_white', height=400)
chart_htmls.append(fig9.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart9'))

# 10. Latitude Distribution
print("  📊 Chart 10: Latitude distribution...")
fig10 = px.histogram(df, x='latitude', nbins=50,
                     title='<b>התפלגות קו רוחב</b>',
                     labels={'latitude': 'קו רוחב', 'count': 'תדירות'},
                     color_discrete_sequence=['#95E1D3'])
fig10.update_layout(template='plotly_white', height=400, showlegend=False)
chart_htmls.append(fig10.to_html(include_plotlyjs='cdn', full_html=False, div_id='chart10'))

# 11. Longitude Distribution
print("  📊 Chart 11: Longitude distribution...")
fig11 = px.histogram(df, x='longtitude', nbins=50,
                     title='<b>התפלגות קו אורך</b>',
                     labels={'longtitude': 'קו אורך', 'count': 'תדירות'},
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
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>לוח בקרה לניתוח מסלולים</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, Arial;
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
            <h1>🚀 לוח בקרה לניתוח מסלולים</h1>
            <p>ניתוח מקיף של נתוני מסלולים | נוצר ב-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab(event, 'overview')">📊 סקירה</button>
            <button class="nav-tab" onclick="showTab(event, 'visualizations')">📈 תצוגות חזותיות</button>
            <button class="nav-tab" onclick="showTab(event, 'insights')">💡 תובנות</button>
            <button class="nav-tab" onclick="showTab(event, 'recommendations')">🎯 המלצות</button>
        </div>

        <!-- OVERVIEW TAB -->
        <div id="overview" class="tab-content active">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">📊 סיכום מנהלים</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>סה"כ רשומות</h3>
                    <div class="value">{total_routes:,}</div>
                </div>
                <div class="metric-card">
                    <h3>מסלולים ייחודיים</h3>
                    <div class="value">{unique_routes:,}</div>
                </div>
                <div class="metric-card">
                    <h3>מכשירים ייחודיים</h3>
                    <div class="value">{unique_devices}</div>
                </div>
                <div class="metric-card">
                    <h3>ערים מכוסות</h3>
                    <div class="value">{unique_cities}</div>
                </div>
                <div class="metric-card">
                    <h3>רחובות במעקב</h3>
                    <div class="value">{unique_streets}</div>
                </div>
                <div class="metric-card">
                    <h3>סטטוס שכיח ביותר</h3>
                    <div class="value">{most_common_status}</div>
                </div>
                <div class="metric-card">
                    <h3>שעת שיא</h3>
                    <div class="value">{peak_hour}:00</div>
                </div>
                <div class="metric-card">
                    <h3>יום עמוס ביותר</h3>
                    <div class="value" style="font-size: 1.5em;">{busiest_day[:3]}</div>
                </div>
            </div>

            <div class="stat-highlight">
                📅 <strong>טווח תאריכים:</strong> {date_range} ({(df['date'].max() - df['date'].min()).days} ימים)
            </div>

            <div class="stat-highlight">
                🏆 <strong>עיר הכי פעילה:</strong> {most_active_city} עם {df[df['citysmbl'] == most_active_city].shape[0]:,} מסלולים ({(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}%)
            </div>

            <div class="stat-highlight">
                🔥 <strong>מסלול מוביל:</strong> מסלול {top_route_id} מופיע {top_route:,} פעמים (השכיח ביותר)
            </div>

            <div class="insight-card">
                <h3>📋 סיכום איכות נתונים</h3>
                <p><strong>שלמות כוללת:</strong> {data_completeness:.2f}%</p>
                <table>
                    <tr>
                        <th>עמודה</th>
                        <th>ערכים חסרים</th>
                        <th>אחוז חסר</th>
                        <th>סטטוס</th>
                    </tr>
                    {''.join([f'<tr><td>{col}</td><td>{missing_summary[col]}</td><td>{missing_pct[col]}%</td><td>{"✅ טוב" if missing_pct[col] < 5 else "⚠️ בדוק" if missing_pct[col] < 20 else "❌ גרוע"}</td></tr>' for col in df.columns])}
                </table>
            </div>

            <div class="insight-card">
                <h3>📍 כיסוי גיאוגרפי</h3>
                <ul>
                    <li><strong>קו רוחב מרכזי:</strong> {lat_mean:.6f} (±{lat_std:.6f})</li>
                    <li><strong>קו אורך מרכזי:</strong> {lon_mean:.6f} (±{lon_std:.6f})</li>
                    <li><strong>פריסה גיאוגרפית:</strong> הנתונים מכסים {unique_cities} ערים ייחודיות ו-{unique_streets} רחובות ייחודיים</li>
                    <li><strong>ממוצע רשומות למסלול:</strong> {avg_records_per_route:.2f}</li>
                </ul>
            </div>
        </div>

        <!-- VISUALIZATIONS TAB -->
        <div id="visualizations" class="tab-content">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">📈 תצוגות חזותיות אינטראקטיביות</h2>

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
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">💡 תובנות וממצאים מרכזיים</h2>

            <div class="insight-card">
                <h3>🔍 ניתוח התפלגות סטטוס</h3>
                <ul>
                    <li>מערך הנתונים מכיל <strong>{df['status'].nunique()} ערכי סטטוס ייחודיים</strong></li>
                    <li>הסטטוס הנפוץ ביותר הוא <strong>{most_common_status}</strong> עם {df['status'].value_counts().iloc[0]:,} הופעות ({(df['status'].value_counts().iloc[0]/len(df)*100):.1f}%)</li>
                    <li>קודי הסטטוס נעים בטווח {df['status'].min()} עד {df['status'].max()}</li>
                    <li>{'התפלגות הסטטוס מרוכזת' if df['status'].value_counts().iloc[0]/len(df) > 0.5 else 'התפלגות הסטטוס מפוזרת באופן שווה'}</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🌆 התפלגות גיאוגרפית</h3>
                <ul>
                    <li><strong>העיר הפעילה ביותר:</strong> עיר {most_active_city} מובילה עם {df[df['citysmbl'] == most_active_city].shape[0]:,} מסלולים ({(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}% מהסך הכל)</li>
                    <li><strong>10 הערים המובילות:</strong> מהוות {(df['citysmbl'].value_counts().head(10).sum()/len(df)*100):.1f}% מכל המסלולים</li>
                    <li><strong>טווח כיסוי:</strong> {unique_cities} ערים, המציינות התפלגות גיאוגרפית {'נרחבת' if unique_cities > 20 else 'מרוכזת'}</li>
                    <li><strong>רשת רחובות:</strong> {unique_streets} רחובות ייחודיים במעקב ברחבי הרשת</li>
                    <li><strong>ריכוז גיאוגרפי:</strong> {'ריכוז גבוה בערים המובילות מצביע על פעילות ממוקדת' if (df['citysmbl'].value_counts().head(3).sum()/len(df)) > 0.5 else 'פיזור במספר ערים המעיד על כיסוי רחב'}</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>⏰ דפוסים זמניים</h3>
                <ul>
                    <li><strong>שעת שיא פעילות:</strong> שעה {peak_hour}:00 מציגה פעילות מסלולים מקסימלית</li>
                    <li><strong>היום העמוס ביותר:</strong> {busiest_day} עם {df[df['day_of_week'] == busiest_day].shape[0]:,} מסלולים</li>
                    <li><strong>שונות יומית:</strong> המסלולים נעים בטווח {df.groupby('date_only').size().min()} עד {df.groupby('date_only').size().max()} ליום (ממוצע: {df.groupby('date_only').size().mean():.1f})</li>
                    <li><strong>התפלגות שעות:</strong> פעילות משתרעת על פני {df['hour'].nunique()} שעות, {'מה שמצביע על פעילות 24/7' if df['hour'].nunique() >= 20 else 'מרוכזת בשעות ספציפיות'}</li>
                    <li><strong>דפוס שבועי:</strong> {'התפלגות עקבית לאורך ימי השבוע' if df['day_of_week'].value_counts().std() < df['day_of_week'].value_counts().mean() * 0.3 else 'התפלגות מגוונת המציגה ימי שיא וימי שפל'}</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🚛 ניתוח מסלולים ומכשירים</h3>
                <ul>
                    <li><strong>יעילות מסלולים:</strong> ממוצע של {avg_records_per_route:.2f} רשומות למסלול ייחודי</li>
                    <li><strong>צי מכשירים:</strong> {unique_devices} מכשירים ייחודיים (IMEI) במעקב פעיל</li>
                    <li><strong>תדירות מסלול מוביל:</strong> מסלול {top_route_id} מופיע {top_route:,} פעמים (תדירות הגבוהה ביותר)</li>
                    <li><strong>ריכוז מסלולים:</strong> 20 המסלולים המובילים מהווים {(df['routeid'].value_counts().head(20).sum()/len(df)*100):.1f}% מכל הנתונים</li>
                    <li><strong>ניצול מכשירים:</strong> ממוצע של {(total_routes/unique_devices):.1f} רשומות למכשיר</li>
                    <li><strong>גיוון מסלולים:</strong> {unique_routes} מסלולים ייחודיים ב-{unique_cities} ערים (ממוצע {(unique_routes/unique_cities):.1f} מסלולים/עיר)</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>📊 תצפיות על איכות הנתונים</h3>
                <ul>
                    <li><strong>שלמות מערך הנתונים:</strong> {data_completeness:.2f}% שלם בסך הכל</li>
                    <li><strong>שדות קריטיים:</strong> קו רוחב, קו אורך ומזהה מסלול כוללים נתונים חסרים {'מינימליים' if df[['latitude', 'longtitude', 'routeid']].isnull().sum().max() < len(df)*0.01 else 'מסוימים'}</li>
                    <li><strong>כיסוי זמן:</strong> {(df['date'].max() - df['date'].min()).days} ימים של נתונים</li>
                    <li><strong>צפיפות נתונים:</strong> {(total_routes/max(1, (df['date'].max() - df['date'].min()).days)):.1f} רשומות ליום בממוצע</li>
                    <li><strong>השפעת נתונים חסרים:</strong> {len([col for col in df.columns if missing_pct[col] > 5])} עמודות עם > 5% ערכים חסרים</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🎯 מדדי ביצועים</h3>
                <ul>
                    <li><strong>ביצועי עיר מובילה:</strong> עיר {most_active_city} שולטת עם {(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}% נתח שוק</li>
                    <li><strong>שיעור שימוש חוזר במסלולים:</strong> מסלול ממוצע במעקב {avg_records_per_route:.2f} פעמים</li>
                    <li><strong>ריכוז שעת שיא:</strong> שעה {peak_hour} מהווה {(df[df['hour'] == peak_hour].shape[0]/len(df)*100):.1f}% מהפעילות היומית</li>
                    <li><strong>ימי חול לעומת כל הימים:</strong> ימי חול מייצגים {(df[df['day_of_week'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])].shape[0]/len(df)*100):.1f}% מהמסלולים</li>
                </ul>
            </div>
        </div>

        <!-- RECOMMENDATIONS TAB -->
        <div id="recommendations" class="tab-content">
            <h2 style="margin-bottom: 30px; color: #667eea; font-size: 2em;">🎯 המלצות אסטרטגיות</h2>

            <div class="recommendation">
                <h3>🎯 אופטימיזציה תפעולית</h3>
                <ul>
                    <li><strong>איוש בשעות שיא:</strong> הקצה 30-40% יותר משאבים במהלך שעה {peak_hour}:00 כאשר הפעילות מגיעה לשיא של {(df[df['hour'] == peak_hour].shape[0]/len(df)*100):.1f}% מהנפח היומי</li>
                    <li><strong>איחוד מסלולים:</strong> התמקד באופטימיזציה של 20 המסלולים המובילים המייצגים {(df['routeid'].value_counts().head(20).sum()/len(df)*100):.1f}% מהפעילות להשפעה מקסימלית</li>
                    <li><strong>הקצאה מחדש של מכשירים:</strong> נתח דפוסי שימוש ב-{unique_devices} מכשירים לאיזון עומס (ממוצע נוכחי: {(total_routes/unique_devices):.1f} רשומות/מכשיר)</li>
                    <li><strong>ניהול קודי סטטוס:</strong> עקוב אחר סטטוס {most_common_status} שמהווה {(df['status'].value_counts().iloc[0]/len(df)*100):.1f}% מהמסלולים לבטחון איכות</li>
                    <li><strong>תכנון לפי יום בשבוע:</strong> הכן משאבים משופרים ליום {busiest_day} (היום העמוס ביותר) לטיפול בביקוש השיא</li>
                </ul>
            </div>

            <div class="recommendation">
                <h3>🌍 אסטרטגיה גיאוגרפית</h3>
                <ul>
                    <li><strong>מינוף המובילה:</strong> השתמש במודל המוצלח של עיר {most_active_city} ({(df[df['citysmbl'] == most_active_city].shape[0]/len(df)*100):.1f}% נתח שוק) כתבנית להרחבה</li>
                    <li><strong>חדירת שוק:</strong> 10 הערים המובילות מניעות {(df['citysmbl'].value_counts().head(10).sum()/len(df)*100):.1f}% מהנפח - שקול להעמיק שירותים כאן לפני הרחבה</li>
                    <li><strong>שווקים לא מספקים:</strong> זהה הזדמנויות צמיחה בערים מתחת לספירת מסלולים חציונית להרחבה</li>
                    <li><strong>קיבוץ אזורי:</strong> קבץ {unique_cities} ערים למרכזים אזוריים ליעילות תפעולית</li>
                    <li><strong>אופטימיזציה ברמת רחוב:</strong> נתח רחובות מובילים (כרגע במעקב {unique_streets}) לאופטימיזציית מיקרו-מסלולים</li>
                </ul>
            </div>

            <div class="recommendation">
                <h3>📈 יוזמות נתונים וניתוח</h3>
                <ul>
                    <li><strong>שיפור איכות נתונים:</strong> טפל ב-{len([col for col in df.columns if missing_pct[col] > 0])} עמודות עם ערכים חסרים לשיפור דיוק הניתוח מ-{data_completeness:.2f}% ל-100%</li>
                    <li><strong>לוחות בקרה בזמן אמת:</strong> פרוס ניטור חי לסטטוס מסלולים, ביצועי מכשירים וכיסוי גיאוגרפי</li>
                    <li><strong>ניתוח חיזוי:</strong> בנה מודלים של ML באמצעות {total_routes:,} רשומות היסטוריות לחיזוי ביקוש לפי שעה/יום/עיר</li>
                    <li><strong>מסגרת KPI:</strong> הקם מדדים ליעילות מסלולים (נוכחי: {avg_records_per_route:.2f} רשומות/מסלול), ניצול מכשירים וכיסוי ערים</li>
                    <li><strong>זיהוי חריגות:</strong> הטמע התראות לדפוסים חריגים בקודי סטטוס, תזמון או חריגות גיאוגרפיות</li>
                </ul>
            </div>

            <div class="recommendation">
                <h3>⚡ הישגים מהירים (פעולות ל-30 יום)</h3>
                <ul>
                    <li><strong>ניטור סטטוס:</strong> הגדר התראות אוטומטיות לקודי סטטוס לא סטנדרטיים (כרגע {df['status'].nunique()} סטטוסים ייחודיים)</li>
                    <li><strong>תגובה לשעת שיא:</strong> הגדל מיידית את קיבולת שעה {peak_hour} ב-{(df[df['hour'] == peak_hour].shape[0]/df['hour'].value_counts().mean() - 1)*100:.0f}% לעומת שעה ממוצעת</li>
                    <li><strong>ביקורת מסלולים:</strong> בדוק 20 מסלולים מובילים ({(df['routeid'].value_counts().head(20).sum()/len(df)*100):.1f}% מהנפח) להזדמנויות אופטימיזציה</li>
                    <li><strong>תחזוקת מכשירים:</strong> תזמן תחזוקה מונעת למכשירים עם השימוש הגבוה ביותר (10 המכשירים המובילים מטפלים בעומס משמעותי)</li>
                    <li><strong>מיקוד גיאוגרפי:</strong> פרוס משאבים נוספים לעיר {most_active_city} כדי לנצל את המנהיגות בשוק</li>
                </ul>
            </div>

            <div class="insight-card">
                <h3>🔮 הזדמנויות לניתוח עתידי</h3>
                <ul>
                    <li><strong>למידת מכונה:</strong> הטמע אלגוריתמי אופטימיזציית מסלולים באמצעות דפוסים היסטוריים מ-{(df['date'].max() - df['date'].min()).days} ימים של נתונים</li>
                    <li><strong>חיזוי סדרות זמן:</strong> חזה ביקוש עתידי על ידי ניתוח {df.groupby('date_only').size().count()} ימים של מגמות יומיות</li>
                    <li><strong>ניתוח אשכולות:</strong> פלח מסלולים לאשכולות תפעוליים המבוססים על {unique_cities} ערים, {unique_streets} רחובות ודפוסי שימוש</li>
                    <li><strong>מחזור חיי מכשירים:</strong> בנה מודלי תחזוקה חיזויים עבור {unique_devices} מכשירים על בסיס עוצמת שימוש</li>
                    <li><strong>פילוח לקוחות:</strong> נתח דפוסי כתובות כדי לזהות פלחי לקוחות וצרכי שירות</li>
                    <li><strong>אופטימיזציית רשת:</strong> השתמש בנתונים גיאוגרפיים (קו רוחב/אורך) לאופטימיזציה של נתיבי מסלולים והפחתת זמן נסיעה</li>
                    <li><strong>תכנון קיבולת:</strong> בנה מודל לצרכי קיבולת עתידיים באמצעות מגמות צמיחה נוכחיות ועונתיות</li>
                </ul>
            </div>

            <div class="stat-highlight">
                💡 <strong>פעולה בעדיפות:</strong> התמקד ב-20 המסלולים המובילים ובעיר {most_active_city} להשפעה מיידית - שילוב זה מייצג למעלה מ-{((df['routeid'].value_counts().head(20).sum() + df[df['citysmbl'] == most_active_city].shape[0])/len(df)/2*100):.0f}% מהטביעה התפעולית שלך!
            </div>
        </div>

        <div class="footer">
            <p>📊 לוח בקרה נוצר: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 📈 נקודות נתונים: {total_routes:,} | 🎯 מסלולים: {unique_routes} | 📱 מכשירים: {unique_devices} | 🌆 ערים: {unique_cities}</p>
            <p style="margin-top: 10px; opacity: 0.8;">מופעל על ידי Python, Pandas ו-Plotly | כל התצוגות החזותיות אינטראקטיביות - ריחוף, זום ותזוזה!</p>
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
