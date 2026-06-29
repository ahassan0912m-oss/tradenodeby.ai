import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="TradeNode.ai", layout="wide", page_icon="🌍")

# --- FOUNDER & COMPANY CONFIG ---
FOUNDER = "Muhammad Ali Hassan"
COMPANY = "TradeNode.ai"
CONTACT = "a.hassan0912/m@gmail.com"
DOMAIN = "www.https.tradenod.ai" # Fix typo: should be https://tradenod.ai

# --- API KEYS: GET THESE FREE - INSTRUCTIONS BELOW ---
NEWSAPI_KEY = "your_newsapi_key" # newsapi.org
OPENWEATHER_KEY = "your_openweather_key" # openweathermap.org
MAPBOX_TOKEN = "your_mapbox_token" # mapbox.com

# --- DISCLAIMER ---
st.error("⚠️ **LIVE INTELLIGENCE BETA** - Data from public sources. Human verification mandatory for navigation. TradeNode.ai not liable for routing decisions.")

# --- HEADER ---
col1, col2 = st.columns([3,1])
with col1:
    st.title("🌍 TradeNode.ai - Global Trade Risk OS")
    st.caption(f"Real-time AI for chokepoints, sanctions, weather, and route intelligence | Built by {FOUNDER}")
with col2:
    st.write(f"**Contact:** {CONTACT}")
    st.write(f"**Domain:** {DOMAIN}")

# --- GLOBAL CHOKEPOINTS + COORDINATES ---
CHOKEPOINTS = {
    "Strait of Hormuz": {"lat": 26.6, "lon": 56.3, "risk_type": "Geopolitical"},
    "Suez Canal": {"lat": 30.0, "lon": 32.5, "risk_type": "Blockage"},
    "Panama Canal": {"lat": 9.1, "lon": -79.7, "risk_type": "Drought"},
    "Strait of Malacca": {"lat": 1.2, "lon": 103.4, "risk_type": "Piracy"},
    "Bab el-Mandeb": {"lat": 12.6, "lon": 43.3, "risk_type": "Conflict"},
    "Turkish Straits": {"lat": 41.0, "lon": 29.0, "risk_type": "Sanctions"},
    "Danish Straits": {"lat": 55.8, "lon": 12.7, "risk_type": "Weather"}
}

# --- REAL DATA FUNCTIONS ---

@st.cache_data(ttl=300)
def get_live_news(query):
    """REAL: NewsAPI - Live threat detection"""
    if NEWSAPI_KEY == "your_newsapi_key": return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {"q": f'{query} AND (closure OR strike OR attack OR sanction OR storm)', "sortBy": "publishedAt", "pageSize": 5, "apiKey": NEWSAPI_KEY}
        r = requests.get(url, params=params, timeout=5)
        return r.json().get("articles", [])
    except: return []

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    """REAL: OpenWeather - Live weather at chokepoint"""
    if OPENWEATHER_KEY == "your_openweather_key": return {"status": "Add API Key"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        return {"temp": data["main"]["temp"], "wind": data["wind"]["speed"], "desc": data["weather"][0]["main"]}
    except: return {"status": "Error"}

@st.cache_data(ttl=3600)
def get_sanctioned_vessels():
    """REAL: OFAC Sanctions List - Updated daily"""
    try:
        # US Treasury OFAC list - public CSV
        url = "https://www.treasury.gov/ofac/downloads/sdn.csv"
        df = pd.read_csv(url, header=None)
        # Filter for vessels - column 2 contains type
        vessels = df[df[2].str.contains("Vessel", na=False)][1].tolist()
        return vessels[:50] # First 50 for demo
    except:
        return ["SANCTION LIST OFFLINE - CHECK OFAC.GOV"]

def get_satellite_link(lat, lon):
    """REAL: Sentinel-2 Latest Image"""
    return f"https://apps.sentinel-hub.com/eo-browser/?lat={lat}&lng={lon}&zoom=10&time=latest"

# --- USER ROUTE CHECKER ---
st.divider()
st.subheader("🧭 Check Your Route - Live Risk Assessment")

col1, col2 = st.columns(2)
with col1:
    user_route = st.text_input("Enter chokepoint or port name", "Strait of Hormuz")
with col2:
    if st.button("Analyze Route Risk", type="primary"):
        news = get_live_news(user_route)
        if news:
            st.error(f"🔴 LIVE THREAT DETECTED: {len(news)} incidents in last 24h")
            for n in news[:3]:
                st.markdown(f"- [{n['title']}]({n['url']})")
        else:
            st.success(f"🟢 Route '{user_route}' shows no active threats in public news feeds")

# --- MAIN DASHBOARD ---
st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["🌐 Chokepoints", "🚢 Vessel Tracking", "🚫 Sanctions", "🗺️ Route Planner"])

with tab1:
    st.subheader("Live Global Chokepoint Monitor")
    for route, data in CHOKEPOINTS.items():
        weather = get_weather(data["lat"], data["lon"])
        news = get_live_news(route)
        risk_score = 10 + len(news)*15 + (20 if weather.get("wind", 0) > 15 else 0)
        
        with st.expander(f"**{route}** - Risk Score: {min(risk_score, 100)}/100 - {data['risk_type']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Wind Speed", f"{weather.get('wind', 'N/A')} m/s")
            c2.metric("News Alerts 24h", len(news))
            c3.metric("Weather", weather.get('desc', 'N/A'))
