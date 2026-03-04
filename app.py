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
# =========================
# FULL DYNAMIC ALPHA ENGINE (FREE)
# =========================

import numpy as np

# ---- YOUR CURRENT PORTFOLIO NAMES ----
portfolio_names = [
    "SOFI","ZETA","PLTR","HOOD",
    "GRAB","SBET","SG","BMNR",
    "QQQ","SPX"
]

# ---- LOAD S&P 500 TICKERS (STATIC SAFE LIST FOR STABILITY) ----
sp500 = pd.read_csv(
    "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
)["Symbol"].tolist()

# ---- BULK DOWNLOAD LAST 7 DAYS ----
with st.spinner("Building dynamic universe..."):
    data = yf.download(sp500, period="7d", group_by="ticker", progress=False)

results = []

spy_data = yf.download("SPY", period="7d", progress=False)
spy_5d = ((spy_data["Close"].iloc[-1] - spy_data["Close"].iloc[-6]) /
          spy_data["Close"].iloc[-6]) * 100

for ticker in sp500:
    try:
        df = data[ticker].dropna()
        if len(df) < 6:
            continue

        close = df["Close"]
        volume = df["Volume"]

        day_change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100
        five_day = ((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6]) * 100
        vol_proxy = (close.max() - close.min()) / close.mean() * 100
        rel_strength = five_day - spy_5d

        score = abs(five_day) + abs(day_change) + vol_proxy + abs(rel_strength)

        results.append({
            "Ticker": ticker,
            "1D %": round(day_change,2),
            "5D %": round(five_day,2),
            "Rel vs SPY": round(rel_strength,2),
            "Vol Proxy": round(vol_proxy,2),
            "Score": round(score,2),
            "In Portfolio": "YES" if ticker in portfolio_names else "NEW"
        })

    except:
        continue

# ---- BUILD DYNAMIC TOP 120 ----
df_all = pd.DataFrame(results)
df_all = df_all.sort_values("Score", ascending=False).head(120)

# ---- ADD ETFs ----
etfs = [
    "XLE","XLK","XLF","XLV","XLI","XLP","XLY","XLRE","XLB","XLC",
    "QQQ","IWM","SPY","TLT","GLD","SLV","USO","SMH","ARKK"
]

etf_data = yf.download(etfs, period="7d", group_by="ticker", progress=False)

for ticker in etfs:
    try:
        df = etf_data[ticker].dropna()
        if len(df) < 6:
            continue

        close = df["Close"]
        day_change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100
        five_day = ((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6]) * 100
        vol_proxy = (close.max() - close.min()) / close.mean() * 100
        rel_strength = five_day - spy_5d

        score = abs(five_day) + abs(day_change) + vol_proxy + abs(rel_strength)

        df_all = pd.concat([df_all, pd.DataFrame([{
            "Ticker": ticker,
            "1D %": round(day_change,2),
            "5D %": round(five_day,2),
            "Rel vs SPY": round(rel_strength,2),
            "Vol Proxy": round(vol_proxy,2),
            "Score": round(score,2),
            "In Portfolio": "YES" if ticker in portfolio_names else "NEW"
        }])])

    except:
        continue

# ---- CLASSIFICATIONS ----

# Aggressive Income (5D positive, 1D pullback)
income = df_all[
    (df_all["5D %"] > 1) &
    (df_all["1D %"] < 0)
].sort_values("Score", ascending=False).head(5)

# Momentum Calls (strong trend)
calls = df_all[
    (df_all["5D %"] > 2) &
    (df_all["1D %"] > 0)
].sort_values("Score", ascending=False).head(5)

# Breakdown Puts (negative acceleration)
puts = df_all[
    (df_all["5D %"] < -2) &
    (df_all["1D %"] < 0)
].sort_values("Score", ascending=False).head(5)

top10 = df_all.sort_values("Score", ascending=False).head(10)

# ---- DISPLAY ----

if income.empty and calls.empty and puts.empty:
    st.warning("🚫 No strong setups right now — market mixed.")
else:
    if not income.empty:
        st.subheader("🟢 Top 5 Aggressive Income (Pullbacks)")
        st.dataframe(income, use_container_width=True)

    if not calls.empty:
        st.subheader("🔵 Top 5 Momentum Calls")
        st.dataframe(calls, use_container_width=True)

    if not puts.empty:
        st.subheader("🔴 Top 5 Breakdown Puts")
        st.dataframe(puts, use_container_width=True)

st.subheader("📊 Top 10 Overall Alpha Ranked")
st.dataframe(top10, use_container_width=True)    
