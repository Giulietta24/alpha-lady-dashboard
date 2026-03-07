import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Alpha Lady Pro", layout="wide")
st.title("💎 Alpha Lady — Pro Trading Cockpit")

# =====================================================
# ACCOUNT SECTION
# =====================================================
st.header("Account Overview")

col1, col2, col3 = st.columns(3)
with col1:
    net_liq = st.number_input("Net Liquidation ($)", value=50000)
with col2:
    excess_liq = st.number_input("Excess Liquidity ($)", value=31000)
with col3:
    cash = st.number_input("Cash Available ($)", value=40000)

# =====================================================
# MARKET REGIME ENGINE
# =====================================================
st.subheader("📡 Market Regime Engine")

@st.cache_data(ttl=60)
def get_regime():
    spy = yf.download("SPY", period="5d", progress=False)
    vix = yf.download("^VIX", period="5d", progress=False)

    if spy is None or vix is None:
        return "Loading..."

    if len(spy) < 2 or len(vix) < 2:
        return "Loading..."

    spy_change = float((spy["Close"].iloc[-1] - spy["Close"].iloc[-2]) / spy["Close"].iloc[-2] * 100)
    vix_change = float((vix["Close"].iloc[-1] - vix["Close"].iloc[-2]) / vix["Close"].iloc[-2] * 100)


    if spy_change > 0.3 and vix_change < 0:
        return "🟢 Risk-On"
    elif spy_change < -0.3 and vix_change > 0:
        return "🔴 Risk-Off"
    else:
        return "🟡 Mixed"

st.write(get_regime())

# =====================================================
# DYNAMIC UNIVERSE BUILDER
# =====================================================
@st.cache_data(ttl=300)
def build_dynamic_universe():

    sp500 = pd.read_csv(
        "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    )["Symbol"].tolist()

    data = yf.download(sp500, period="2d", progress=False)["Close"]

    pct = (data.iloc[-1] - data.iloc[-2]) / data.iloc[-2] * 100
    pct = pct.dropna().sort_values(ascending=False)

    top = pct.head(60).index.tolist()
    bottom = pct.tail(40).index.tolist()

    return list(set(top + bottom))

# =====================================================
# PREMIUM SUITABILITY SCANNER
# =====================================================
@st.cache_data(ttl=300)
def scan_universe(tickers):

    results = []

    data = yf.download(tickers, period="7d", group_by="ticker", progress=False)
    spy = yf.download("SPY", period="7d", progress=False)

    if spy is None or len(spy) < 6:
        return pd.DataFrame()

    spy_5d = (spy["Close"].iloc[-1] - spy["Close"].iloc[-6]) / spy["Close"].iloc[-6] * 100

    for ticker in tickers:
        try:
            df = data[ticker].dropna()
            if len(df) < 6:
                continue

            close = df["Close"]

            day = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            five = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100
            rel = five - spy_5d
            range_pct = (close.max() - close.min()) / close.mean() * 100

            trend_score = max(five, 0) * 1.5
            relative_score = max(rel, 0) * 1.2

            pullback_score = 0
            if -4 <= day <= -0.5:
                pullback_score = abs(day) * 1.3

            vol_score = range_pct * 0.8

            collapse_penalty = 0
            if day < -5 or five < -3:
                collapse_penalty = 10

            premium_score = (
                trend_score +
                relative_score +
                pullback_score +
                vol_score -
                collapse_penalty
            )

            results.append({
                "Ticker": ticker,
                "1D %": round(day, 2),
                "5D %": round(five, 2),
                "Rel vs SPY": round(rel, 2),
                "Range %": round(range_pct, 2),
                "Premium Score": round(premium_score, 2)
            })

        except:
            continue

    return pd.DataFrame(results)

# =====================================================
# DISPLAY SCANNER
# =====================================================
st.header("⭐ A+ Trade Scanner (Balanced Income + Growth)")

core_universe = build_dynamic_universe()
df_scan = scan_universe(core_universe)

if not df_scan.empty:

    df_scan = df_scan.sort_values(by="Premium Score", ascending=False)

    income = df_scan[
        (df_scan["5D %"] > 1.5) &
        (df_scan["1D %"] < 0)
    ].head(5)

    if not income.empty:
        st.subheader("🟢 Pullback Income Candidates")
        st.dataframe(income, use_container_width=True)

    st.subheader("📊 Top 10 Ranked Overall")
    st.dataframe(df_scan.head(10), use_container_width=True)

else:
    st.warning("Scanner loading...")
