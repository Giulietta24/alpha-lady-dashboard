import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import numpy as np

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
# MARKET REGIME
# =====================================================
st.subheader("📡 Market Regime Engine")

@st.cache_data(ttl=60)
def get_regime_data():
    spy = yf.download("SPY", period="5d", progress=False)
    vix = yf.download("^VIX", period="5d", progress=False)
    return spy, vix

spy, vix = get_regime_data()

regime = "Loading..."

if spy is not None and vix is not None and len(spy) > 2 and len(vix) > 2:
    try:
        spy_close = spy["Close"]
        vix_close = vix["Close"]

        spy_change = float((spy_close.iloc[-1] - spy_close.iloc[-2]) / spy_close.iloc[-2] * 100)
        vix_change = float((vix_close.iloc[-1] - vix_close.iloc[-2]) / vix_close.iloc[-2] * 100)

        if spy_change > 0.3 and vix_change < 0:
            regime = "🟢 Risk-On"
        elif spy_change < -0.3 and vix_change > 0:
            regime = "🔴 Risk-Off"
        else:
            regime = "🟡 Mixed"
    except:
        regime = "Loading..."

st.write(regime)

# =====================================================
# ⭐ A+ SCANNER
# =====================================================
st.header("⭐ A+ Trade Scanner (Balanced Income + Growth)")

# =====================================================
# BUILD TRUE DYNAMIC UNIVERSE (TOP + BOTTOM MOVERS)
# =====================================================

@st.cache_data(ttl=300)
def build_dynamic_universe():

    # Load S&P 500 symbols
    sp500 = pd.read_csv(
        "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    )["Symbol"].tolist()

    # Download 2 days of data
    data = yf.download(sp500, period="2d", progress=False)["Close"]

    # Calculate daily % change
    pct = (data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100
    pct = pct.dropna().sort_values(ascending=False)

    # Select strongest + weakest
    top_movers = pct.head(60).index.tolist()
    bottom_movers = pct.tail(40).index.tolist()

    dynamic_universe = list(set(top_movers + bottom_movers))

    return dynamic_universe


core_universe = build_dynamic_universe()

@st.cache_data(ttl=300)
def scan_universe(tickers):
    data = yf.download(tickers, period="7d", group_by="ticker", progress=False)
    spy = yf.download("SPY", period="7d", progress=False)

    if spy is None or len(spy) < 6:
        return pd.DataFrame()

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

            close = df["Close"]

# Price changes
day = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
five = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100
rel = five - spy_5d

# Volatility proxy
range_pct = (close.max() - close.min()) / close.mean() * 100

# -------------------------------
# PREMIUM SUITABILITY SCORING
# -------------------------------

# 1️⃣ Trend strength score
trend_score = max(five, 0) * 1.5

# 2️⃣ Relative strength score
relative_score = max(rel, 0) * 1.2

# 3️⃣ Pullback quality (A + B zone)
pullback_score = 0
if -4 <= day <= -0.5:
    pullback_score = abs(day) * 1.3

# 4️⃣ Volatility premium proxy
vol_score = range_pct * 0.8

# 5️⃣ Downside penalty (avoid collapses)
collapse_penalty = 0
if day < -5 or five < -3:
    collapse_penalty = 10

premium_score = trend_score + relative_score + pullback_score + vol_score - collapse_penalty

results.append({
    "Ticker": ticker,
    "1D %": round(day,2),
    "5D %": round(five,2),
    "Rel vs SPY": round(rel,2),
    "Range %": round(range_pct,2),
    "Premium Score": round(premium_score,2)
})

        except:
            continue

    return pd.DataFrame(results)

df_scan = scan_universe(core_universe)

if df_scan is not None and not df_scan.empty and "Score" in df_scan.columns:

    df_scan["Score"] = pd.to_numeric(df_scan["Score"], errors="coerce")
    df_scan = df_scan.dropna(subset=["Score"])

    if not df_scan.empty:

        df_scan = df_scan.sort_values(by="Premium Score", ascending=False)

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
        st.warning("No valid scan results yet.")

else:
    st.warning("Scanner loading...")
