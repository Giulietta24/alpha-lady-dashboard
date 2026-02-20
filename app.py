import streamlit as st
import yfinance as yf
import pandas as pd
import requests

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

import streamlit as st
import yfinance as yf
import time

st.set_page_config(layout="wide")

# -----------------------------
# AUTO REFRESH EVERY 60 SECONDS
# -----------------------------
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = time.time()
    st.rerun()

# -----------------------------
# MARKET DATA
# -----------------------------
@st.cache_data(ttl=60)
def get_market_data():
    try:
        qqq = yf.download("QQQ", period="5d", interval="15m", progress=False)
        vix = yf.download("^VIX", period="5d", interval="15m", progress=False)
        smh = yf.download("SMH", period="5d", interval="15m", progress=False)
        return qqq, vix, smh
    except:
        return None, None, None

qqq, vix, smh = get_market_data()
if qqq is None or vix is None or smh is None:
    st.warning("Market data loading...")
    st.stop()
def trend_up(data):
    if data is None or len(data) < 15:
        return False
    return float(data["Close"].iloc[-1]) > float(data["Close"].iloc[-5])

def trend_down(data):
    if data is None or len(data) < 15:
        return False
    return float(data["Close"].iloc[-1]) < float(data["Close"].iloc[-5])

def trend_down(data):
    if data is None or len(data) < 15:
        return False
    return float(data["Close"].iloc[-1]) < float(data["Close"].iloc[-5])

def trend_down(data):
    return data["Close"].iloc[-1] < data["Close"].iloc[-10]

qqq_up = trend_up(qqq)
vix_up = trend_up(vix)
smh_up = trend_up(smh)

if vix is None or len(vix) == 0:
    vix_level = 20
else:
    vix_level = float(vix["Close"].iloc[-1])

# -----------------------------
# MARKET REGIME LOGIC
# -----------------------------
if qqq_up and not vix_up and smh_up:
    regime = "INCOME MODE"
elif not qqq_up and vix_up:
    regime = "DANGER MODE"
elif not qqq_up:
    regime = "DEFENCE MODE"
else:
    regime = "CAUTION MODE"

# -----------------------------
# DISPLAY REGIME
# -----------------------------
st.subheader("📡 Market Regime Engine")

if regime == "INCOME MODE":
    st.success("💰 INCOME WINDOW OPEN – Sell CSP + Covered Calls")
elif regime == "CAUTION MODE":
    st.warning("🟡 CAUTION – Smaller Size / Selective CSP")
elif regime == "DEFENCE MODE":
    st.warning("🔴 DEFENCE – Reduce New Put Selling")
elif regime == "DANGER MODE":
    st.error("🚨 DANGER – STOP Selling Puts / Protect Margin")

# -----------------------------
# LONG PUT INTELLIGENCE
# -----------------------------
st.subheader("📉 Long Put Manager")

if vix_level > 22 and vix_up:
    st.info("HOLD HEDGES – Volatility Rising")
elif vix_level > 25:
    st.success("TAKE PARTIAL PROFIT ON PUTS")
elif qqq_up:
    st.warning("CLOSE OR REDUCE HEDGES – Market Stabilising")
else:
    st.write("Monitor Hedges")

# -----------------------------
# LEAPS / LONG CALL MANAGER
# -----------------------------
st.subheader("📈 LEAPS Manager")

if qqq_up and smh_up:
    st.success("HOLD LEAPS – Bullish Trend")
elif not qqq_up and not vix_up:
    st.warning("Consider Selling Calls Against LEAPS")
else:
    st.write("Monitor Momentum")

# -----------------------------
# MARGIN SAFETY BAR (Manual Input for Now)
# -----------------------------
st.subheader("🚨 Margin Risk Status")

excess_liquidity = st.number_input("Enter Current Excess Liquidity", value=15000)

if excess_liquidity > 20000:
    st.success("SAFE – Continue Strategy")
elif excess_liquidity > 10000:
    st.warning("WATCH – Avoid Large New Positions")
elif excess_liquidity > 5000:
    st.error("TIGHT – No New CSP")
else:
    st.error("CRITICAL – Reduce Risk Immediately")
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
elif regime == "INCOME MODE" and excess_liq > 20000:
    st.success("Focus: Sell premium on strongest stocks")
else:
    st.info("Focus: Patience — wait for best setups")

# =========================
# LIVE MARKET INTELLIGENCE (FINNHUB)
# =========================
st.header("Live Market Intelligence")

API_KEY = "d6bqqlpr01qp4li0gq5gd6bqqlpr01qp4li0gq60"

def get_price(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "dp" in data and data["dp"] is not None:
            return round(data["dp"], 2)
        return None
    except:
        return None

tickers = {
    "S&P 500": "SPY",
    "Nasdaq": "QQQ",
    "Small Caps": "IWM",
    "Semis": "SMH",
    "Financials": "XLF",
    "Energy": "XLE",
    "Healthcare": "XLV",
    "REITs": "XLRE",
    "Discretionary": "XLY",
    "Staples": "XLP",
    "Industrials": "XLI",
    "Materials": "XLB"
}

results = {}
for name, ticker in tickers.items():
    results[name] = get_price(ticker)

data_rows = [(k, v) for k, v in results.items() if isinstance(v, (int, float))]
df = pd.DataFrame(data_rows, columns=["Theme", "% Move Today"])

if not df.empty:
    df = df.sort_values("% Move Today", ascending=False)

st.subheader("Strongest Themes Today")
st.dataframe(df.head(6), use_container_width=True)

st.subheader("Weakest Themes Today")
st.dataframe(df.tail(6), use_container_width=True)

# Market regime
qqq_move = results.get("Nasdaq")
spy_move = results.get("S&P 500")

if isinstance(qqq_move, (int, float)) and isinstance(spy_move, (int, float)):
    if qqq_move > 0.5 and spy_move > 0:
        regime = "🟢 Risk-On"
    elif qqq_move < -0.5:
        regime = "🔴 Risk-Off"
    else:
        regime = "🟡 Mixed"
else:
    regime = "Loading..."

st.subheader("Market Regime")
st.write(regime)

# =========================
# ⭐ A+ TRADE SCANNER ENGINE
# =========================
st.header("⭐ A+ Trade Scanner (Balanced Income + Growth)")



def market_open_check():
    # simple placeholder until full regime engine connected
    if "Risk-Off" in regime:
        return False
    return True

if not market_open_check():
    st.error("🚫 Market risk high — NO A+ TRADES")
else:
    st.success("Scanning market for A+ setups...")

# --- sample liquid universe (will expand dynamically) ---
sell_put_universe = [
    "XOM","SLB","HAL","CVX","CAT","GE","IWM","SPY","QQQ",
    "MSFT","AMZN","META","NVDA","MU","TSLA","GOOGL"
]

long_put_universe = [
    "TSLA","COIN","SHOP","PYPL","RIVN","SNOW","ZM",
    "ROKU","AFRM","LCID"
]

call_universe = [
    "NVDA","META","AMZN","MSFT","SMH","MU","AVGO","PANW"
]

# =========================
# REAL DYNAMIC A+ ENGINE
# =========================

st.info("Scanning live market movers...")

def get_movers(endpoint):
    try:
        url = f"https://finnhub.io/api/v1/stock/market/list/{endpoint}?token={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data if isinstance(data, list) else []
    except:
        return []

# Pull live movers
gainers = get_movers("gainers")
losers = get_movers("losers")
active = get_movers("mostactive")

# Combine and deduplicate
universe = {}

for group in [gainers, losers, active]:
    for s in group:
        ticker = s.get("symbol")
        move = s.get("changePercent")
        if ticker and move is not None:
            universe[ticker] = float(move)

sell_puts = []
long_puts = []
calls = []

spy_move = get_price("SPY")

for ticker, move in universe.items():

    # SELL PUT = outperform SPY by >1%
    if isinstance(spy_move, (int, float)) and move > spy_move + 1.0:
        sell_puts.append({
            "Ticker": ticker,
            "% Move": round(move,2),
            "Setup": "Sell Put",
            "Quality": "A+"
        })

    # LONG PUT = underperform SPY by >1%
    if isinstance(spy_move, (int, float)) and move < spy_move - 1.0:
        long_puts.append({
            "Ticker": ticker,
            "% Move": round(move,2),
            "Setup": "Long Put",
            "Quality": "A+"
        })

    # CALL MOMENTUM = strong breakout >2%
    if move > 2.0:
        calls.append({
            "Ticker": ticker,
            "% Move": round(move,2),
            "Setup": "Long Call",
            "Quality": "A+"
        })

# Display results

if not sell_puts and not long_puts and not calls:
    st.warning("🚫 NO A+ SETUPS — DO NOT TRADE")
else:
    if sell_puts:
        st.subheader("🟢 A+ SELL PUTS")
        st.dataframe(pd.DataFrame(sell_puts), use_container_width=True)

    if calls:
        st.subheader("🔵 A+ LONG CALLS")
        st.dataframe(pd.DataFrame(calls), use_container_width=True)

    if long_puts:
        st.subheader("🔴 A+ LONG PUTS")
        st.dataframe(pd.DataFrame(long_puts), use_container_width=True)

# --- OUTPUT TABLES ---

if not sell_puts and not long_puts and not calls:
    st.warning("🚫 NO A+ SETUPS RIGHT NOW — DO NOT TRADE")
else:

    if sell_puts:
        st.subheader("🟢 A+ SELL PUT SETUPS")
        st.dataframe(pd.DataFrame(sell_puts), use_container_width=True)

    if calls:
        st.subheader("🔵 A+ CALL MOMENTUM")
        st.dataframe(pd.DataFrame(calls), use_container_width=True)

    if long_puts:
        st.subheader("🔴 A+ LONG PUT SETUPS")
        st.dataframe(pd.DataFrame(long_puts), use_container_width=True)
