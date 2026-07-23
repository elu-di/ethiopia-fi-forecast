"""
Ethiopia Financial Inclusion Forecasting Dashboard
Selam Analytics — Interactive Stakeholder Dashboard
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from src.data_loader import DataLoader
from src.impact_model import ImpactModel
from src.forecaster import InclusionForecaster

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Forecast | Selam Analytics",
    page_icon="🇪🇹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLING ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0f1117; }

.metric-card {
    background: linear-gradient(135deg, #1a1d2e 0%, #16213e 100%);
    border: 1px solid #2d3561;
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    margin: 4px;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform: translateY(-3px); border-color: #4f8ef7; }
.metric-value { font-size: 2.2rem; font-weight: 700; color: #4f8ef7; margin: 4px 0; }
.metric-label { font-size: 0.82rem; color: #8892b0; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-delta { font-size: 0.9rem; color: #64ffda; font-weight: 500; }
.metric-delta.negative { color: #ff6b6b; }

.section-header {
    font-size: 1.5rem; font-weight: 700;
    color: #ccd6f6; margin: 16px 0 8px 0;
    border-left: 4px solid #4f8ef7; padding-left: 12px;
}
.insight-box {
    background: linear-gradient(135deg, #1a1d2e 0%, #16213e 100%);
    border-left: 4px solid #64ffda; border-radius: 8px;
    padding: 14px 18px; margin: 8px 0; color: #ccd6f6;
}
.crossover-banner {
    background: linear-gradient(90deg, #1a472a 0%, #2d3561 100%);
    border: 1px solid #64ffda; border-radius: 12px;
    padding: 16px 24px; margin: 12px 0;
    text-align: center; color: #64ffda;
    font-size: 1.1rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    loader = DataLoader()
    df_joined = loader.get_joined_impact_links()
    impact_model = ImpactModel(df_joined)
    forecaster = InclusionForecaster(impact_model)

    access_hist = loader.get_findex_access_history()
    fit_access = forecaster.fit_trend(access_hist)
    access_fc = forecaster.forecast_all_scenarios(fit_access, 'ACC_OWNERSHIP', [2025, 2026, 2027])

    digital_pts = pd.DataFrame({
        'observation_date': pd.to_datetime(['2014-12-31','2017-12-31','2021-12-31','2024-11-29']),
        'value_numeric': [1.3, 5.0, 12.7, 35.0],
        'year': [2014, 2017, 2021, 2024]
    })
    fit_usage = forecaster.fit_trend(digital_pts, date_col='observation_date')
    usage_fc = forecaster.forecast_all_scenarios(fit_usage, 'USG_DIGITAL_PAYMENT', [2025, 2026, 2027])

    return loader, impact_model, access_fc, usage_fc, access_hist, digital_pts

loader, impact_model, access_fc, usage_fc, access_hist, digital_pts = load_all_data()

FINDEX_ACCESS = [(2011,14),(2014,22),(2017,35),(2021,46),(2024,49)]
FINDEX_USAGE = [(2014,1.3),(2017,5.0),(2021,12.7),(2024,35.0)]

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇪🇹 Selam Analytics")
    st.markdown("**Ethiopia FI Forecast System**")
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Overview",
        "📈 Historical Trends",
        "🔗 Event Impact Matrix",
        "🔮 2025–2027 Projections"
    ])
    st.markdown("---")
    scenario = st.selectbox("Default Scenario", ["base", "optimistic", "pessimistic"],
                             format_func=lambda x: {"base":"📊 Base","optimistic":"🚀 Optimistic","pessimistic":"⚠️ Pessimistic"}[x])
    st.markdown("---")
    st.markdown("**Data Sources**")
    st.caption("World Bank Global Findex 2011–2024\nEthio Telecom / Telebirr\nSafaricom Ethiopia / M-Pesa\nNational Bank of Ethiopia\nEthSwitch S.C.\nGSMA, ITU, IMF FAS")

# ─── OVERVIEW PAGE ──────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.markdown("# 🇪🇹 Ethiopia Financial Inclusion Dashboard")
    st.markdown("*Forecasting Ethiopia's digital financial transformation — Access & Usage 2025–2027*")

    # P2P/ATM crossover banner
    st.markdown("""<div class="crossover-banner">
        🎉 Historic Milestone: P2P Digital Transfers Surpassed ATM Cash Withdrawals in October 2024
        &nbsp;|&nbsp; P2P/ATM Ratio: <strong>1.08×</strong>
    </div>""", unsafe_allow_html=True)

    # Key Metric Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("Account Ownership", "49%", "+3pp since 2021", False),
        ("Telebirr Users", "54.8M", "+12% YoY (est.)", False),
        ("M-Pesa Users", "10.8M", "65.7% 90-day active", False),
        ("P2P Transactions", "128.3M", "vs 119.3M ATM", False),
        ("Digital Payments", "~35%", "of adults 15+", False),
    ]
    for col, (label, value, delta, neg) in zip([col1,col2,col3,col4,col5], metrics):
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-delta {'negative' if neg else ''}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Consortium Questions
    col_q, col_fc = st.columns([1, 1])
    with col_q:
        st.markdown('<div class="section-header">Consortium Key Questions</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight-box">
        <b>Q1: What drives financial inclusion in Ethiopia?</b><br>
        Infrastructure (4G: 37%→71%), Digital ID (Fayda: 8M→15M enrolled), mobile agent density, 
        and Telebirr's network effects are the primary drivers. Affordable data (2% GNI) 
        and smartphone penetration (42%) are key enablers.
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="insight-box">
        <b>Q2: How do events affect inclusion?</b><br>
        Telebirr launch (May 2021) contributed ~+15pp to account ownership trajectory. 
        M-Pesa entry (Aug 2023) added ~+5pp to mobile money accounts. 
        Fayda Digital ID is projected to add +10pp to access over 24 months.
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="insight-box">
        <b>Q3: 2025 rates and 2026–2027 outlook?</b><br>
        Base forecast: Access reaches <b>~57% by 2025</b>, ~64.5% by 2027 (NFIS-II target: 60% ✅). 
        Usage reaches <b>~41% by 2025</b>, ~48% by 2027 — approaching access rates 
        due to Ethiopia's P2P-dominant payment culture and EthSwitch interoperability.
        </div>""", unsafe_allow_html=True)

    with col_fc:
        st.markdown('<div class="section-header">2027 Base Forecast at a Glance</div>', unsafe_allow_html=True)
        base_acc_2027 = access_fc[(access_fc['scenario']=='base')&(access_fc['year']==2027)].iloc[0]
        base_usg_2027 = usage_fc[(usage_fc['scenario']=='base')&(usage_fc['year']==2027)].iloc[0]

        fig_gauge = make_subplots(rows=1, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}]],
            subplot_titles=["Access 2027 (Base)", "Usage 2027 (Base)"])

        for col_idx, (val, target, label) in enumerate([
            (base_acc_2027['forecast_final'], 60, "Account Ownership"),
            (base_usg_2027['forecast_final'], 55, "Digital Payments")
        ], 1):
            fig_gauge.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=val,
                delta={'reference': target, 'suffix': 'pp vs target', 'font': {'size': 12}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "#4f8ef7", 'thickness': 0.25},
                    'bgcolor': "#1a1d2e",
                    'bordercolor': "#2d3561",
                    'steps': [
                        {'range': [0, 40], 'color': '#1a1d2e'},
                        {'range': [40, 60], 'color': '#16213e'},
                        {'range': [60, 100], 'color': '#0f3460'}
                    ],
                    'threshold': {'line': {'color': '#FF9800', 'width': 3}, 'value': target}
                },
                number={'suffix': '%', 'font': {'size': 28}},
                title={'text': label, 'font': {'size': 13}}
            ), row=1, col=col_idx)

        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=280, font_color='#ccd6f6',
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("🟡 Orange needle = NFIS-II policy target")


# ─── HISTORICAL TRENDS PAGE ──────────────────────────────────────────────────
elif page == "📈 Historical Trends":
    st.markdown("# 📈 Historical Trends & Enablers")

    tab1, tab2, tab3 = st.tabs(["📊 Access & Usage", "📡 Enabler Infrastructure", "💹 Mobile Money Operators"])

    with tab1:
        col_y1, col_y2 = st.columns(2)
        with col_y1:
            year_start = st.slider("Start Year", 2011, 2023, 2011, key="trend_start")
        with col_y2:
            year_end = st.slider("End Year", 2012, 2024, 2024, key="trend_end")

        fig_trend = go.Figure()
        acc_x = [y for y,v in FINDEX_ACCESS if year_start <= y <= year_end]
        acc_y = [v for y,v in FINDEX_ACCESS if year_start <= y <= year_end]
        usg_x = [y for y,v in FINDEX_USAGE if year_start <= y <= year_end]
        usg_y = [v for y,v in FINDEX_USAGE if year_start <= y <= year_end]

        fig_trend.add_trace(go.Scatter(x=acc_x, y=acc_y, mode='lines+markers', name='Account Ownership (Access)',
            line=dict(color='#4f8ef7', width=3), marker=dict(size=9)))
        fig_trend.add_trace(go.Scatter(x=usg_x, y=usg_y, mode='lines+markers', name='Digital Payments (Usage)',
            line=dict(color='#64ffda', width=3, dash='dash'), marker=dict(size=9)))
        fig_trend.add_trace(go.Scatter(x=[2014,2021,2024], y=[4.7,4.7,9.45], mode='lines+markers',
            name='Mobile Money Accounts', line=dict(color='#FF9800', width=2, dash='dot'), marker=dict(size=8)))

        # Annotate key events
        for evt_yr, evt_label in [(2021,'Telebirr\nLaunch'),(2022,'Safaricom\nEntry'),(2023,'M-Pesa\nLaunch')]:
            if year_start <= evt_yr <= year_end:
                fig_trend.add_vline(x=evt_yr, line_dash='dot', line_color='rgba(255,152,0,0.5)', line_width=1.5)
                fig_trend.add_annotation(x=evt_yr, y=75, text=evt_label, showarrow=False,
                    font=dict(size=9, color='#FF9800'), bgcolor='rgba(0,0,0,0.6)', borderpad=3)

        fig_trend.update_layout(
            title='Ethiopia Financial Inclusion Trajectory (Global Findex Survey Data)',
            xaxis_title='Year', yaxis_title='% of Adults (15+)',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
            font_color='#ccd6f6', legend=dict(bgcolor='rgba(0,0,0,0.4)'),
            yaxis=dict(range=[0, 80], gridcolor='rgba(255,255,255,0.08)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            height=420
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("#### 📉 Why Did Growth Slow? The 2021–2024 Puzzle")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""<div class="insight-box">
            <b>65M+ mobile money accounts opened, yet account ownership only grew +3pp</b><br><br>
            Key explanations:<br>
            • <b>Survey definition gap</b>: Findex asks about personal account usage in last 12 months — 
            many Telebirr users registered but weren't "active users" by survey date<br>
            • <b>Double-counting</b>: Users hold both bank + mobile money accounts<br>
            • <b>Inactivity</b>: Ethiopia's mobile money active rate is ~66% (good by global standards 
            but leaves 34% registered-only)<br>
            • <b>Semi-formal use</b>: P2P transfers used as commerce proxies — not captured as "digital payment"
            </div>""", unsafe_allow_html=True)
        with col_b:
            # Gender gap chart
            fig_gender = go.Figure()
            fig_gender.add_trace(go.Bar(x=['2021','2024'], y=[53, 58], name='Male', marker_color='#4f8ef7'))
            fig_gender.add_trace(go.Bar(x=['2021','2024'], y=[33, 40], name='Female', marker_color='#ff6b9d'))
            fig_gender.add_trace(go.Bar(x=['2021','2024'], y=[20, 18], name='Gender Gap (pp)', marker_color='rgba(255,152,0,0.5)'))
            fig_gender.update_layout(
                title='Account Ownership by Gender (%)', barmode='group',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
                font_color='#ccd6f6', height=280,
                yaxis=dict(title='% of Adults', gridcolor='rgba(255,255,255,0.08)'),
                legend=dict(bgcolor='rgba(0,0,0,0.4)')
            )
            st.plotly_chart(fig_gender, use_container_width=True)

    with tab2:
        infra_data = {
            'Indicator': ['4G Coverage', 'Mobile Penetration', 'Smartphone %', 'Agent Density\n(per 10k adults)',
                         'ATM Density\n(per 100k)', 'Electricity Access', 'Fayda Digital ID\n(millions enrolled)'],
            '2023': [37, 55, 35, 9, 3.5, 48, 0],
            '2024': [45, 65, 42, 12.5, 4.2, 55, 8],
            '2025': [71, 61, 50, 16, 5.0, 60, 15]
        }
        df_infra = pd.DataFrame(infra_data).melt(id_vars='Indicator', var_name='Year', value_name='Value')

        fig_infra = px.bar(df_infra, x='Indicator', y='Value', color='Year', barmode='group',
            color_discrete_map={'2023':'#374785', '2024':'#4f8ef7', '2025':'#64ffda'},
            title='Infrastructure & Enabler Indicators (2023–2025)')
        fig_infra.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
            font_color='#ccd6f6', height=420, xaxis_tickangle=-20,
            legend=dict(bgcolor='rgba(0,0,0,0.4)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.08)')
        )
        st.plotly_chart(fig_infra, use_container_width=True)

    with tab3:
        fig_ops = go.Figure()
        fig_ops.add_trace(go.Bar(x=['Telebirr\n(Jun 2025)', 'M-Pesa\n(Dec 2024)', 'Bank Accounts\n(2024 est.)'],
            y=[54.84, 10.8, 42.0], marker_color=['#4f8ef7','#FF9800','#64ffda'],
            text=['54.84M', '10.8M', '~42M'], textposition='outside'))
        fig_ops.add_trace(go.Bar(x=['Telebirr\n(Jun 2025)', 'M-Pesa\n(Dec 2024)', 'Bank Accounts\n(2024 est.)'],
            y=[np.nan, 7.1, np.nan], name='90-day Active (M-Pesa)',
            marker_color='rgba(255,152,0,0.4)', text=['','7.1M',''], textposition='outside'))

        fig_ops.update_layout(
            title='Ethiopia Digital Finance Operator Landscape', barmode='overlay',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
            font_color='#ccd6f6', height=380,
            yaxis=dict(title='Users (Millions)', gridcolor='rgba(255,255,255,0.08)'),
            xaxis=dict(title='Platform')
        )
        st.plotly_chart(fig_ops, use_container_width=True)

        col_p2p, col_atm = st.columns(2)
        with col_p2p:
            fig_cross = go.Figure(go.Indicator(
                mode="number+delta",
                value=1.08,
                title={'text': "P2P / ATM Ratio (Jul 2025)"},
                delta={'reference': 0.83, 'relative': False, 'valueformat': '.2f',
                       'increasing': {'color': '#64ffda'}},
                number={'suffix': 'x', 'font': {'size': 44, 'color': '#64ffda'}}
            ))
            fig_cross.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, font_color='#ccd6f6')
            st.plotly_chart(fig_cross, use_container_width=True)
        with col_atm:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(x=['P2P Count\n(128.3M)','ATM Count\n(119.3M)'],
                y=[128.3, 119.3], marker_color=['#64ffda','#ff6b6b']))
            fig_vol.update_layout(
                title='P2P vs ATM Transactions (Jul 2025)',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
                font_color='#ccd6f6', height=200,
                yaxis=dict(title='Millions', gridcolor='rgba(255,255,255,0.08)'),
                margin=dict(t=30, b=10)
            )
            st.plotly_chart(fig_vol, use_container_width=True)


# ─── EVENT IMPACT MATRIX PAGE ────────────────────────────────────────────────
elif page == "🔗 Event Impact Matrix":
    st.markdown("# 🔗 Event-Indicator Impact Matrix")
    st.markdown("*How do policies, product launches, and infrastructure investments affect financial inclusion?*")

    df_joined = loader.get_joined_impact_links()
    assoc_matrix = impact_model.get_association_matrix()

    indicator_cols = [c for c in assoc_matrix.columns
                      if c not in ['parent_id', 'event_name', 'category_final']]
    pivot_data = assoc_matrix[indicator_cols].fillna(0.0)

    # Label the index
    idx_reset = assoc_matrix.reset_index()
    y_labels = [f"{r['parent_id']}: {r['event_name'][:35]}" for _, r in idx_reset.iterrows()]

    fig_heat = go.Figure(go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns.tolist(),
        y=y_labels,
        colorscale='RdYlGn',
        zmid=0,
        text=np.round(pivot_data.values, 1),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title='Impact<br>(pp/unit)', tickfont=dict(color='#ccd6f6'))
    ))
    fig_heat.update_layout(
        title='Event-Indicator Association Matrix (Net Estimated Impact)',
        xaxis=dict(title='Target Indicator', tickangle=-30, tickfont=dict(color='#ccd6f6')),
        yaxis=dict(title='Event', tickfont=dict(size=10, color='#ccd6f6')),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.8)',
        font_color='#ccd6f6', height=520, margin=dict(l=280, r=20, t=50, b=100)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("#### 📉 Temporal Impact Realization Curves")
    st.markdown("*How quickly does an event's effect materialize?*")
    months_range = np.linspace(-2, 30, 200)

    fig_curves = go.Figure()
    for lag, col, name in [(6,'#64ffda','Short Lag (6 months)'),(12,'#4f8ef7','Medium Lag (12 months)'),(24,'#FF9800','Long Lag (24 months)')]:
        curve = [ImpactModel.calculate_temporal_factor(m, lag, 'logistic') * 15 for m in months_range]
        fig_curves.add_trace(go.Scatter(x=months_range, y=curve, mode='lines', name=name,
            line=dict(color=col, width=2.5)))

    fig_curves.add_vline(x=0, line_dash='dot', line_color='rgba(255,255,255,0.3)', annotation_text='Event Launch')
    fig_curves.update_layout(
        title='Logistic S-Curve: Impact Realization by Lag Period (max impact = 15pp)',
        xaxis_title='Months Since Event Launch', yaxis_title='Realized Impact (pp)',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
        font_color='#ccd6f6', height=320,
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)'),
        legend=dict(bgcolor='rgba(0,0,0,0.4)')
    )
    st.plotly_chart(fig_curves, use_container_width=True)

    # Event timeline
    st.markdown("#### 📅 Ethiopia Digital Finance Event Timeline")
    events_data = [
        (2021.38, 'Telebirr Launch', 'product_launch', '#4f8ef7'),
        (2021.67, 'NFIS-II Launch', 'policy', '#FF9800'),
        (2022.58, 'Safaricom Ethiopia Entry', 'market_entry', '#64ffda'),
        (2023.58, 'M-Pesa Launch', 'product_launch', '#4f8ef7'),
        (2024.0,  'Fayda Digital ID Rollout', 'infrastructure', '#ff6b6b'),
        (2024.57, 'FX Liberalization', 'policy', '#FF9800'),
        (2024.75, 'P2P > ATM Crossover', 'milestone', '#64ffda'),
        (2025.04, 'Digital ID Expansion', 'policy', '#FF9800'),
        (2025.17, 'Telebirr Merchant Expansion', 'product_launch', '#4f8ef7'),
        (2025.42, 'EthSwitch Full Interoperability', 'infrastructure', '#ff6b6b'),
        (2025.67, 'Rural Agent Expansion', 'infrastructure', '#ff6b6b'),
        (2025.84, 'MM Regulation Update', 'policy', '#FF9800'),
        (2025.96, 'EthioPay Launch', 'infrastructure', '#ff6b6b'),
    ]
    fig_timeline = go.Figure()
    cat_y = {'product_launch': 0.3, 'policy': 0.6, 'market_entry': 0.9, 'infrastructure': 0.0, 'milestone': 1.2}

    for yr, name, cat, col in events_data:
        y_pos = cat_y.get(cat, 0.5)
        fig_timeline.add_trace(go.Scatter(
            x=[yr], y=[y_pos], mode='markers+text',
            marker=dict(size=14, color=col, symbol='diamond', line=dict(color='white', width=1.5)),
            text=[name], textposition='top center', textfont=dict(size=8.5, color='#ccd6f6'),
            name=cat, showlegend=False
        ))
        fig_timeline.add_shape(type='line', x0=yr, x1=yr, y0=-0.1, y1=y_pos,
            line=dict(color=col, width=1, dash='dot'))

    for cat, y_pos, label in [('infrastructure',0.0,'Infrastructure'), ('product_launch',0.3,'Product Launch'),
                                ('policy',0.6,'Policy'), ('market_entry',0.9,'Market Entry'), ('milestone',1.2,'Milestone')]:
        fig_timeline.add_annotation(x=2020.6, y=y_pos, text=label, showarrow=False,
            font=dict(size=9, color='rgba(200,200,200,0.6)'), xanchor='left')

    fig_timeline.update_layout(
        title='Ethiopia Digital Finance Events Timeline (2021–2026)',
        xaxis=dict(title='Year', range=[2020.5, 2026.5], gridcolor='rgba(255,255,255,0.06)'),
        yaxis=dict(showticklabels=False, range=[-0.15, 1.5]),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
        font_color='#ccd6f6', height=400
    )
    st.plotly_chart(fig_timeline, use_container_width=True)


# ─── PROJECTIONS PAGE ────────────────────────────────────────────────────────
elif page == "🔮 2025–2027 Projections":
    st.markdown("# 🔮 Ethiopia Financial Inclusion Projections: 2025–2027")

    col_sc, col_ci = st.columns([2, 1])
    with col_sc:
        selected_scenarios = st.multiselect("Show Scenarios", ['base','optimistic','pessimistic'],
            default=['base','optimistic','pessimistic'],
            format_func=lambda x: {'base':'📊 Base','optimistic':'🚀 Optimistic','pessimistic':'⚠️ Pessimistic'}[x])
    with col_ci:
        show_ci = st.checkbox("Show Confidence Intervals", value=True)

    SCENARIO_COLORS = {'base':'#4f8ef7', 'optimistic':'#64ffda', 'pessimistic':'#ff6b6b'}
    NFIS_TARGETS = [(2025, 55), (2027, 60)]

    fig_proj = make_subplots(rows=1, cols=2, subplot_titles=[
        "Access: Account Ownership Rate (%)", "Usage: Digital Payment Adoption (%)"
    ])

    for col_idx, (fc_df, hist_pts, title) in enumerate([
        (access_fc, FINDEX_ACCESS, "Access"), (usage_fc, FINDEX_USAGE, "Usage")
    ], 1):
        hist_x = [y for y,v in hist_pts]
        hist_y = [v for y,v in hist_pts]
        fig_proj.add_trace(go.Scatter(x=hist_x, y=hist_y, mode='lines+markers', name='Historical',
            line=dict(color='white', width=2.5), marker=dict(size=8),
            showlegend=(col_idx == 1)), row=1, col=col_idx)

        for sc in selected_scenarios:
            df_sc = fc_df[fc_df['scenario']==sc]
            conn_x = [hist_x[-1]] + df_sc['year'].tolist()
            conn_y = [hist_y[-1]] + df_sc['forecast_final'].tolist()
            col = SCENARIO_COLORS[sc]

            fig_proj.add_trace(go.Scatter(x=conn_x, y=conn_y, mode='lines+markers',
                name=sc.capitalize(), line=dict(color=col, width=2.5, dash='dash'),
                marker=dict(size=8), showlegend=(col_idx == 1),
                legendgroup=sc), row=1, col=col_idx)

            if show_ci:
                ci_x = [hist_x[-1]] + df_sc['year'].tolist() + df_sc['year'].tolist()[::-1]
                ci_y = ([hist_y[-1]] + df_sc['ci_upper'].tolist() +
                        df_sc['ci_lower'].tolist()[::-1])
                fig_proj.add_trace(go.Scatter(x=ci_x, y=ci_y, fill='toself', mode='none',
                    fillcolor=col.replace('#','rgba(').rstrip(')')+'0.12)',
                    line=dict(width=0), showlegend=False, legendgroup=sc), row=1, col=col_idx)

        if col_idx == 1:
            for yr, target in NFIS_TARGETS:
                fig_proj.add_trace(go.Scatter(x=[2021, yr], y=[target, target], mode='lines',
                    line=dict(color='#FF9800', dash='dot', width=1.5),
                    name=f'NFIS-II Target ({yr})', showlegend=True), row=1, col=1)
                fig_proj.add_annotation(x=yr, y=target+2, text=f'{target}%', font=dict(size=9, color='#FF9800'),
                    showarrow=False, row=1, col=1)

    fig_proj.update_layout(
        height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
        font_color='#ccd6f6',
        legend=dict(bgcolor='rgba(0,0,0,0.5)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1),
        yaxis=dict(title='% of Adults (15+)', range=[0,80], gridcolor='rgba(255,255,255,0.07)'),
        yaxis2=dict(range=[0,80], gridcolor='rgba(255,255,255,0.07)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        xaxis2=dict(gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_proj, use_container_width=True)

    # Forecast Table
    st.markdown("#### 📋 Full Forecast Summary Table")
    col_acc_t, col_usg_t = st.columns(2)
    for col, (fc_df, label) in zip([col_acc_t, col_usg_t],
        [(access_fc,'Access (Account Ownership %)'),(usage_fc,'Usage (Digital Payments %)')]):
        with col:
            st.markdown(f"**{label}**")
            tbl = fc_df[fc_df['scenario'].isin(selected_scenarios)][
                ['year','scenario','forecast_final','ci_lower','ci_upper','event_impact_pp']
            ].round(1).rename(columns={
                'year':'Year', 'scenario':'Scenario', 'forecast_final':'Forecast %',
                'ci_lower':'CI Lower', 'ci_upper':'CI Upper', 'event_impact_pp':'Event Impact (pp)'
            })
            st.dataframe(tbl, hide_index=True, use_container_width=True)

    # Download button
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_acc = access_fc.to_csv(index=False).encode()
        st.download_button("⬇️ Download Access Forecast CSV", csv_acc,
            "ethiopia_access_forecast.csv", "text/csv")
    with col_dl2:
        csv_usg = usage_fc.to_csv(index=False).encode()
        st.download_button("⬇️ Download Usage Forecast CSV", csv_usg,
            "ethiopia_usage_forecast.csv", "text/csv")

    # Event impacts
    st.markdown("#### 🎯 Projected Event Impacts on Access by 2027")
    impact_2027 = impact_model.compute_cumulative_impact('ACC_OWNERSHIP', pd.to_datetime('2027-12-31'))
    if impact_2027['event_breakdown']:
        breakdown = pd.DataFrame([{'Event': k, 'Impact (pp)': v}
                                   for k, v in impact_2027['event_breakdown'].items()])
        breakdown = breakdown.sort_values('Impact (pp)', ascending=False)
        fig_impact = px.bar(breakdown, x='Impact (pp)', y='Event', orientation='h',
            color='Impact (pp)', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
        fig_impact.update_layout(
            title=f"Cumulative Event Impact on Access by 2027 (Total: {impact_2027['total_impact_pp']:+.1f}pp)",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,46,0.5)',
            font_color='#ccd6f6', height=380, showlegend=False,
            xaxis=dict(gridcolor='rgba(255,255,255,0.07)', title='Percentage Points Added'),
            yaxis=dict(title='')
        )
        st.plotly_chart(fig_impact, use_container_width=True)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#8892b0'>Selam Analytics © 2025 | Data: World Bank Global Findex, "
    "NBE, Ethio Telecom, Safaricom Ethiopia, EthSwitch | Model: OLS Trend + Event-Augmented Logistic Intervention</small>",
    unsafe_allow_html=True
)
