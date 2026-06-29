import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="TradeNode.ai", layout="wide", page_icon="⚓", initial_sidebar_state="expanded")

# ================== 1. REPLIT CSS THEME ==================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0A0A0B; }
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stSidebar"] { background-color: #111214; border-right: 1px solid #1F1F22; }
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; max-width: 1800px; }
    
    /* KPI Card */
    .kpi-card {
        background-color: #111214; border: 1px solid #1F1F22;
        padding: 20px; border-radius: 12px; height: 100%;
    }
    .kpi-label { font-size: 0.75rem; color: #A0A0A5; text-transform: uppercase; letter-spacing: 0.5px; display:flex; align-items:center; gap:8px;}
    .kpi-value { font-size: 2.5rem; font-weight: 900; color: #FFFFFF; line-height: 1.2; }
    .kpi-sub { font-size: 0.85rem; color: #A0A0A5; }
    
    /* News Ticker */
    .news-ticker {
        background: #111214; border: 1px solid #EF4444; border-radius: 8px;
        padding: 10px 16px; overflow: hidden; white-space: nowrap;
    }
    .news-ticker span {
        display: inline-block; padding-left: 100%;
        animation: ticker 40s linear infinite; color: #FCA5A5; font-weight: 600;
    }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); }

    /* Chokepoint Card */
    .cp-card { background:#111214; border:1px solid #1F1F22; padding:12px 16px; border-radius:8px; margin-bottom:8px; }
    .cp-score { float:right; color:white; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ================== 2. SIDEBAR NAV ==================
with st.sidebar:
    st.markdown("### ⚓ TRADENODE.AI")
    st.caption("Global Trade Risk OS")
    st.markdown("---")
    page = st.radio("NAV", ["📈 Dashboard", "🌐 Global Map", "🚢 Vessels", "🛡️ Sanctions", "⛽ Fuel"], label_visibility="collapsed")

# ================== 3. DEMO DATA GENERATOR - NO API NEEDED ==================
@st.cache_data
def load_demo_data():
    np.random.seed(42)
    # 1. KPI Data
    kpis = {"alerts": 14, "sanc": 4, "risk": 77.0, "assets": 12}
    
    # 2. Risk Bar Chart Data
    risk_df = pd.DataFrame({
        "Category": ["Geopolitical", "Blockage", "Drought", "Piracy", "Conflict", "Sanctions", "Weather"],
        "Risk": [100, 78, 55, 82, 100, 62, 64]
    })

    # 3. Chokepoint List
    chokepoints = [
        {"name": "Strait of Hormuz", "lat": 26.6, "lon": 56.3, "type": "Geopolitical", "score": 100, "vessels": 3},
        {"name": "Suez Canal", "lat": 30.0, "lon": 32.5, "type": "Blockage", "score": 78, "vessels": 2},
        {"name": "Panama Canal", "lat": 9.1, "lon": -79.7, "type": "Drought", "score": 55, "vessels": 0},
        {"name": "Strait of Malacca", "lat": 1.2, "lon": 103.4, "type": "Piracy", "score": 81, "vessels": 2},
        {"name": "Bab el-Mandeb", "lat": 12.6, "lon": 43.3, "type": "Conflict", "score": 92, "vessels": 5},
    ]
    
    # 4. Map Vessel Data - 50 fake ships
    vessel_data = []
    for cp in chokepoints:
        for i in range(random.randint(3, 8)):
            vessel_data.append({
                "lat": cp["lat"] + np.random.uniform(-0.5, 0.5),
                "lon": cp["lon"] + np.random.uniform(-0.5, 0.5),
                "name": f"MV DEMO-{random.randint(100,999)}",
                "imo": f"IMO{random.randint(1000000,9999)}",
                "sanctioned": random.random() > 0.85, # 15% sanctioned
                "type": random.choice(["Tanker", "Container", "Bulk"])
            })
    vessels_df = pd.DataFrame(vessel_data)
    vessels_df["color"] = vessels_df["sanctioned"].apply(lambda x: [239, 68, 68, 200] if x else [59, 130, 246, 200]) # Red vs Blue

    # 5. News Ticker Data
    news_headlines = [
        "BREAKING: Houthi activity reported near Bab el-Mandeb",
        "ALERT: Suez Canal delays up 18% due to inspection backlog",
        "SANCTION: 2 new tankers flagged by OFAC in Hormuz region",
        "WEATHER: Typhoon warning issued for Strait of Malacca",
        "RISK: Panama Canal draft restrictions extended to Oct 2026"
    ]

    # 6. Fuel Cost Line Chart
    dates = pd.date_range(end=datetime.today(), periods=30)
    fuel_df = pd.DataFrame({"Date": dates, "Cost": np.cumsum(np.random.randn(30) * 20 + 600)})

    return kpis, risk_df, chokepoints, vessels_df, news_headlines, fuel_df

kpis, risk_df, chokepoints, vessels_df, news_headlines, fuel_df = load_demo_data()

# ================== 4. NEWS TICKER BAR - TOP OF PAGE ==================
st.markdown(f'<div class="news-ticker"><span>{" 🔴 ".join(news_headlines)} 🔴 </span></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ================== 5. DASHBOARD PAGE ==================
if page == "📈 Dashboard":
    col1, col2 = st.columns([4,1])
    with col1:
        st.markdown("### Global Trade Risk OS")
        st.caption("Real-time monitoring of maritime chokepoints and systemic threats")
    with col2:
        st.markdown("<p style='text-align: right; color:#3B82F6; font-weight:600;'>● LIVE DEMO</p>", unsafe_allow_html=True)

    # 4 KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">📈 CRITICAL ALERTS</div><div class="kpi-value">{kpis["alerts"]}</div><div class="kpi-sub">Active geopolitical events</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">🛡️ SANCTIONED VESSELS</div><div class="kpi-value">{kpis["sanc"]}</div><div class="kpi-sub">Under active monitoring</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">🌐 GLOBAL RISK INDEX</div><div class="kpi-value">{kpis["risk"]}</div><div class="kpi-sub">Average across all chokepoints</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">📍 TRACKED ASSETS</div><div class="kpi-value">{kpis["assets"]}</div><div class="kpi-sub">Vessels in operational range</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2 Column Layout: Graph + Chokepoints
    left, right = st.columns([2,1])
    with left:
        st.markdown("#### SYSTEMIC RISK BY CATEGORY")
        fig = px.bar(risk_df, x="Category", y="Risk", color="Risk", color_continuous_scale=["#F97316", "#EF4444"], range_y=[0,100])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='#111214', font_color="#A0A0A5", margin=dict(l=0, r=0, t=20, b=0), height=350, showlegend=False)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#1F1F22")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### BUNKER PRICE 30D TREND [DEMO]")
        fig2 = px.line(fuel_df, x="Date", y="Cost", markers=True)
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='#111214', font_color="#A0A0A5", margin=dict(l=0, r=0, t=20, b=0), height=250, yaxis_title="$/ton MGO")
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        st.markdown("#### CRITICAL CHOKEPOINTS")
        for cp in chokepoints:
            color = "#EF4444" if cp["score"] > 80 else "#F97316" if cp["score"] > 50 else "#22C55E"
            st.markdown(f'<div class="cp-card"><b>{cp["name"]}</b><span class="cp-score" style="background:{color};">{cp["score"]}/100</span><br><span style="color:#A0A0A5; font-size:0.85rem;">⚠️ {cp["type"]}</span><div style="color:#A0A0A5; font-size:0.85rem;">{cp["vessels"]} vessels</div></div>', unsafe_allow_html=True)

# ================== 6. GLOBAL MAP PAGE ==================
elif page == "🌐 Global Map":
    st.markdown("### Global Vessel & Risk Map [DEMO DATA]")
    fig_map = px.scatter_mapbox(vessels_df, lat="lat", lon="lon", hover_name="name", hover_data=["imo", "type", "sanctioned"],
                                color="sanctioned", color_discrete_map={True: "red", False: "blue"}, zoom=2, height=700)
    fig_map.update_layout(mapbox_style="carto-dark", mapbox_accesstoken=None, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='#0A0A0B')
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("Red = Sanctioned. Blue = Normal. All data is synthetic for demo.")

# ================== 7. VESSELS TABLE PAGE ==================
elif page == "🚢 Vessels":
    st.markdown("### Live Vessel Feed [DEMO]")
    st.dataframe(vessels_df[["name", "imo", "type", "lat", "lon", "sanctioned"]], use_container_width=True, height=600)

# ================== 8. SANCTIONS PAGE ==================
elif page == "🛡️ Sanctions":
    st.markdown("### Sanctioned Vessels Detected [DEMO]")
    sanc_df = vessels_df[vessels_df["sanctioned"] == True]
    if not sanc_df.empty:
        st.error(f"🔴 {len(sanc_df)} Sanctioned Vessel(s) in Current View")
        st.dataframe(sanc_df[["name", "imo", "lat", "lon"]])
    else:
        st.success("🟢 No sanctioned vessels detected in current view")

# ================== 9. FUEL PAGE ==================
elif page == "⛽ Fuel":
    st.markdown("### Route Fuel Cost Estimator [DEMO MATH]")
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox("Origin", ["Dubai", "Singapore", "Rotterdam"])
        distance = st.slider("Distance (Nautical Miles)", 100, 10000, 1200)
    with col2:
        vessel_type = st.selectbox("Vessel Type", ["Tanker", "Container", "Bulk"])
        bunker_price = st.number_input("Bunker Price $/ton", 400, 1000, 620)
    
    rates = {"Tanker": 85, "Container": 120, "Bulk": 70}
    cost = distance * rates.get(vessel_type, 85) * (bunker_price / 1000)
    st.metric("Estimated Bunker Cost", f"${cost:,.0f}")
    st.caption("Demo calculation. Replace with BunkerEx API for live prices.")
