from pathlib import Path
import re

src = Path("/mnt/data/MAIN.txt")
code = src.read_text(encoding="utf-8")

# Replace the original app with a substantially improved, graphics-rich Streamlit dashboard.
improved = r'''import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# TradeNode.ai — Global Trade Risk OS
# ============================================================

st.set_page_config(
    page_title="TradeNode.ai | Global Trade Risk OS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------- CONFIG -------------------------------
FOUNDER = "Muhammad Ali Hassan"
COMPANY = "TradeNode.ai"
CONTACT = "a.hassan0912/m@gmail.com"
DOMAIN = "https://tradenod.ai"

# Store secrets in .streamlit/secrets.toml instead of hard-coding keys.
NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")
OPENWEATHER_KEY = st.secrets.get("OPENWEATHER_KEY", "")

# ---------------------- STYLE -------------------------------
st.markdown("""
<style>
    .main { background: #f7f9fc; }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #071a2f 0%, #123b63 55%, #0b6b73 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,.12);
    }
    .hero h1 { margin: 0; font-size: 2.35rem; }
    .hero p { margin: .35rem 0 0; opacity: .88; }
    .risk-card {
        border-radius: 15px;
        padding: 1rem;
        background: white;
        border: 1px solid #e5eaf0;
        box-shadow: 0 4px 14px rgba(20,40,70,.06);
    }
    .small-muted { color: #6b7280; font-size: .86rem; }
    .status-pill {
        display:inline-block; padding:.25rem .65rem; border-radius:999px;
        font-size:.78rem; font-weight:700;
    }
    .safe { background:#dcfce7; color:#166534; }
    .watch { background:#fef3c7; color:#92400e; }
    .danger { background:#fee2e2; color:#991b1b; }
</style>
""", unsafe_allow_html=True)

# ---------------------- DATA ---------------------------------
CHOKEPOINTS = {
    "Strait of Hormuz": {"lat": 26.6, "lon": 56.3, "risk_type": "Geopolitical"},
    "Suez Canal": {"lat": 30.0, "lon": 32.5, "risk_type": "Blockage"},
    "Panama Canal": {"lat": 9.1, "lon": -79.7, "risk_type": "Drought"},
    "Strait of Malacca": {"lat": 1.2, "lon": 103.4, "risk_type": "Piracy"},
    "Bab el-Mandeb": {"lat": 12.6, "lon": 43.3, "risk_type": "Conflict"},
    "Turkish Straits": {"lat": 41.0, "lon": 29.0, "risk_type": "Sanctions"},
    "Danish Straits": {"lat": 55.8, "lon": 12.7, "risk_type": "Weather"},
}

# ---------------------- HELPERS ------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def get_live_news(query: str):
    """Return recent public news matching the route/risk query."""
    if not NEWSAPI_KEY:
        return []
    try:
        r = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": f"{query} AND (closure OR strike OR attack OR sanction OR storm OR disruption)",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": NEWSAPI_KEY,
            },
            timeout=8,
        )
        r.raise_for_status()
        return r.json().get("articles", [])
    except requests.RequestException:
        return []


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(lat: float, lon: float):
    """Return current weather for a chokepoint."""
    if not OPENWEATHER_KEY:
        return {"status": "API key not configured"}
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        return {
            "temp": data["main"]["temp"],
            "wind": data["wind"]["speed"],
            "desc": data["weather"][0]["main"],
        }
    except (requests.RequestException, KeyError, TypeError):
        return {"status": "Weather unavailable"}


def calculate_risk(news_count: int, wind: float | int = 0, base: int = 10) -> int:
    """Simple transparent demo score; not a navigation-grade risk model."""
    score = base + news_count * 15 + (20 if float(wind or 0) > 15 else 0)
    return max(0, min(score, 100))


def risk_label(score: int):
    if score >= 70:
        return "HIGH", "danger"
    if score >= 40:
        return "WATCH", "watch"
    return "LOW", "safe"


def satellite_link(lat: float, lon: float) -> str:
    return f"https://apps.sentinel-hub.com/eo-browser/?lat={lat}&lng={lon}&zoom=10&time=latest"


def make_map():
    rows = []
    for name, d in CHOKEPOINTS.items():
        rows.append({
            "Location": name,
            "Latitude": d["lat"],
            "Longitude": d["lon"],
            "Risk Type": d["risk_type"],
        })
    df = pd.DataFrame(rows)
    fig = px.scatter_geo(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Location",
        hover_data=["Risk Type"],
        projection="natural earth",
        title="Global Maritime Chokepoints",
    )
    fig.update_traces(marker=dict(size=12))
    fig.update_layout(height=470, margin=dict(l=0, r=0, t=55, b=0))
    return fig


# ---------------------- HEADER -------------------------------
st.markdown(f"""
<div class="hero">
    <h1>🌍 {COMPANY}</h1>
    <p>Global trade risk intelligence for chokepoints, sanctions, weather and route decisions.</p>
    <p class="small-muted">Built by {FOUNDER} · Public-data beta</p>
</div>
""", unsafe_allow_html=True)

# Safety / data disclaimer
st.warning(
    "⚠️ **LIVE INTELLIGENCE BETA:** Public-source data can be incomplete or delayed. "
    "Human verification is mandatory before navigation, routing, or operational decisions."
)

# ---------------------- SIDEBAR ------------------------------
with st.sidebar:
    st.header("⚙️ Control Center")
    st.caption("Configure the dashboard and refresh live feeds.")
    if st.button("🔄 Clear cached data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.subheader("About")
    st.write(f"**Founder:** {FOUNDER}")
    st.write(f"**Contact:** {CONTACT}")
    st.write(f"**Domain:** {DOMAIN}")

    st.divider()
    st.subheader("Data status")
    st.success("News API configured" if NEWSAPI_KEY else "News API not configured")
    st.success("Weather API configured" if OPENWEATHER_KEY else "Weather API not configured")

# ---------------------- KPI ROW ------------------------------
total_points = len(CHOKEPOINTS)
configured_feeds = int(bool(NEWSAPI_KEY)) + int(bool(OPENWEATHER_KEY))

k1, k2, k3, k4 = st.columns(4)
k1.metric("🌐 Chokepoints", total_points)
k2.metric("📡 Live feeds", f"{configured_feeds}/2")
k3.metric("🕒 Updated", datetime.now(timezone.utc).strftime("%H:%M UTC"))
k4.metric("🛡️ Mode", "BETA")

# ---------------------- TABS --------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌐 Global Monitor", "🧭 Route Risk", "🚢 Vessel & Sanctions", "🗺️ Route Map"]
)

# ============================================================
# TAB 1 — GLOBAL MONITOR
# ============================================================
with tab1:
    st.subheader("Global Chokepoint Monitor")

    # Map graphic
    st.plotly_chart(make_map(), use_container_width=True)

    summary = []
    for route, data in CHOKEPOINTS.items():
        weather = get_weather(data["lat"], data["lon"])
        news = get_live_news(route)
        score = calculate_risk(len(news), weather.get("wind", 0))
        label, css = risk_label(score)

        summary.append({
            "Chokepoint": route,
            "Risk": score,
            "Level": label,
            "Type": data["risk_type"],
            "Wind": weather.get("wind", None),
            "Alerts": len(news),
        })

        with st.expander(f"**{route}** · Risk {score}/100 · {label}"):
            a, b, c, d = st.columns(4)
            a.metric("Risk Score", f"{score}/100")
            b.metric("Wind", f"{weather.get('wind', 'N/A')} m/s")
            c.metric("News Alerts", len(news))
            d.metric("Weather", weather.get("desc", "N/A"))

            st.markdown(
                f'<span class="status-pill {css}">{label}</span> '
                f'<span class="small-muted">{data["risk_type"]}</span>',
                unsafe_allow_html=True,
            )

            if news:
                st.markdown("**Recent intelligence**")
                for article in news[:3]:
                    title = article.get("title", "Untitled")
                    url = article.get("url", "#")
                    st.markdown(f"- [{title}]({url})")
            else:
                st.info("No matching public-news alerts returned.")

    summary_df = pd.DataFrame(summary)

    st.divider()
    st.subheader("📊 Risk Analytics")
    chart = px.bar(
        summary_df.sort_values("Risk", ascending=False),
        x="Chokepoint",
        y="Risk",
        color="Level",
        text="Risk",
        title="Current Risk Score by Chokepoint",
    )
    chart.update_layout(height=430, margin=dict(l=0, r=0, t=55, b=0))
    st.plotly_chart(chart, use_container_width=True)

# ============================================================
# TAB 2 — ROUTE RISK
# ============================================================
with tab2:
    st.subheader("🧭 Check Your Route")

    route = st.selectbox("Select a monitored chokepoint", list(CHOKEPOINTS))
    custom_route = st.text_input("Or enter a port / route name", "")
    target = custom_route.strip() or route

    if st.button("🚨 Analyze Route Risk", type="primary", use_container_width=True):
        with st.spinner("Scanning public intelligence feeds..."):
            news = get_live_news(target)

        st.markdown(f"### Intelligence result: `{target}`")

        if news:
            score = min(100, 10 + len(news) * 15)
            label, css = risk_label(score)
            st.markdown(
                f'<span class="status-pill {css}">{label}</span> '
                f'Risk score: **{score}/100**',
                unsafe_allow_html=True,
            )
            st.error(f"🔴 {len(news)} matching public-news incident(s) returned.")
            for article in news[:5]:
                st.markdown(f"- [{article.get('title', 'Untitled')}]({article.get('url', '#')})")
        else:
            st.success("🟢 No matching active threats were returned by the configured public news feed.")
            st.caption("This does not prove a route is safe; it only indicates no matching feed results.")

# ============================================================
# TAB 3 — VESSEL / SANCTIONS
# ============================================================
with tab3:
    st.subheader("🚢 Vessel & Sanctions Intelligence")

    st.info(
        "For production use, connect this module to an authoritative, licensed vessel/AIS "
        "data source and the latest official sanctions datasets."
    )

    sanctions_url = "https://www.treasury.gov/ofac/downloads/sdn.csv"
    st.markdown(f"[Open official OFAC SDN data source]({sanctions_url})")

    st.code(
        """# Example architecture
AIS provider → vessel identity → IMO/MMSI normalization
        ↓
Sanctions screening → name / IMO / aliases
        ↓
Risk engine → alert → analyst review""",
        language="text",
    )

    st.metric("Screening status", "Ready for data connector")
    st.caption("Do not treat a demo or partial list as a complete sanctions-screening result.")

# ============================================================
# TAB 4 — MAP
# ============================================================
with tab4:
    st.subheader("🗺️ Interactive Route Intelligence Map")
    st.plotly_chart(make_map(), use_container_width=True)

    selected = st.selectbox("Select location for satellite context", list(CHOKEPOINTS))
    point = CHOKEPOINTS[selected]
    st.markdown(f"**{selected}** · {point['lat']}, {point['lon']}")
    st.link_button("🛰️ Open Sentinel EO Browser", satellite_link(point["lat"], point["lon"]))

# ---------------------- FOOTER -------------------------------
st.divider()
st.caption(
    f"© {datetime.now().year} {COMPANY} · Public-data beta · "
    "Risk scores are illustrative and must not be used as sole navigation guidance."
)
'''

out = Path("/mnt/data/TradeNode_improved.py")
out.write_text(improved, encoding="utf-8")
print(f"Created: {out}")
print("Added: interactive Plotly map, risk analytics chart, KPI cards, route analysis UI, safer secrets handling, improved error handling, sidebar controls, and cleaner styling.")
