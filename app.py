import streamlit as st

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
