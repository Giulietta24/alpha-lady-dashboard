import streamlit as st

st.set_page_config(page_title="Alpha Lady", layout="wide")

st.title("💎 Alpha Lady Trading Dashboard")

st.markdown("### Account Overview")

col1, col2, col3 = st.columns(3)

with col1:
    net_liq = st.number_input("Net Liquidation Value", value=49000)

with col2:
    excess_liq = st.number_input("Excess Liquidity", value=26000)

with col3:
    positions = st.number_input("Open Positions", value=12)

st.markdown("---")

# Risk Engine
if excess_liq > 22000:
    risk_status = "🟢 SAFE"
elif excess_liq > 15000:
    risk_status = "🟡 FULL"
else:
    risk_status = "🔴 REDUCE RISK"

st.subheader("Risk Status")
st.write(risk_status)

st.markdown("---")

st.markdown("### Market Conditions")

col4, col5, col6 = st.columns(3)

with col4:
    qqq = st.selectbox("QQQ Today", ["green", "red"])

with col5:
    vix = st.selectbox("VIX Trend", ["up", "down"])

with col6:
    smh = st.selectbox("Semis (SMH)", ["green", "red"])

if qqq == "green" and smh == "green" and vix == "down":
    market_signal = "🟢 RISK ON – Sell Puts"
elif qqq == "red" and vix == "up":
    market_signal = "🔴 RISK OFF – Hedge or Sell Calls"
else:
    market_signal = "🟡 NEUTRAL – Selective Trades"

st.subheader("Market Signal")
st.write(market_signal)

st.markdown("---")

st.markdown("### Weekly Income Tracker")

target = 500
col7, col8 = st.columns(2)

with col7:
    collected = st.number_input("Premium Collected This Week", value=0)

with col8:
    remaining = target - collected
    st.metric("Remaining to Target ($500)", remaining)

st.markdown("---")

st.markdown("### Today's Action")
st.info("Wait for high-quality setup. Only trade when system aligns.")
