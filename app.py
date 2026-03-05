import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import numpy as np
import time

st.set_page_config(page_title="Alpha Lady Pro", layout="wide")
st.title("💎 Alpha Lady — Pro Trading Cockpit")

# =====================================================
# ACCOUNT SECTION
# =====================================================
st.header("Account Overview")

col1, col2, col3 = st.columns(3)
with col1:
    net_liq = st.number_input("Net Liquidation ($)", value=49000)
with col2:
    excess_liq = st.number_input("Excess Liquidity ($)", value=26000)
with col3:
    cash = st.number_input("Cash Available ($)", value=0)

# =====================================================
# MARKET REGIME (LIGHTWEIGHT + STABLE)
# =====================================================
st.subheader("📡 Market Regime Engine")

@st.cache_data(ttl=60)
def get_regime_data():
    spy = yf.download("SPY", period="5d", progress=False)
    vix = yf.download("^VIX", period="5d", progress=False)
    return spy, vix

spy, vix = get_regime_data()

if len(spy) > 1 and len(vix) > 1:
    spy_change = (spy["Close"].iloc[-1] - spy["Close"].iloc[-2]) / spy["Close"].iloc[-2] * 100
    vix_change = (vix["Close"].iloc[-1] - vix["Close"].iloc[-2]) / vix["Close"].iloc[-2] * 100

    if spy_change > 0.3 and vix_change < 0:
        regime = "🟢 Risk-On"
    elif spy_change < -0.3 and vix_change > 0:
        regime = "🔴 Risk-Off"
    else:
        regime = "🟡 Mixed"
else:
    regime = "Loading..."

st.write(regime)

# =====================================================
# THEME MOVES (FINNHUB LIGHTWEIGHT)
# =====================================================
st.header("Live Market Intelligence")

API_KEY = "PUT_YOUR_FINNHUB_KEY_HERE"

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

themes = {
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

rows = []
for name, ticker in themes.items():
    move = get_price(ticker)
    if move is not None:
        rows.append((name, move))

df = pd.DataFrame(rows, columns=["Theme", "% Move Today"])

if not df.empty:
    df = df.sort_values("% Move Today", ascending=False)

    st.subheader("Strongest Themes")
    st.dataframe(df.head(6), use_container_width=True)

    st.subheader("Weakest Themes")
    st.dataframe(df.tail(6), use_container_width=True)
else:
    st.warning("Theme data loading...")

# =====================================================
# ⭐ DYNAMIC A+ SCANNER (STABLE CORE UNIVERSE)
# =====================================================
st.header("⭐ A+ Trade Scanner (Balanced Income + Growth)")

# Stable dynamic universe (liquid leaders + ETFs)
core_universe = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA",
    "AMD","AVGO","JPM","XOM","LLY","UNH","BRK-B",
    "PLTR","SOFI","HOOD","ZETA","SMH","QQQ","SPY","IWM"
]

@st.cache_data(ttl=300)
def scan_universe(tickers):
    data = yf.download(tickers, period="7d", group_by="ticker", progress=False)
    spy = yf.download("SPY", period="7d", progress=False)

    spy_5d = (spy["Close"].iloc[-1] - spy["Close"].iloc[-6]) / spy["Close"].iloc[-6] * 100

    results = []

    for ticker in tickers:
        try:
            df = data[ticker].dropna()
            if len(df) < 6:
                continue

            close = df["Close"]
            day = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            five = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100
            rel = five - spy_5d
            vol = (close.max() - close.min()) / close.mean() * 100

            score = abs(five) + abs(day) + abs(rel) + vol

            results.append({
                "Ticker": ticker,
                "1D %": round(day,2),
                "5D %": round(five,2),
                "Rel vs SPY": round(rel,2),
                "Score": round(score,2)
            })

        except:
            continue

    return pd.DataFrame(results)

df_scan = scan_universe(core_universe)

if not df_scan.empty:
    df_scan = df_scan.sort_values("Score", ascending=False)

    income = df_scan[(df_scan["5D %"] > 1) & (df_scan["1D %"] < 0)].head(5)
    calls = df_scan[(df_scan["5D %"] > 2) & (df_scan["1D %"] > 0)].head(5)
    puts = df_scan[(df_scan["5D %"] < -2) & (df_scan["1D %"] < 0)].head(5)

    if not income.empty:
        st.subheader("🟢 Pullback Income Candidates")
        st.dataframe(income, use_container_width=True)

    if not calls.empty:
        st.subheader("🔵 Momentum Call Candidates")
        st.dataframe(calls, use_container_width=True)

    if not puts.empty:
        st.subheader("🔴 Breakdown Put Candidates")
        st.dataframe(puts, use_container_width=True)

    st.subheader("📊 Top 10 Ranked Overall")
    st.dataframe(df_scan.head(10), use_container_width=True)

else:
    st.warning("Scanner loading...")
