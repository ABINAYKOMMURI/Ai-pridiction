"""
Smart Multi-Category Price Trend Analysis and Future Forecast Dashboard
═══════════════════════════════════════════════════════════════════════════
Flask Backend — Routes, Data Processing, Chart Generation
Uses: Pandas, NumPy, Plotly, Matplotlib
Formula: Future Price = Current Price × (1 + Growth Rate)^Years
         Growth Rate  = (Current Price − Previous Price) / Previous Price
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# ─── App Config ───────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'smart_price_dashboard_dav_project_2025'

DATASET_PATH = os.path.join('dataset', 'price_data.csv')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('dataset', exist_ok=True)

CATEGORIES = [
    'Mobiles', 'Laptops', 'Grocery', 'Fuel', 'Gold', 'Silver',
    'Electronics', 'Home Appliances', 'Clothing', 'Fruits and Vegetables',
    'Medicine', 'Computer Components', 'Travel Tickets', 'Vehicles', 'Books'
]

# ─── Plotly Chart Styling ─────────────────────────────────────────────────
CHART_TEMPLATE = 'plotly_dark'
CHART_BG       = 'rgba(0,0,0,0)'
CHART_PAPER    = 'rgba(0,0,0,0)'
CHART_FONT     = dict(color='#e8edf5', family='Inter, sans-serif')
COLOR_PREV     = '#4e73df'
COLOR_CURR     = '#1cc88a'
COLOR_FUTURE   = '#f6c23e'


def chart_layout(**kwargs):
    """Common Plotly layout settings."""
    base = dict(
        template=CHART_TEMPLATE,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_PAPER,
        font=CHART_FONT,
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(26,45,77,0.5)',
            borderwidth=1,
            font=dict(size=11)
        )
    )
    base.update(kwargs)
    return base


def to_json(fig):
    """Convert Plotly figure to JSON string."""
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


# ─── Data Loader ──────────────────────────────────────────────────────────
def load_data():

    print("\nLOADING DATA...")

    if not os.path.exists(DATASET_PATH):

        print("CSV NOT FOUND")
        print(DATASET_PATH)

        return pd.DataFrame()

    try:

        df = pd.read_csv(
            DATASET_PATH
        )

        print("CSV LOADED")

        print(
            "ROWS:",
            len(df)
        )

        print(
            df.columns
        )

        required_cols = [

            'Date',

            'Category',

            'Product_Name',

            'Brand',

            'Location',

            'Previous_Price',

            'Current_Price'

        ]

        missing = [

            col

            for col in required_cols

            if col not in df.columns

        ]

        if missing:

            print(
                "MISSING:",
                missing
            )

            return pd.DataFrame()

        df = df.drop_duplicates()

        df['Date'] = pd.to_datetime(

            df['Date'],

            errors='coerce'

        )

        df['Previous_Price'] = pd.to_numeric(

            df['Previous_Price'],

            errors='coerce'

        )

        df['Current_Price'] = pd.to_numeric(

            df['Current_Price'],

            errors='coerce'

        )

        df = df.dropna(

            subset=[

                'Date',

                'Previous_Price',

                'Current_Price'

            ]

        )

        df = df[

            df['Previous_Price'] > 0

        ]

        df['Growth_Rate'] = (

            (

                df['Current_Price']

                -

                df['Previous_Price']

            )

            /

            df['Previous_Price']

        )

        df['Growth_Rate'] = np.clip(

            df['Growth_Rate'],

            -0.25,

            0.35

        )

        years = 3

        df['Future_Price'] = (

            df['Current_Price']

            *

            (

                1+

                df['Growth_Rate']

            )**years

        )

        q1 = df[

            'Current_Price'

        ].quantile(
            0.01
        )

        q99 = df[

            'Current_Price'

        ].quantile(
            0.99
        )

        df = df[

            (

                df['Current_Price']

                >=

                q1

            )

            &

            (

                df['Current_Price']

                <=

                q99

            )

        ]

        df = df.sort_values(

            'Date'

        )

        df = df.reset_index(

            drop=True

        )

        print()

        print(
            "FINAL ROWS"
        )

        print(
            len(df)
        )

        print()

        print(
            "DATA CHECK"
        )

        print(
            df.head()
        )

        print()

        print(
            "GROWTH RANGE"
        )

        print(

            df[
                'Growth_Rate'
            ]

            .describe()

        )

        return df

    except Exception as e:

        print()

        print(
            "LOAD ERROR"
        )

        print(e)

        return pd.DataFrame()
# ═══════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════

# ─── Home Page ────────────────────────────────────────────────────────────
@app.route('/')
def home():
    df = load_data()
    stats = {}

    if not df.empty:
        stats = {
            'total_products':  len(df),
            'total_categories': df['Category'].nunique(),
            'total_brands':     df['Brand'].nunique(),
            'avg_growth_rate':  round(df['Growth_Rate'].mean() * 100, 2),
            'total_locations':  df['Location'].nunique(),
            'avg_price':        round(df['Current_Price'].mean(), 2),
        }

    return render_template('index.html', stats=stats)


# ─── About Page ──────────────────────────────────────────────────────────
@app.route('/about')
def about():
    return render_template('about.html')


# ─── Upload Page ──────────────────────────────────────────────────────────
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        # ── CSV File Upload ───────────────────────────────────────────
        if 'csv_file' in request.files:
            file = request.files['csv_file']
            if file.filename and file.filename.endswith('.csv'):
                try:
                    uploaded_df = pd.read_csv(file)
                    if os.path.exists(DATASET_PATH):
                        existing_df = pd.read_csv(DATASET_PATH)
                        combined = pd.concat([existing_df, uploaded_df], ignore_index=True)
                    else:
                        combined = uploaded_df
                    combined.to_csv(DATASET_PATH, index=False)
                    flash(f'CSV uploaded successfully! {len(uploaded_df)} rows added.', 'success')
                except Exception as e:
                    flash(f'Error processing CSV: {str(e)}', 'error')
                return redirect(url_for('upload'))

        # ── Manual Form Entry ─────────────────────────────────────────
        try:
            product_name   = request.form.get('product_name', '').strip()
            category       = request.form.get('category', '').strip()
            brand          = request.form.get('brand', '').strip()
            previous_price = float(request.form.get('previous_price', 0))
            current_price  = float(request.form.get('current_price', 0))
            location       = request.form.get('location', '').strip()
            date           = request.form.get('date', '')
            discount       = float(request.form.get('discount', 0))
            quantity       = int(request.form.get('quantity', 1))

            if previous_price <= 0:
                flash('Previous price must be greater than 0.', 'error')
                return redirect(url_for('upload'))

            growth_rate  = (current_price - previous_price) / previous_price
            future_price = current_price * (1 + growth_rate) ** 3

            new_row = pd.DataFrame([{
                'Product_Name':   product_name,
                'Category':       category,
                'Brand':          brand,
                'Previous_Price': round(previous_price, 2),
                'Current_Price':  round(current_price, 2),
                'Growth_Rate':    round(growth_rate, 4),
                'Future_Price':   round(future_price, 2),
                'Date':           date,
                'Location':       location,
                'Discount':       discount,
                'Quantity':        quantity,
            }])

            if os.path.exists(DATASET_PATH):
                existing_df = pd.read_csv(DATASET_PATH)
                combined = pd.concat([existing_df, new_row], ignore_index=True)
            else:
                combined = new_row
            combined.to_csv(DATASET_PATH, index=False)

            flash(f'"{product_name}" added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding data: {str(e)}', 'error')

        return redirect(url_for('upload'))

    return render_template('upload.html', categories=CATEGORIES)

# ─── Dashboard Page ──────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():

    df = load_data()

    print("\nDATA CHECK")
    print(df.head())

    print("\nROWS:")
    print(len(df))

    if df.empty:
        flash(
            'No data available. Please upload data first.',
            'error'
        )

        return render_template(
            'dashboard.html',
            kpi={},
            charts={}
        )
    # ── KPI Calculations ──────────────────────────────────────────────
    highest_idx = df['Growth_Rate'].idxmax()
    lowest_idx  = df['Growth_Rate'].idxmin()

    kpi = {
        'total_products':     f"{len(df):,}",
        'avg_prev_price':     f"₹{df['Previous_Price'].mean():,.2f}",
        'avg_curr_price':     f"₹{df['Current_Price'].mean():,.2f}",
        'avg_future_price':   f"₹{df['Future_Price'].mean():,.2f}",
        'highest_growth':     df.loc[highest_idx, 'Product_Name'],
        'highest_growth_rate': f"{df['Growth_Rate'].max() * 100:+.2f}%",
        'lowest_growth':      df.loc[lowest_idx, 'Product_Name'],
        'lowest_growth_rate':  f"{df['Growth_Rate'].min() * 100:+.2f}%",
    }

    charts = {}

    # ── 1. Bar Chart: Category-wise Previous vs Current vs Future ─────
    cat_avg = df.groupby('Category').agg({
        'Previous_Price': 'mean',
        'Current_Price':  'mean',
        'Future_Price':   'mean',
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Previous Price', x=cat_avg['Category'], y=cat_avg['Previous_Price'], marker_color=COLOR_PREV))
    fig.add_trace(go.Bar(name='Current Price',  x=cat_avg['Category'], y=cat_avg['Current_Price'],  marker_color=COLOR_CURR))
    fig.add_trace(go.Bar(name='Future Price',   x=cat_avg['Category'], y=cat_avg['Future_Price'],   marker_color=COLOR_FUTURE))
    fig.update_layout(**chart_layout(
        barmode='group',
        title='📊 Category-wise Price Comparison (Avg)',
        xaxis_tickangle=-45,
        height=520,
        margin=dict(b=130)
    ))
    charts['bar'] = to_json(fig)

    # ── 2. Line Chart: Price Trend Over Time ──────────────────────────
    monthly = df.set_index('Date').resample('ME').agg({
        'Previous_Price': 'mean',
        'Current_Price':  'mean',
        'Future_Price':   'mean',
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly['Date'], y=monthly['Previous_Price'], name='Previous Price',
                             line=dict(color=COLOR_PREV, width=2.5), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=monthly['Date'], y=monthly['Current_Price'],  name='Current Price',
                             line=dict(color=COLOR_CURR, width=2.5), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=monthly['Date'], y=monthly['Future_Price'],   name='Future Price',
                             line=dict(color=COLOR_FUTURE, width=2.5), mode='lines+markers', marker=dict(size=5)))
    fig.update_layout(**chart_layout(title='📈 Price Trend Over Time (Monthly Avg)', height=460))
    charts['line'] = to_json(fig)

    # ── 3. Pie Chart: Category Distribution ───────────────────────────
    cat_count = df['Category'].value_counts().reset_index()
    cat_count.columns = ['Category', 'Count']

    fig = px.pie(cat_count, values='Count', names='Category',
                 title='🥧 Category Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3,
                 hole=0.35)
    fig.update_layout(**chart_layout(height=460))
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11)
    charts['pie'] = to_json(fig)

    # ── 4. Histogram: Price Distribution ──────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df['Current_Price'], nbinsx=50, name='Current Price',
                               marker_color=COLOR_CURR, opacity=0.75))
    fig.add_trace(go.Histogram(x=df['Previous_Price'], nbinsx=50, name='Previous Price',
                               marker_color=COLOR_PREV, opacity=0.6))
    fig.update_layout(**chart_layout(
        title='📊 Price Distribution', barmode='overlay', height=460
    ))
    charts['histogram'] = to_json(fig)

    # ── 5. Scatter: Growth Rate vs Future Price ───────────────────────
    sample_df = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(sample_df, x='Growth_Rate', y='Future_Price', color='Category',
                     title='🔬 Growth Rate vs Future Price',
                     opacity=0.65, color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(**chart_layout(height=460))
    charts['scatter'] = to_json(fig)

    # ── 6. Brand-wise Analysis ────────────────────────────────────────
    brand_avg = df.groupby('Brand')['Current_Price'].mean().nlargest(15).reset_index()
    fig = px.bar(brand_avg, x='Brand', y='Current_Price',
                 title='🏷️ Top 15 Brands — Average Current Price',
                 color='Current_Price', color_continuous_scale='Viridis')
    fig.update_layout(**chart_layout(height=460, xaxis_tickangle=-45))
    fig.update_coloraxes(showscale=False)
    charts['brand'] = to_json(fig)

    # ── 7. Location-wise Analysis ─────────────────────────────────────
    loc_avg = df.groupby('Location').agg({
        'Current_Price': 'mean',
        'Growth_Rate':   'mean',
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Avg Current Price', x=loc_avg['Location'], y=loc_avg['Current_Price'],
                         marker_color=COLOR_CURR, marker_line=dict(width=0)))
    fig.update_layout(**chart_layout(title='📍 Location-wise Average Price', height=460))
    charts['location'] = to_json(fig)

    # ── 8. Gold vs Silver Trend ───────────────────────────────────────
    # ── 8. Gold vs Silver Trend ──

    precious = df[
        df['Category'].isin(
            ['Gold','Silver']
        )
    ].copy()

    precious['Date']=pd.to_datetime(
        precious['Date'],
        errors='coerce'
    )

    precious=precious.dropna(
        subset=['Date']
    )

    if not precious.empty:

        precious_q = precious.set_index(
            'Date'
        ).groupby(
            'Category'
        ).resample(
            'QE-DEC'
        )[
            'Current_Price'
        ].mean().reset_index()

        fig = px.line(
            precious_q,
            x='Date',
            y='Current_Price',
            color='Category',
            title='Gold vs Silver Quarterly Price Trend',
            markers=True
        )

        fig.update_layout(
            **chart_layout(
                height=460
            )
        )

        fig.update_traces(
            line_width=3,
            marker_size=7
        )

        charts['gold_silver']=to_json(fig)

    # ── 9. Fuel Trend Analysis ────────────────────────────────────────
    fuel = df[df['Category'] == 'Fuel'].copy()
    fuel['Date'] = pd.to_datetime(fuel['Date'], errors='coerce')
    fuel = fuel.dropna(subset=['Date'])
    
    if not fuel.empty:
        fuel_q = fuel.set_index('Date').groupby('Product_Name').resample('QE-DEC')['Current_Price'].mean().reset_index()
        fig = px.line(fuel_q, x='Date', y='Current_Price', color='Product_Name',
                      title='⛽ Fuel Price Trend Analysis (Quarterly)', markers=True)
        fig.update_layout(**chart_layout(height=460))
        fig.update_traces(line_width=2.5, marker_size=6)
        charts['fuel'] = to_json(fig)

    # ── 10. Mobile Price Trend ────────────────────────────────────────
    mobiles = df[df['Category'] == 'Mobiles'].copy()
    if not mobiles.empty:
        mob_brand = mobiles.groupby('Brand').agg({
            'Previous_Price': 'mean',
            'Current_Price':  'mean',
            'Future_Price':   'mean',
        }).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Previous', x=mob_brand['Brand'], y=mob_brand['Previous_Price'], marker_color=COLOR_PREV))
        fig.add_trace(go.Bar(name='Current',  x=mob_brand['Brand'], y=mob_brand['Current_Price'],  marker_color=COLOR_CURR))
        fig.add_trace(go.Bar(name='Future',   x=mob_brand['Brand'], y=mob_brand['Future_Price'],   marker_color=COLOR_FUTURE))
        fig.update_layout(**chart_layout(
            barmode='group', title='📱 Mobile Price Trend by Brand', height=460
        ))
        charts['mobile'] = to_json(fig)

    # ── 11. Discount Distribution ─────────────────────────────────────
    fig = px.histogram(df, x='Discount', nbins=30,
                       title='🏷️ Discount Distribution',
                       color_discrete_sequence=[COLOR_FUTURE])
    fig.update_layout(**chart_layout(height=460))
    charts['discount'] = to_json(fig)

    print("\nKPI DATA")
    print(kpi)

    print("\nCHARTS GENERATED")
    print(charts.keys())

    return render_template(
        'dashboard.html',
        kpi=kpi,
        charts=charts
    )


# ─── Results Page ─────────────────────────────────────────────────────────
@app.route('/results')
def results():
    df = load_data()

    if df.empty:
        flash('No data available. Please upload data first.', 'error')
        return render_template('results.html', results={}, summary={},
                               matplotlib_charts={}, cat_analysis='')

    # ── Category-wise Growth ──────────────────────────────────────────
    cat_growth = df.groupby('Category')['Growth_Rate'].mean()

    results_data = {
        'highest_growth_category':      cat_growth.idxmax(),
        'highest_growth_category_rate': round(cat_growth.max() * 100, 2),
        'lowest_growth_category':       cat_growth.idxmin(),
        'lowest_growth_category_rate':  round(cat_growth.min() * 100, 2),
        'avg_growth_rate':              round(df['Growth_Rate'].mean() * 100, 2),
        'price_increase_pct':           round((df['Growth_Rate'] > 0).sum() / len(df) * 100, 2),
        'price_decline_pct':            round((df['Growth_Rate'] < 0).sum() / len(df) * 100, 2),
        'top_growing_product':          df.loc[df['Growth_Rate'].idxmax(), 'Product_Name'],
        'top_growing_product_rate':     round(df['Growth_Rate'].max() * 100, 2),
        'top_declining_product':        df.loc[df['Growth_Rate'].idxmin(), 'Product_Name'],
        'top_declining_product_rate':   round(df['Growth_Rate'].min() * 100, 2),
    }

    # ── Summary Statistics (NumPy + Pandas) ───────────────────────────
    summary = {}
    for col in ['Previous_Price', 'Current_Price', 'Future_Price', 'Growth_Rate', 'Discount']:
        summary[col] = {
            'mean':   round(float(np.mean(df[col])), 2),
            'median': round(float(np.median(df[col])), 2),
            'max':    round(float(np.max(df[col])), 2),
            'min':    round(float(np.min(df[col])), 2),
            'std':    round(float(np.std(df[col])), 2),
        }

    # ── Matplotlib Charts ─────────────────────────────────────────────
    matplotlib_charts = {}
    mpl_bg = '#0a1628'
    mpl_fg = '#e8edf5'

    # Chart 1: Category-wise Growth Rate (horizontal bar)
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(mpl_bg)
    ax.set_facecolor(mpl_bg)

    sorted_growth = cat_growth.sort_values(ascending=True)
    colors_arr = ['#e74a3b' if v < 0 else '#1cc88a' for v in sorted_growth.values]
    ax.barh(sorted_growth.index, sorted_growth.values * 100, color=colors_arr, height=0.6, edgecolor='none')
    ax.set_xlabel('Growth Rate (%)', color=mpl_fg, fontsize=12, fontfamily='sans-serif')
    ax.set_title('Category-wise Average Growth Rate', color=mpl_fg, fontsize=15, fontweight='bold', pad=15)
    ax.tick_params(colors=mpl_fg, labelsize=10)
    ax.spines['bottom'].set_color('#1a2d4d')
    ax.spines['left'].set_color('#1a2d4d')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.axvline(x=0, color='#1a2d4d', linewidth=1, linestyle='--')
    for i, (val, name) in enumerate(zip(sorted_growth.values * 100, sorted_growth.index)):
        ax.text(val + (0.3 if val >= 0 else -0.3), i, f'{val:.1f}%',
                va='center', ha='left' if val >= 0 else 'right',
                color=mpl_fg, fontsize=9, fontweight='bold')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor=mpl_bg)
    buf.seek(0)
    matplotlib_charts['category_growth'] = base64.b64encode(buf.getvalue()).decode()
    plt.close(fig)

    # Chart 2: Top 10 Products by Growth Rate
    top10 = df.nlargest(10, 'Growth_Rate')[['Product_Name', 'Growth_Rate']].copy()
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    fig2.patch.set_facecolor(mpl_bg)
    ax2.set_facecolor(mpl_bg)
    c2 = plt.cm.plasma(np.linspace(0.25, 0.85, len(top10)))
    ax2.barh(top10['Product_Name'], top10['Growth_Rate'] * 100, color=c2, height=0.6)
    ax2.set_xlabel('Growth Rate (%)', color=mpl_fg, fontsize=12)
    ax2.set_title('Top 10 Products by Growth Rate', color=mpl_fg, fontsize=15, fontweight='bold', pad=15)
    ax2.tick_params(colors=mpl_fg, labelsize=10)
    ax2.spines['bottom'].set_color('#1a2d4d')
    ax2.spines['left'].set_color('#1a2d4d')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    for i, val in enumerate(top10['Growth_Rate'] * 100):
        ax2.text(val + 0.5, i, f'{val:.1f}%', va='center', color=mpl_fg, fontsize=9, fontweight='bold')
    plt.tight_layout()
    buf2 = BytesIO()
    fig2.savefig(buf2, format='png', dpi=120, bbox_inches='tight', facecolor=mpl_bg)
    buf2.seek(0)
    matplotlib_charts['top_products'] = base64.b64encode(buf2.getvalue()).decode()
    plt.close(fig2)

    # ── Category Analysis Table ───────────────────────────────────────
    cat_analysis = df.groupby('Category').agg({
        'Previous_Price': 'mean',
        'Current_Price':  'mean',
        'Future_Price':   'mean',
        'Growth_Rate':    'mean',
        'Discount':       'mean',
        'Product_Name':   'count',
    }).round(2).reset_index()
    cat_analysis.columns = ['Category', 'Avg Previous ₹', 'Avg Current ₹', 'Avg Future ₹',
                             'Avg Growth Rate', 'Avg Discount %', 'Total Products']
    cat_analysis['Avg Growth Rate'] = (cat_analysis['Avg Growth Rate'] * 100).round(2).astype(str) + '%'
    cat_analysis_html = cat_analysis.to_html(
        classes='table table-dark table-striped table-hover table-dark-custom',
        index=False, border=0
    )

    return render_template('results.html',
                           results=results_data,
                           summary=summary,
                           matplotlib_charts=matplotlib_charts,
                           cat_analysis=cat_analysis_html)


# ═══════════════════════════════════════════════════════════════════════════
from flask import jsonify


@app.route('/api/stats')
def api_stats():

    df = load_data()

    if df.empty:

        return jsonify({
            "overview": {},
            "summary_statistics": {}
        })

    cat_growth = (
        df.groupby('Category')
        ['Growth_Rate']
        .mean()
    )

    top = df.loc[
        df['Growth_Rate']
        .idxmax()
    ]

    summary = {}

    cols = [

        'Previous_Price',

        'Current_Price',

        'Growth_Rate',

        'Future_Price'

    ]

    for col in cols:

        summary[col]={

            "mean":
            float(df[col].mean()),

            "median":
            float(df[col].median()),

            "max":
            float(df[col].max()),

            "min":
            float(df[col].min()),

            "std_dev":
            float(df[col].std())

        }

    output = {

        "overview": {

            "highest_growth_category":

            cat_growth.idxmax(),

            "highest_growth_rate":

            round(
            cat_growth.max()*100,
            2
            ),

            "lowest_growth_category":

            cat_growth.idxmin(),

            "lowest_growth_rate":

            round(
            cat_growth.min()*100,
            2
            ),

            "avg_growth_rate":

            round(
            df['Growth_Rate']
            .mean()*100,
            2
            ),

            "increase_pct":

            round(
            (
            df['Growth_Rate']>0
            ).mean()*100,
            2
            ),

            "decline_pct":

            round(
            (
            df['Growth_Rate']<0
            ).mean()*100,
            2
            ),

            "top_product":{

                "name":

                top['Product_Name'],

                "brand":

                top['Brand'],

                "category":

                top['Category'],

                "growth":

                float(
                top['Growth_Rate']
                *100
                ),

                "location":

                top['Location']

            }

        },

        "summary_statistics":

        summary

    }

    return jsonify(output)


@app.route(
'/api/matplotlib_chart'
)

def api_mpl():

    fig,ax=plt.subplots(
    figsize=(8,5)
    )

    df=load_data()

    growth=(
    df.groupby(
    'Category'
    )[
    'Growth_Rate'
    ].mean()*100
    )

    growth.plot(
    kind='bar',
    ax=ax
    )

    ax.set_title(
    "Category Growth"
    )

    ax.set_ylabel(
    "Growth %"
    )

    buf=BytesIO()

    plt.savefig(
    buf,
    format='png'
    )

    buf.seek(0)

    img=base64.b64encode(
    buf.getvalue()
    ).decode()

    plt.close()

    return jsonify({

    "image":

    "data:image/png;base64,"+img

    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
