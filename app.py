import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Alpha Lady Pro", layout="wide")

st.title("💎 Alpha Lady — Pro Trading Cockpit")

# =========================
# ACCOUNT CORE
# =========================
st.header("Account Overview")

col1, col2, col3 = st.columns(3)

with col1:
    net_liq = st.number_input("Net Liquidation ($)", value=49000)

with col2:
    excess_liq = st.number_input("Excess Liquidity ($)", value=26000)

with col3:
    cash = st.number_input("Cash Available ($)", value=0)

# =========================
# PORTFOLIO STRUCTURE
# =========================
st.header("Portfolio Structure")

c1, c2, c3, c4 = st.columns(4)

with c1:
    short_puts = st.number_input("Short Puts (contracts)", value=0)

with c2:
    covered_calls = st.number_input("Covered Calls", value=0)

with c3:
    long_calls = st.number_input("Long Calls", value=0)

with c4:
    shares = st.number_input("Stock Positions", value=0)
    hedges = st.number_input("Hedge Positions", value=0)


total_positions = short_puts + covered_calls + long_calls + shares + hedges
# =========================
# POSITION LOAD SCORING
# =========================
st.header("Position Load Score")

# weighted exposure (puts heavier risk)
load_score = (short_puts * 2) + covered_calls + long_calls + shares + (hedges * 0.5)

if load_score < 15:
    load_status = "🟢 LIGHT — capacity to add trades"
elif load_score < 30:
    load_status = "🟡 BALANCED — add selectively"
elif load_score < 45:
    load_status = "🔴 HEAVY — only best setups"
else:
    load_status = "⛔ OVERLOADED — no new trades"

st.subheader(load_status)
st.write(f"Load Score: {load_score}")



# =========================
# RISK ENGINE
# =========================
st.header("Risk Engine")

if excess_liq > 25000:
    risk = "🟢 SAFE — capacity to trade"
elif excess_liq > 15000:
    risk = "🟡 FULL — trade selectively"
else:
    risk = "🔴 DEFENSIVE — reduce risk"

st.subheader(risk)

if total_positions > 20:
    st.warning("⚠️ Large number of positions — avoid adding more")
elif total_positions < 8:
    st.success("Good capacity for income trades")

# =========================
# MARKET MODE
# =========================
st.header("Market Mode")

m1, m2, m3 = st.columns(3)

with m1:
    qqq = st.selectbox("QQQ", ["green", "red"])

with m2:
    vix = st.selectbox("VIX", ["falling", "rising"])

with m3:
    semis = st.selectbox("Semiconductors (SMH)", ["green", "red"])

if qqq == "green" and semis == "green" and vix == "falling":
    market = "🟢 RISK ON — Sell puts"
elif qqq == "red" and vix == "rising":
    market = "🔴 RISK OFF — Hedge / sell calls"
else:
    market = "🟡 NEUTRAL — selective trades"

st.subheader(market)

# =========================
# INCOME TRACKER
# =========================
st.header("Income Tracker")

target = 500
col7, col8 = st.columns(2)

with col7:
    collected = st.number_input("Premium Collected This Week", value=0)

with col8:
    remaining = target - collected
    st.metric("Remaining to Weekly Target ($500)", remaining)

# =========================
# TRADE SIGNAL BOX
# =========================
st.header("Today's Trade Focus")

if risk.startswith("🔴"):
    st.error("Focus: Reduce risk / hedge")
elif "RISK ON" in market and excess_liq > 20000:
    st.success("Focus: Sell premium on strongest stocks")
else:
    st.info("Focus: Patience — wait for best setups")

# =========================
# TRADE RANKING SCANNER
# =========================
st.header("Trade Ranking Scanner")

st.write("Enter market feel for key stocks (quick daily scan)")

colA, colB, colC = st.columns(3)

with colA:
    tsla = st.selectbox("TSLA", ["strong", "neutral", "weak"])
    coin = st.selectbox("COIN", ["strong", "neutral", "weak"])
    nvda = st.selectbox("NVDA", ["strong", "neutral", "weak"])

with colB:
    mu = st.selectbox("MU", ["strong", "neutral", "weak"])
    amzn = st.selectbox("AMZN", ["strong", "neutral", "weak"])
    rklb = st.selectbox("RKLB", ["strong", "neutral", "weak"])

with colC:
    googl = st.selectbox("GOOGL", ["strong", "neutral", "weak"])
    sofi = st.selectbox("SOFI", ["strong", "neutral", "weak"])
    pltr = st.selectbox("PLTR", ["strong", "neutral", "weak"])

st.subheader("Scanner Result")

candidates = []

if tsla == "strong": candidates.append("TSLA sell puts")
if coin == "strong": candidates.append("COIN sell puts")
if nvda == "strong": candidates.append("NVDA sell puts")
if mu == "strong": candidates.append("MU sell puts")
if amzn == "strong": candidates.append("AMZN sell puts")
if rklb == "strong": candidates.append("RKLB sell puts")
if googl == "strong": candidates.append("GOOGL sell puts")
if sofi == "strong": candidates.append("SOFI sell puts")
if pltr == "strong": candidates.append("PLTR sell puts")

if len(candidates) == 0:
    st.info("No strong setups today — patience")
else:
    st.success("Top Put Candidates:")
    for c in candidates[:3]:
        st.write("•", c)
# =========================
# LIVE MACRO & THEME ENGINE
# =========================
st.header("Live Market Intelligence")

@st.cache_data(ttl=300)
def get_price(symbol):
    data = yf.download(symbol, period="5d", interval="1d", progress=False)
    if len(data) < 2:
        return 0
    return round(((data["Close"][-1] / data["Close"][-2]) - 1) * 100, 2)

# Core macro tickers
tickers = {
    "QQQ (Growth)": "QQQ",
    "SPY (Market)": "SPY",
    "IWM (Small caps)": "IWM",
    "VIX": "^VIX",
    "Bonds TLT": "TLT",
    "Dollar DXY": "DX-Y.NYB",
    "Oil": "CL=F",
    "Gold": "GC=F",
    "Copper": "HG=F",
    "Semis SMH": "SMH",
    "Financials": "XLF",
    "Energy": "XLE",
    "Healthcare": "XLV",
    "REITs": "XLRE",
    "Staples": "XLP",
    "Discretionary": "XLY",
    "Industrials": "XLI",
    "Materials": "XLB"
}

results = {}

for name, ticker in tickers.items():
    try:
        results[name] = get_price(ticker)
    except:
        results[name] = 0

df = pd.DataFrame(list(results.items()), columns=["Theme", "% Move Today"])
df = df.sort_values("% Move Today", ascending=False)

st.subheader("Strongest Themes Today")
st.dataframe(df.head(8), use_container_width=True)

st.subheader("Weakest Themes Today")
st.dataframe(df.tail(8), use_container_width=True)

# Risk regime logic
qqq_move = results.get("QQQ (Growth)",0)
vix_move = results.get("VIX",0)

if qqq_move > 0.4 and vix_move < 0:
    regime = "🟢 Risk-on"
elif qqq_move < -0.4 and vix_move > 0:
    regime = "🔴 Risk-off"
else:
    regime = "🟡 Mixed/Neutral"

st.subheader("Market Regime")
st.write(regime)
