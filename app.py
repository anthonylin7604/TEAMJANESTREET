import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

from wealth_score import calculate_wealth_score
from ai_insights import generate_advice
from simulator import simulate_growth_monte_carlo

from streamlit_option_menu import option_menu

st.set_page_config(page_title="Wealth Wellness Hub", layout="wide")

# ===============================
# Styling
# ===============================

st.markdown("""
<style>

.main {
    background-color:#f7f9fc;
}

[data-testid="metric-container"] {
    background-color:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.05);
}

h1,h2,h3{
    margin-top:0.5rem;
}

.stButton>button{
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# Header
# ===============================

st.title("💰 Wealth Wellness Hub")
st.caption("Your personal financial health dashboard")
st.divider()

# ===============================
# Session State
# ===============================

if "connected_data" not in st.session_state:
    st.session_state.connected_data = {}

if "wealth_history" not in st.session_state:
    st.session_state.wealth_history = []

if "private_assets_list" not in st.session_state:
    st.session_state.private_assets_list = []

# ===============================
# Sidebar Controls
# ===============================

st.sidebar.title("⚙️ Controls")

selected = option_menu(
    menu_title="Navigation",
    options=["Overview","Portfolio","Simulator","Insights","Export"],
    icons=["house","pie-chart","graph-up","robot","download"],
    menu_icon="cast",
    default_index=0,
)

st.sidebar.divider()

# ===============================
# Connected Accounts Simulation
# ===============================

connect_bank = st.sidebar.checkbox("🏦 Bank Account")
connect_broker = st.sidebar.checkbox("📈 Stock Broker")
connect_crypto = st.sidebar.checkbox("🪙 Crypto Wallet")

if st.sidebar.button("Connect Accounts"):
    with st.spinner("Fetching data..."):
        time.sleep(1)

    if connect_bank:
        st.session_state.connected_data["cash"] = 50000

    if connect_broker:
        st.session_state.connected_data["stocks"] = 20000
        st.session_state.connected_data["bonds"] = 10000

    if connect_crypto:
        st.session_state.connected_data["crypto"] = 10000

    st.success("Accounts connected!")

# ===============================
# Financial Inputs
# ===============================

if st.session_state.connected_data.get("cash") is not None:
    cash = st.session_state.connected_data.get("cash",0)
    stocks = st.session_state.connected_data.get("stocks",0)
    bonds = st.session_state.connected_data.get("bonds",0)
    crypto = st.session_state.connected_data.get("crypto",0)

else:
    cash = st.sidebar.number_input("Cash",0)
    stocks = st.sidebar.number_input("Stocks / ETFs",0)
    bonds = st.sidebar.number_input("Bonds",0)
    crypto = st.sidebar.number_input("Crypto",0)

monthly_income = st.sidebar.number_input("Monthly Income",0)
monthly_expenses = st.sidebar.number_input("Monthly Expenses",1)

# ===============================
# Private Assets
# ===============================

with st.sidebar.expander("Add Private Asset"):

    asset_name = st.text_input("Asset Name")
    asset_type = st.selectbox("Asset Type",
        ["Real Estate","Vehicle","Business Equity","Collectible","Other"])

    asset_value = st.number_input("Market Value",0)
    loan_value = st.number_input("Outstanding Loan",0)

    if st.button("Add Asset"):

        net_value = asset_value - loan_value

        st.session_state.private_assets_list.append({
            "name":asset_name,
            "type":asset_type,
            "value":net_value
        })

        st.success("Asset Added")

private_assets = sum(a["value"] for a in st.session_state.private_assets_list)

# ===============================
# Calculations
# ===============================

total_wealth = cash + stocks + bonds + crypto + private_assets
savings = monthly_income - monthly_expenses

savings_rate = savings / monthly_income if monthly_income>0 else 0

score = calculate_wealth_score(
    cash,stocks,bonds,crypto,
    private_assets,monthly_income,monthly_expenses
)

projected_cash = cash + max(savings,0)
liquidity_ratio = projected_cash / monthly_expenses if monthly_expenses>0 else 0

# ===============================
# OVERVIEW PAGE
# ===============================

if selected == "Overview":

    st.subheader("📊 Financial Overview")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Net Worth",f"${total_wealth:,.0f}")
    col2.metric("Monthly Savings",f"${savings:,.0f}")
    col3.metric("Savings Rate",f"{savings_rate*100:.1f}%")
    col4.metric("Wealth Score",f"{score}/100")

    st.divider()

    colA,colB = st.columns([2,1])

    # Wealth Trend

    with colA:

        st.subheader("Wealth Trend")

        if st.button("Save Snapshot"):

            st.session_state.wealth_history.append({
                "date":pd.Timestamp.now(),
                "wealth":total_wealth
            })

        if st.session_state.wealth_history:

            history_df = pd.DataFrame(st.session_state.wealth_history)

            fig = px.line(history_df,x="date",y="wealth",markers=True)

            fig.update_layout(template="plotly_white",height=400)

            st.plotly_chart(fig,use_container_width=True)

        else:
            st.info("Save snapshots to track wealth.")

    # Liquidity

    with colB:

        st.subheader("Liquidity")

        st.metric("Months Covered",f"{liquidity_ratio:.2f}")

        progress = min(liquidity_ratio/12,1)
        st.progress(progress)

        if liquidity_ratio >= 6:
            st.success("Strong emergency fund")
        elif liquidity_ratio >= 3:
            st.warning("Moderate liquidity")
        else:
            st.error("Low liquidity")

    st.divider()

    # Wealth Score Gauge

    st.subheader("Financial Health Score")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis":{"range":[0,100]},
            "steps":[
                {"range":[0,40],"color":"lightcoral"},
                {"range":[40,70],"color":"khaki"},
                {"range":[70,100],"color":"lightgreen"},
            ]
        }
    ))

    gauge.update_layout(height=300)

    st.plotly_chart(gauge,use_container_width=True)

    # Portfolio Summary

    st.subheader("Portfolio Summary")

    s1,s2,s3 = st.columns(3)

    s1.metric("Invested Assets",f"${stocks+bonds+crypto:,.0f}")
    s2.metric("Liquid Assets",f"${cash:,.0f}")
    s3.metric("Private Assets",f"${private_assets:,.0f}")

    # Risk Indicator

    if total_wealth > 0:

        crypto_ratio = crypto / total_wealth

        if crypto_ratio > 0.3:
            st.warning("High exposure to volatile assets")
        elif crypto_ratio > 0.1:
            st.info("Moderate exposure to crypto")
        else:
            st.success("Low portfolio volatility")

# ===============================
# PORTFOLIO PAGE
# ===============================

if selected == "Portfolio":

    st.subheader("💼 Portfolio Composition")

    df = pd.DataFrame({
        "Asset":["Cash","Stocks","Bonds","Crypto","Private"],
        "Value":[cash,stocks,bonds,crypto,private_assets]
    })

    df = df[df["Value"]>0]

    if not df.empty:

        col1,col2 = st.columns(2)

        with col1:

            fig = px.pie(df,names="Asset",values="Value",hole=0.45)
            fig.update_layout(template="plotly_white")

            st.plotly_chart(fig,use_container_width=True)

        with col2:

            bar = px.bar(df,x="Asset",y="Value",text="Value")

            bar.update_layout(template="plotly_white")

            st.plotly_chart(bar,use_container_width=True)

    st.divider()

    st.subheader("Private Assets")

    if st.session_state.private_assets_list:

        for asset in st.session_state.private_assets_list:

            st.info(
                f"{asset['name']} ({asset['type']}) — ${asset['value']:,.0f}"
            )

    else:
        st.info("No private assets added")

# ===============================
# SIMULATOR
# ===============================

if selected == "Simulator":

    st.subheader("🔮 Monte Carlo Wealth Simulator")

    monthly_investment = st.number_input("Monthly Investment",0,500)

    years = st.slider("Investment Horizon",1,30,10)

    expected_return = st.slider("Expected Return (%)",1,15,8)/100

    annual_volatility = st.slider("Volatility (%)",5,50,15)/100

    n_simulations = st.number_input("Simulations",100,5000,1000,100)

    inflation_rate = st.number_input("Inflation (%)",0,10,3)/100

    median,low,high,years_axis = simulate_growth_monte_carlo(
        total_wealth,
        monthly_investment,
        years,
        expected_return,
        annual_volatility,
        n_simulations,
        inflation_rate
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years_axis,y=high,
        line=dict(color="lightblue"),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=years_axis,y=low,
        fill="tonexty",
        line=dict(color="lightblue"),
        fillcolor="rgba(173,216,230,0.4)",
        name="10-90%"
    ))

    fig.add_trace(go.Scatter(
        x=years_axis,y=median,
        line=dict(color="blue",width=3),
        name="Median"
    ))

    fig.update_layout(
        template="plotly_white",
        height=500,
        title="Projected Wealth Growth"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.metric("Projected Median Wealth",f"${median[-1]:,.0f}")

    future_year = years_axis[-1]

    growth_rate = ((median[-1]/total_wealth)**(1/future_year)-1) if total_wealth>0 else 0

    st.metric("Estimated Annual Growth",f"{growth_rate*100:.2f}%")

# ===============================
# INSIGHTS
# ===============================

if selected == "Insights":

    st.subheader("🤖 AI Financial Insights")

    advice = generate_advice(liquidity_ratio,score,savings_rate)

    for i,tip in enumerate(advice):

        st.markdown(f"""
        **Insight {i+1}**

        {tip}

        ---
        """)

    st.subheader("Financial Independence Tracker")

    if monthly_expenses > 0:

        fire_number = monthly_expenses*12*25

        progress = total_wealth / fire_number if fire_number>0 else 0

        years_to_fi = (fire_number-total_wealth)/(savings*12) if savings>0 else None

        st.metric("FI Target",f"${fire_number:,.0f}")

        st.progress(min(progress,1))

        if years_to_fi:
            st.metric("Years to FI",f"{years_to_fi:.1f}")

# ===============================
# EXPORT
# ===============================

if selected == "Export":

    st.subheader("📤 Export Portfolio Data")

    export_df = pd.DataFrame({
        "Cash":[cash],
        "Stocks":[stocks],
        "Bonds":[bonds],
        "Crypto":[crypto],
        "Private Assets":[private_assets],
        "Monthly Income":[monthly_income],
        "Monthly Expenses":[monthly_expenses],
        "Savings":[savings],
        "Savings Rate":[savings_rate],
        "Total Wealth":[total_wealth]
    })

    csv = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "portfolio_data.csv",
        "text/csv"
    )