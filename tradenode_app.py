
import streamlit as st
import requests
import pandas as pd
import math

st.set_page_config(
    page_title="TradeNode.AI | Global Trade Risk OS",
    page_icon="🌍",
    layout="wide",
)

# =========================
# CONFIG
# =========================
FOUNDER = "Muhammad Ali Hassan"
COMPANY = "TradeNode.AI"
CONTACT = "a.hassan0912@gmail.com"
DOMAIN = "https://tradenod.ai"

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")
OPENWEATHER_KEY = st.secrets.get("OPENWEATHER_KEY", "")

CHOKEPOINTS = {
    "Strait of Hormuz": {"lat": 26.6, "lon": 56.3, "risk_type": "Geopolitical"},
    "Suez Canal": {"lat": 30.0, "lon": 32.5, "risk_type": "Blockage"},
    "Panama Canal": {"lat": 9.1, "lon": -79.7, "risk_type": "Drought"},
    "Strait of Malacca": {"lat": 1.2, "lon": 103.4, "risk_type": "Piracy"},
    "Bab-el-Mandeb": {"lat": 12.6, "lon": 43.3, "risk_type": "Conflict"},
    "Turkish Straits": {"lat": 41.0, "lon": 29.0, "risk_type": "Sanctions"},
    "Danish Straits": {"lat": 55.8, "lon": 12.7, "risk_type": "Weather"},
}

FEATURES = [
    ("🛰️", "Vessel Tracking", "Monitor vessel movement and unusual activity."),
    ("🛢️", "Route & Fuel Analysis", "Compare route, journey and fuel implications."),
    ("🌦️", "Weather Intelligence", "Monitor weather and storm-related risk."),
    ("🚫", "Sanctions Monitoring", "Support sanctioned-vessel compliance workflows."),
    ("📰", "News Intelligence", "Bring relevant disruption news into one view."),
    ("🎯", "Threat Score", "Combine signals into an understandable risk score."),
    ("⚓", "Affected Ports", "Highlight potentially exposed ports."),
    ("📦", "Affected Shipments", "Assess shipment exposure to developing events."),
    ("🧭", "Recommended Routes", "Compare alternative routing options."),
    ("💰", "Transport Cost", "Estimate route and transport-cost implications."),
]

# =========================
# STYLE + DEMO WATERMARK
# =========================
st.markdown("""
<style>
.block-container {padding-top:1.2rem;padding-bottom:2rem;}
.hero {
    padding:1.4rem 1.6rem;border-radius:18px;
    background:linear-gradient(135deg,#071827,#0d2842);
    border:1px solid #183b59;margin-bottom:1rem;
}
.card {
    padding:1rem;border-radius:14px;background:#0d1825;
    border:1px solid #1d3044;min-height:135px;margin-bottom:.8rem;
}
.small {color:#93a4b8;font-size:.86rem;}
.risk-high {color:#ff5c67;font-weight:700;}
.risk-med {color:#f5b942;font-weight:700;}
.risk-low {color:#32d583;font-weight:700;}
.demo-watermark {
    position:fixed;right:18px;bottom:18px;z-index:999999;
    padding:7px 13px;border:1px solid rgba(255,255,255,.25);
    border-radius:7px;background:rgba(12,18,28,.82);
    color:rgba(255,255,255,.62);font-size:12px;
    font-weight:800;letter-spacing:2px;
    pointer-events:none;
}
</style>
<div class="demo-watermark">DEMO</div>
""", unsafe_allow_html=True)

# =========================
# DATA FUNCTIONS
# =========================
@st.cache_data(ttl=300)
def get_live_news(query):
    if not NEWSAPI_KEY:
        return []
    try:
        r = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": f'{query} AND (closure OR strike OR attack OR sanction OR storm OR disruption)',
                "sortBy": "publishedAt",
                "pageSize": 8,
                "apiKey": NEWSAPI_KEY,
                "language": "en",
            },
            timeout=8,
        )
        if r.ok:
            return r.json().get("articles", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    if not OPENWEATHER_KEY:
        return {"status": "API key not configured"}
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric"},
            timeout=8,
        )
        if r.ok:
            d = r.json()
            return {
                "temp": d["main"]["temp"],
                "wind": d["wind"]["speed"],
                "desc": d["weather"][0]["description"].title(),
            }
    except Exception:
        pass
    return {"status": "Weather unavailable"}

def risk_score(news_count, wind, risk_type):
    score = 15 + min(news_count * 10, 45)
    score += 25 if wind > 15 else 12 if wind > 10 else 0
    score += 10 if risk_type in {"Geopolitical", "Conflict", "Sanctions"} else 0
    return min(score, 100)

def risk_label(score):
    if score >= 70:
        return "High", "risk-high"
    if score >= 40:
        return "Medium", "risk-med"
    return "Low", "risk-low"

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 🌍 TradeNode.AI")
    st.caption("Global Trade Risk OS")
    page = st.radio(
        "Navigate",
        [
            "Executive Dashboard",
            "Chokepoint Radar",
            "Vessel & Sanctions",
            "Route & Fuel",
            "Weather Intelligence",
            "News Intelligence",
            "Threat Score",
            "Affected Ports & Shipments",
            "About TradeNode.AI",
        ],
    )
    st.divider()
    st.caption("LIVE INTELLIGENCE BETA")
    st.caption("Public-data signals require human verification.")

# =========================
# HEADER
# =========================
st.markdown(f"""
<div class="hero">
<h1 style="margin:0;">🌍 {COMPANY}</h1>
<p style="margin:.35rem 0 0;color:#9db0c4;">
AI-powered maritime route, vessel, weather, sanctions and geopolitical risk intelligence.
</p>
</div>
""", unsafe_allow_html=True)

# =========================
# EXECUTIVE DASHBOARD
# =========================
if page == "Executive Dashboard":
    st.subheader("Global Trade Risk Dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Critical Chokepoints", 5)
    b.metric("Product Modules", len(FEATURES))
    c.metric("Target Warning Window", "6 hrs")
    d.metric("Company Status", "Pre-revenue")

    st.divider()
    st.subheader("5-Chokepoint Dynamic Radar")
    names = [
        "Strait of Hormuz",
        "Bab-el-Mandeb",
        "Suez Canal",
        "Danish Straits",
        "Strait of Malacca",
    ]
    cols = st.columns(5)
    for col, name in zip(cols, names):
        data = CHOKEPOINTS[name]
        news = get_live_news(name)
        weather = get_weather(data["lat"], data["lon"])
        score = risk_score(len(news), weather.get("wind", 0), data["risk_type"])
        label, css = risk_label(score)
        with col:
            st.markdown(f"### {name}")
            st.metric("Threat Score", f"{score}/100")
            st.markdown(f'<span class="{css}">{label} risk</span>', unsafe_allow_html=True)
            st.caption(f"{len(news)} news signals • {weather.get('desc','N/A')}")

    st.divider()
    st.subheader("Predict → See → Decide → Comply → Act")
    flow = [
        ("PREDICT", "Threat scoring from multiple signals."),
        ("SEE", "Map vessels, weather and affected areas."),
        ("DECIDE", "Compare route and fuel implications."),
        ("COMPLY", "Check sanctions and regulatory exposure."),
        ("ACT", "Evaluate early operational responses."),
    ]
    cols = st.columns(5)
    for col, (h, text) in zip(cols, flow):
        with col:
            st.markdown(
                f'<div class="card"><h4>{h}</h4><p class="small">{text}</p></div>',
                unsafe_allow_html=True,
            )

    st.subheader("Platform Modules")
    cols = st.columns(3)
    for i, (icon, h, text) in enumerate(FEATURES):
        with cols[i % 3]:
            st.markdown(
                f'<div class="card"><h3>{icon} {h}</h3><p class="small">{text}</p></div>',
                unsafe_allow_html=True,
            )

# =========================
# CHOKEPOINT RADAR
# =========================
elif page == "Chokepoint Radar":
    st.subheader("🌐 Global Chokepoint Monitor")
    selected = st.selectbox("Select chokepoint", list(CHOKEPOINTS))
    data = CHOKEPOINTS[selected]
    weather = get_weather(data["lat"], data["lon"])
    news = get_live_news(selected)
    score = risk_score(len(news), weather.get("wind", 0), data["risk_type"])
    label, css = risk_label(score)

    a,b,c,d = st.columns(4)
    a.metric("Threat Score", f"{score}/100")
    b.metric("News Signals", len(news))
    c.metric("Wind", f"{weather.get('wind','N/A')} m/s")
    d.metric("Weather", weather.get("desc","N/A"))
    st.markdown(f"### {selected}")
    st.markdown(f'<span class="{css}">{label} risk</span>', unsafe_allow_html=True)
    st.write(f"Risk type: **{data['risk_type']}**")

    if news:
        st.subheader("Recent public-news signals")
        for item in news:
            st.markdown(f"- [{item.get('title','Untitled')}]({item.get('url','#')})")
    else:
        st.info("No live NewsAPI results. Add NEWSAPI_KEY in Streamlit secrets.")

# =========================
# VESSEL + SANCTIONS
# =========================
elif page == "Vessel & Sanctions":
    st.subheader("🚢 Vessel Tracking & Sanctions")
    st.info(
        "The current prototype does not have a live AIS provider connected. "
        "This section provides the intended workflow without inventing vessel positions."
    )
    st.markdown("### Vessel intelligence workflow")
    st.write(
        "AIS position → movement/anchoring detection → vessel identity → sanctions check "
        "→ threat score → affected routes/shipments."
    )
    st.markdown("### Sanctions lookup")
    vessel = st.text_input("Vessel name or IMO number")
    if st.button("Check vessel", type="primary"):
        if vessel.strip():
            st.warning(
                "A verified sanctions-data connector is required for a production result. "
                "No sanctions match is being claimed by this demo."
            )
        else:
            st.error("Enter a vessel name or IMO number.")

# =========================
# ROUTE + FUEL
# =========================
elif page == "Route & Fuel":
    st.subheader("🧭 Route & Fuel Analysis")
    left,right = st.columns(2)
    with left:
        origin = st.text_input("Origin", "Karachi")
        destination = st.text_input("Destination", "Rotterdam")
        distance_nm = st.number_input(
            "Estimated distance (nautical miles)", 100.0, 30000.0, 8500.0
        )
    with right:
        speed = st.number_input("Average speed (knots)", 5.0, 35.0, 14.0)
        fuel_day = st.number_input("Fuel consumption (tons/day)", 1.0, 300.0, 60.0)
        fuel_price = st.number_input("Fuel price ($/ton)", 100.0, 5000.0, 650.0)

    if st.button("Calculate Journey & Fuel", type="primary"):
        days = distance_nm / (speed * 24)
        fuel = days * fuel_day
        cost = fuel * fuel_price
        a,b,c = st.columns(3)
        a.metric("Journey", f"{days:.1f} days")
        b.metric("Fuel", f"{fuel:,.0f} tons")
        c.metric("Fuel Cost", f"${cost:,.0f}")
        st.success(f"Planning estimate for {origin} → {destination}")
        st.caption("Prototype calculation — not navigation advice.")

    st.divider()
    st.subheader("Recommended Route Logic")
    st.write(
        "Production version: compare route distance, threat score, weather, sanctions exposure, "
        "fuel consumption, transport cost and expected delay before recommending alternatives."
    )

# =========================
# WEATHER
# =========================
elif page == "Weather Intelligence":
    st.subheader("🌦️ Weather & Storm Intelligence")
    rows = []
    for name, data in CHOKEPOINTS.items():
        w = get_weather(data["lat"], data["lon"])
        rows.append({
            "Chokepoint": name,
            "Temperature °C": w.get("temp"),
            "Wind m/s": w.get("wind"),
            "Conditions": w.get("desc", w.get("status", "N/A")),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    if not OPENWEATHER_KEY:
        st.info("Add OPENWEATHER_KEY to Streamlit secrets for live weather.")

# =========================
# NEWS
# =========================
elif page == "News Intelligence":
    st.subheader("📰 News Intelligence")
    query = st.text_input("Search maritime risk topic", "Strait of Hormuz")
    if st.button("Search live news", type="primary"):
        articles = get_live_news(query)
        if not articles:
            st.warning("No live results. Add NEWSAPI_KEY to Streamlit secrets.")
        for item in articles:
            st.markdown(f"### {item.get('title','Untitled')}")
            st.caption(
                f"{item.get('source',{}).get('name','Unknown')} • "
                f"{item.get('publishedAt','')}"
            )
            st.write(item.get("description") or "")
            if item.get("url"):
                st.markdown(f"[Open article]({item['url']})")
            st.divider()

# =========================
# THREAT SCORE
# =========================
elif page == "Threat Score":
    st.subheader("🎯 Threat Score Management & Reasoning")
    st.caption("Prototype scoring model — not a validated prediction model.")
    area = st.selectbox("Area", list(CHOKEPOINTS))
    news_count = st.slider("Relevant news signals", 0, 10, 2)
    wind = st.slider("Wind speed (m/s)", 0, 40, 8)
    geopolitical = st.checkbox("Geopolitical/conflict signal", True)

    base = 15
    news_component = min(news_count * 10, 45)
    weather_component = 25 if wind > 15 else 12 if wind > 10 else 0
    geo_component = 10 if geopolitical else 0
    score = min(base + news_component + weather_component + geo_component, 100)
    label, css = risk_label(score)

    st.metric("Threat Score", f"{score}/100")
    st.markdown(f'<span class="{css}">{label} risk</span>', unsafe_allow_html=True)

    st.markdown("### Threat Score Reasoning")
    st.write(f"- Base score: **{base}**")
    st.write(f"- News contribution: **{news_component}**")
    st.write(f"- Weather contribution: **{weather_component}**")
    st.write(f"- Geopolitical contribution: **{geo_component}**")
    st.warning("Production scoring requires validated data, historical back-testing and maritime-domain review.")

# =========================
# AFFECTED PORTS / SHIPMENTS
# =========================
elif page == "Affected Ports & Shipments":
    st.subheader("⚓ Affected Ports & Shipments")
    st.info(
        "This module is structured for the production data layer. "
        "The demo does not fabricate affected-port or shipment records."
    )
    event = st.text_input("Disruption event", "Example: Strait closure")
    st.write("### Intended output")
    cols = st.columns(4)
    cols[0].metric("Affected Ports", "—")
    cols[1].metric("Affected Shipments", "—")
    cols[2].metric("Potential Delay", "—")
    cols[3].metric("Transport Cost Impact", "—")
    st.write(
        "Production workflow: disruption → impacted route graph → ports → shipments → "
        "delay estimate → cost impact → recommended response."
    )

# =========================
# ABOUT
# =========================
elif page == "About TradeNode.AI":
    st.subheader("ℹ️ About TradeNode.AI")
    st.markdown("""
### Company Bio

**TradeNode.AI** is an AI-powered B2B SaaS platform designed to help global trade
companies reduce delays and disruptions caused by uncertainty around maritime routes,
straits, canals, weather, vessel movements, sanctions and geopolitical threats.

TradeNode.AI brings **vessel tracking, route and fuel analysis, weather intelligence,
sanctions monitoring, news intelligence, threat scoring, affected ports, affected
shipments, recommended routes, transport-cost analysis and critical-chokepoint
monitoring** into one unified platform.

The vision is to turn fragmented maritime data into actionable risk intelligence so
trade organizations can identify emerging disruption risks earlier and evaluate
operational responses before delays and costs escalate.
""")

    a,b = st.columns(2)
    with a:
        st.markdown("### Founder")
        st.write(FOUNDER)
        st.write("Founder & Chief Architect")
        st.write("Pakistan")
    with b:
        st.markdown("### Company")
        st.write(COMPANY)
        st.write("AI-powered B2B SaaS")
        st.write("Status: Pre-revenue prototype")

    st.divider()
    st.markdown("### Product Vision")
    for icon, h, text in FEATURES:
        st.markdown(f"**{icon} {h}** — {text}")

    st.divider()
    st.markdown("### Contact")
    st.write(CONTACT)
    st.write(DOMAIN)

st.divider()
st.caption(
    "TradeNode.AI • DEMO • Public-data intelligence prototype • "
    "Human verification required before operational decisions."
)
