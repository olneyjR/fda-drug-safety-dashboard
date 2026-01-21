"""
FDA Drug Safety Dashboard
Adverse Event Monitoring & Risk Analysis
Live FDA API Connection
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.fda_api import FDAAPIClient

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="FDA Drug Safety Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Modern CSS styling (PRESERVED)
# -------------------------
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container with smoother gradient */
    .main {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    }
    
    /* Content width limiter */
    .main .block-container {
        max-width: 1400px;
        padding: 1rem 2rem 4rem 2rem;
    }
    
    /* Custom header with refined styling */
    .custom-header {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 2rem 3rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .custom-header h1 {
        color: white;
        font-size: 3.25rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1.5px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .custom-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.15rem;
        margin-top: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.2px;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #f1f5f9;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
        transform: scaleX(0);
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
        border-color: #dbeafe;
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
    }
    
    .metric-value {
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin: 0.5rem 0;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Refined section headers */
    .section-header {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #3b82f6;
        display: inline-block;
        letter-spacing: -0.5px;
    }
    
    .section-subheader {
        font-size: 1.125rem;
        font-weight: 400;
        color: #64748b;
        margin-bottom: 2rem;
        margin-top: 0.5rem;
        line-height: 1.6;
    }
    
    /* Sidebar with enhanced gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Enhanced info boxes */
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        padding: 2rem;
        border-radius: 16px;
        border-left: 5px solid #3b82f6;
        margin: 2rem 0;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
    }
    
    .info-box-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #1e40af;
        margin-bottom: 0.75rem;
        letter-spacing: 0.2px;
    }
    
    .info-box-text {
        color: #1e3a8a;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Alert boxes */
    .alert-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 5px solid #dc2626;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Plot containers */
    [data-testid="stPlotlyChart"] {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid #e5e7eb;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helpers
# -------------------------
RISK_LABEL_MAP = {
    "Minimal Data": "Minimal Risk (Limited Data)",
    "Low Risk": "Low Risk",
    "Moderate Risk": "Moderate Risk",
    "High Risk": "High Risk",
}

RISK_COLOR_MAP = {
    "Low Risk": "#10b981",
    "Minimal Risk (Limited Data)": "#3b82f6",
    "Moderate Risk": "#f59e0b",
    "High Risk": "#dc2626",
}


def normalize_risk_labels(df: pd.DataFrame, col: str = "risk_classification") -> pd.DataFrame:
    out = df.copy()
    out["risk_label"] = out[col].map(RISK_LABEL_MAP).fillna(out[col])
    return out


def donut_chart(df: pd.DataFrame, values: str, names: str, title: str, height: int = 400):
    fig = px.pie(df, values=values, names=names, hole=0.4, title=title)
    fig.update_layout(
        height=height,
        title_font=dict(size=18, family="Inter", color="#1f2937"),
        font=dict(family="Inter"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


# -------------------------
# Data loading with FDA API
# -------------------------
@st.cache_data(ttl=3600, show_spinner="Fetching live data from FDA API...")
def load_fda_data(record_limit: int = 5000):
    """
    Load data directly from FDA API
    Cache for 1 hour to avoid excessive API calls
    """
    client = FDAAPIClient()
    raw_df = client.fetch_adverse_events(limit=record_limit)
    transformed = client.transform_to_analytics(raw_df)
    return transformed


# Load data once
try:
    data = load_fda_data(record_limit=5000)
    events_df = data['events']
    drug_risk_df = data['drug_risk_profile']
except Exception as e:
    st.error(f"Failed to load FDA data: {e}")
    st.stop()


# -------------------------
# Derived analytics functions
# -------------------------
def load_overview_stats():
    stats = {
        'total_drugs': len(drug_risk_df),
        'total_events': drug_risk_df['total_adverse_events'].sum(),
        'serious_events': drug_risk_df['serious_events'].sum(),
        'deaths': drug_risk_df['death_reports'].sum(),
        'life_threatening': drug_risk_df['life_threatening_events'].sum(),
        'hospitalizations': drug_risk_df['hospitalization_events'].sum(),
        'avg_patient_age': drug_risk_df['avg_patient_age'].mean()
    }
    return pd.Series(stats)


def load_risk_distribution():
    return drug_risk_df.groupby('risk_classification').agg({
        'drug_name': 'count',
        'total_adverse_events': 'sum',
        'death_reports': 'sum'
    }).reset_index().rename(columns={'drug_name': 'drug_count', 'total_adverse_events': 'total_events', 'death_reports': 'deaths'})


def load_top_drugs(n=20):
    return drug_risk_df.nlargest(n, 'total_adverse_events')


def load_high_risk_drugs():
    high_risk = drug_risk_df[
        (drug_risk_df['death_reports'] > 0) & 
        (drug_risk_df['total_adverse_events'] >= 10)
    ].nlargest(15, 'fatality_rate')
    return high_risk


def load_age_analysis():
    age_df = events_df[events_df['patient_age_years'].notna()].copy()
    
    def age_group(age):
        if age < 18:
            return 'Pediatric (<18)'
        elif age < 45:
            return 'Young Adult (18-44)'
        elif age < 65:
            return 'Middle Age (45-64)'
        else:
            return 'Senior (65+)'
    
    age_df['age_group'] = age_df['patient_age_years'].apply(age_group)
    
    result = age_df.groupby('age_group').agg({
        'drug_name': 'count',
        'is_serious': 'sum',
        'is_death': 'sum',
        'patient_age_years': 'min'
    }).reset_index()
    
    result.columns = ['age_group', 'drug_count', 'total_events', 'deaths', 'min_age']
    result = result.sort_values('min_age')
    
    return result


def load_event_details():
    return events_df.groupby('patient_sex_name').agg({
        'safetyreportid': 'count',
        'is_serious': 'sum',
        'is_death': 'sum',
        'patient_age_years': 'mean'
    }).reset_index().rename(columns={
        'safetyreportid': 'event_count',
        'is_serious': 'serious_count',
        'is_death': 'death_count',
        'patient_sex_name': 'patient_sex',
        'patient_age_years': 'avg_age'
    })


def search_drug(drug_name: str):
    mask = drug_risk_df['drug_name'].str.contains(drug_name, case=False, na=False)
    return drug_risk_df[mask].sort_values('total_adverse_events', ascending=False)


# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown("## Navigation")
    view = st.radio(
        "Select View",
        ["Overview", "High Risk Drugs", "Top Drugs", "Demographics", "Drug Search"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Data Source")
    st.markdown(f"""
    **Live FDA API**  
    Records loaded: {len(events_df):,}  
    Drugs analyzed: {len(drug_risk_df):,}
    
    *Cached for 1 hour*
    """)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Real-time adverse drug event monitoring from FDA FAERS database.
    
    **Portfolio Project**
    - Jeffrey Olney
    - Live API Integration
    """)

# -------------------------
# Main content
# -------------------------
st.markdown("""
<div class="custom-header">
    <h1>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle; margin-right: 12px;">
            <path d="M10.5 2a2 2 0 0 1 2 0l7 4a2 2 0 0 1 1 1.73v8.54a2 2 0 0 1-1 1.73l-7 4a2 2 0 0 1-2 0l-7-4a2 2 0 0 1-1-1.73V7.73A2 2 0 0 1 3.5 6z"></path>
            <path d="M12 22v-7"></path>
            <path d="m3.27 6.96 8.23 4.76"></path>
            <path d="M21.73 6.96l-8.23 4.76"></path>
        </svg>
        FDA Drug Safety Dashboard
    </h1>
    <p>Live Monitoring of Adverse Drug Events • Real-Time FDA API</p>
</div>
""", unsafe_allow_html=True)

# OVERVIEW VIEW
if view == "Overview":
    stats = load_overview_stats()

    st.markdown('<div class="section-header">Platform Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Key metrics from FDA adverse event reporting system</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <path d="M10.5 2a2 2 0 0 1 2 0l7 4a2 2 0 0 1 1 1.73v8.54a2 2 0 0 1-1 1.73l-7 4a2 2 0 0 1-2 0l-7-4a2 2 0 0 1-1-1.73V7.73A2 2 0 0 1 3.5 6z"></path>
            </svg>
            <div class="metric-label">Drugs Monitored</div>
            <div class="metric-value">{int(stats['total_drugs']):,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            <div class="metric-label">Total Events</div>
            <div class="metric-value">{int(stats['total_events']):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <div class="metric-label">Serious Events</div>
            <div class="metric-value">{int(stats['serious_events']):,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            </svg>
            <div class="metric-label">Hospitalizations</div>
            <div class="metric-value">{int(stats['hospitalizations']):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <div class="metric-label">Life-Threatening</div>
            <div class="metric-value">{int(stats['life_threatening']):,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <path d="M12 2v20M2 12h20"></path>
            </svg>
            <div class="metric-label">Deaths Reported</div>
            <div class="metric-value">{int(stats['deaths']):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
            </svg>
            <div class="metric-label">Avg Patient Age</div>
            <div class="metric-value">{stats['avg_patient_age']:.1f}</div>
            <div class="metric-delta">years</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        fatality_pct = (int(stats["deaths"]) / int(stats["total_events"]) * 100) if int(stats["total_events"]) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            <div class="metric-label">Fatality Rate</div>
            <div class="metric-value">{fatality_pct:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size: 1.5rem;">Risk & Demographics Analysis</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### Risk Classification Distribution")
        risk_df = normalize_risk_labels(load_risk_distribution())

        fig = px.bar(
            risk_df,
            x="risk_label",
            y="drug_count",
            color="risk_label",
            color_discrete_map=RISK_COLOR_MAP,
            labels={"drug_count": "Number of Drugs", "risk_label": "Risk Level"},
        )
        fig.update_layout(
            showlegend=False, 
            height=400,
            title_font=dict(size=18, family="Inter", color="#1f2937"),
            font=dict(family="Inter"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Demographics by Sex")
        demo_df = load_event_details()

        fig = donut_chart(demo_df, values="event_count", names="patient_sex", title="", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size: 1.5rem;">Age Group Analysis</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Events by Age Group")
    age_df = load_age_analysis()

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        fig = px.bar(
            age_df,
            x="age_group",
            y="total_events",
            color="deaths",
            color_continuous_scale="Reds",
            labels={"total_events": "Total Events", "age_group": "Age Group", "deaths": "Deaths"},
        )
        fig.update_layout(
            height=300,
            font=dict(family="Inter"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(age_df, use_container_width=True, hide_index=True, height=300)

# HIGH RISK DRUGS VIEW
elif view == "High Risk Drugs":
    st.markdown('<div class="section-header">High Fatality Rate Drugs</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Drugs with highest percentage of fatal outcomes (minimum 10 events)</div>', unsafe_allow_html=True)

    high_risk_df = normalize_risk_labels(load_high_risk_drugs())

    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        fig = px.bar(
            high_risk_df.head(10),
            x="drug_name",
            y="fatality_rate",
            color="death_reports",
            color_continuous_scale="Reds",
            labels={"fatality_rate": "Fatality Rate (%)", "drug_name": "Drug", "death_reports": "Deaths"},
        )
        fig.update_layout(
            height=400, 
            xaxis_tickangle=-45,
            font=dict(family="Inter"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if len(high_risk_df) > 0:
            top_drug = high_risk_df.iloc[0]
            st.markdown(f"""
            <div class="alert-error">
                <strong>Highest Risk: {top_drug['drug_name']}</strong><br>
                Fatality Rate: {top_drug['fatality_rate']:.1f}%<br>
                Total Events: {int(top_drug['total_adverse_events']):,}<br>
                Deaths: {int(top_drug['death_reports']):,}
            </div>
            """, unsafe_allow_html=True)

        total_high_risk = len(high_risk_df[high_risk_df["fatality_rate"] > 10])
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Drugs >10% Fatality</div>
            <div class="metric-value">{total_high_risk}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Complete High Risk Drug List")

    st.dataframe(
        high_risk_df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "fatality_rate": st.column_config.NumberColumn("Fatality Rate", format="%.2f%%"),
            "total_adverse_events": st.column_config.NumberColumn("Total Events", format="%d"),
            "death_reports": st.column_config.NumberColumn("Deaths", format="%d"),
        },
    )

    csv = high_risk_df.to_csv(index=False)
    st.download_button("Export High Risk Drugs (CSV)", csv, "high_risk_drugs.csv", "text/csv")

# TOP DRUGS VIEW
elif view == "Top Drugs":
    st.markdown('<div class="section-header">Top 20 Drugs by Adverse Event Volume</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Most frequently reported adverse events in FAERS database</div>', unsafe_allow_html=True)

    top_drugs_df = normalize_risk_labels(load_top_drugs(20))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Events (Top 20)</div>
            <div class="metric-value">{int(top_drugs_df['total_adverse_events'].sum()):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Serious Events</div>
            <div class="metric-value">{int(top_drugs_df['serious_events'].sum()):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Deaths</div>
            <div class="metric-value">{int(top_drugs_df['death_reports'].sum()):,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        fig = px.scatter(
            top_drugs_df.head(15),
            x="total_adverse_events",
            y="serious_event_rate",
            size="death_reports",
            color="risk_label",
            hover_data=["drug_name"],
            labels={
                "total_adverse_events": "Total Adverse Events",
                "serious_event_rate": "Serious Event Rate (%)",
                "death_reports": "Deaths",
                "risk_label": "Risk Level",
            },
            color_discrete_map=RISK_COLOR_MAP,
        )
        fig.update_layout(
            height=500,
            font=dict(family="Inter"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
            yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Legend")
        st.markdown("**X-axis:** Total events")
        st.markdown("**Y-axis:** Serious percent")
        st.markdown("**Size:** Deaths")
        st.markdown("**Color:** Risk level")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Top 3 Drugs")
        for i in range(min(3, len(top_drugs_df))):
            drug = top_drugs_df.iloc[i]
            st.markdown(f"**{i+1}. {drug['drug_name']}**")
            st.caption(f"{int(drug['total_adverse_events']):,} events")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Detailed Drug Data")

    display_df = top_drugs_df[
        [
            "drug_name",
            "total_adverse_events",
            "serious_events",
            "death_reports",
            "serious_event_rate",
            "fatality_rate",
            "avg_patient_age",
            "risk_label",
        ]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "serious_event_rate": st.column_config.NumberColumn("Serious %", format="%.2f%%"),
            "fatality_rate": st.column_config.NumberColumn("Fatal %", format="%.2f%%"),
            "avg_patient_age": st.column_config.NumberColumn("Avg Age", format="%.1f"),
        },
    )

    csv = display_df.to_csv(index=False)
    st.download_button("Export Top Drugs (CSV)", csv, "top_drugs.csv", "text/csv")

# DEMOGRAPHICS VIEW
elif view == "Demographics":
    st.markdown('<div class="section-header">Patient Demographics Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Adverse events by patient characteristics</div>', unsafe_allow_html=True)

    demo_df = load_event_details()
    age_df = load_age_analysis()

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("#### Events by Sex")
        fig = px.bar(
            demo_df,
            x="patient_sex",
            y="event_count",
            color="death_count",
            color_continuous_scale="Reds",
            labels={"event_count": "Number of Events", "patient_sex": "Sex", "death_count": "Deaths"},
        )
        fig.update_layout(
            height=300,
            font=dict(family="Inter"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(demo_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Events by Age Group")

        fig = donut_chart(age_df, values="total_events", names="age_group", title="", height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(age_df, use_container_width=True, hide_index=True)

# DRUG SEARCH VIEW
elif view == "Drug Search":
    st.markdown('<div class="section-header">Drug Safety Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Search for specific drugs in the FAERS database</div>', unsafe_allow_html=True)
    
    search_term = st.text_input("Enter drug name (partial match supported)", placeholder="e.g., LIPITOR, HUMIRA")

    if search_term:
        results_df = normalize_risk_labels(search_drug(search_term))

        if len(results_df) > 0:
            st.markdown(f"""
            <div class="info-box">
                <div class="info-box-title">Search Results</div>
                <div class="info-box-text">
                Found {len(results_df)} drug(s) matching '{search_term}'
                </div>
            </div>
            """, unsafe_allow_html=True)

            for idx, drug in results_df.iterrows():
                title = f"{drug['drug_name']} - {drug['risk_label']}"
                with st.expander(title, expanded=(idx == 0)):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Total Events</div>
                            <div class="metric-value">{int(drug['total_adverse_events']):,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Serious Events</div>
                            <div class="metric-value">{int(drug['serious_events']):,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Deaths</div>
                            <div class="metric-value">{int(drug['death_reports']):,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col4:
                        avg_age_display = f"{drug['avg_patient_age']:.1f}" if pd.notna(drug["avg_patient_age"]) else "N/A"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Avg Age</div>
                            <div class="metric-value">{avg_age_display}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    col1, col2 = st.columns(2, gap="large")
                    with col1:
                        st.markdown("**Safety Metrics**")
                        st.markdown(f"Serious Event Rate: **{drug['serious_event_rate']:.2f}%**")
                        st.markdown(f"Fatality Rate: **{drug['fatality_rate']:.2f}%**")
                        st.markdown(f"Severity Score: **{drug['avg_severity_score']:.2f}** / 5.0")

                        if pd.notna(drug["fatality_rate"]):
                            if drug["fatality_rate"] > 10:
                                st.markdown('<div class="alert-error">High fatality rate detected</div>', unsafe_allow_html=True)
                            elif drug["fatality_rate"] > 5:
                                st.markdown('<div class="alert-warning">Elevated fatality rate</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown("**Event Details**")
                        st.markdown(f"Life-Threatening: **{int(drug['life_threatening_events']):,}**")
                        st.markdown(f"Hospitalizations: **{int(drug['hospitalization_events']):,}**")
                        st.markdown(f"Risk Classification: **{drug['risk_label']}**")

                    if pd.notna(drug["common_indications"]) and drug["common_indications"]:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("**Common Indications**")
                        indications = drug["common_indications"].split("|")[:5]
                        for indication in indications:
                            st.markdown(f"- {indication.strip()}")
        else:
            st.markdown(f"""
            <div class="alert-warning">
                No drugs found matching '{search_term}'
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
            <div class="info-box-title">How to Search</div>
            <div class="info-box-text">
            Enter a drug name above to search. Partial matches are supported (e.g., "LIP" will find "LIPITOR").
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    <div class="info-box-text" style="text-align: center;">
    FDA Drug Safety Dashboard | Live API Integration | Portfolio Project by Jeffrey Olney
    </div>
</div>
""", unsafe_allow_html=True)