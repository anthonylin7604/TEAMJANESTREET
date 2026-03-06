import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from wealth_score import calculate_wealth_score
from ai_insights import generate_advice
from simulator import simulate_growth_monte_carlo

st.set_page_config(page_title="Wealth Wellness Hub", layout="wide")
st.title("💰 Wealth Wellness Hub")

# ===============================
# Initialize Session State
# ===============================
if "connected_data" not in st.session_state:
    st.session_state.connected_data = {}
if "wealth_history" not in st.session_state:
    st.session_state.wealth_history = []
if "private_assets_list" not in st.session_state:
    st.session_state.private_assets_list = []

# ===============================
# Sidebar Inputs
# ===============================
st.sidebar.header("⚙️ Financial Inputs")

# Connected accounts simulation
connect_bank = st.sidebar.checkbox("🏦 Bank Account", key="connect_bank")
connect_broker = st.sidebar.checkbox("📈 Stock Broker", key="connect_broker")
connect_crypto = st.sidebar.checkbox("🪙 Crypto Wallet", key="connect_crypto")

if st.sidebar.button("Connect Selected Accounts"):
    with st.spinner("Fetching data..."):
        time.sleep(1)
    if connect_bank:
        st.session_state.connected_data["cash"] = 50000
    if connect_broker:
        st.session_state.connected_data["stocks"] = 20000
        st.session_state.connected_data["bonds"] = 10000
    if connect_crypto:
        st.session_state.connected_data["crypto"] = 10000
    st.success("Accounts connected successfully!")

# Cash/Assets Inputs
if st.session_state.connected_data.get("cash") is not None:
    cash = st.session_state.connected_data.get("cash",0)
    stocks = st.session_state.connected_data.get("stocks",0)
    bonds = st.session_state.connected_data.get("bonds",0)
    crypto = st.session_state.connected_data.get("crypto",0)
else:
    cash = st.sidebar.number_input("Cash / Bank Deposits ($)", 0, key="cash")
    stocks = st.sidebar.number_input("Stocks / ETFs ($)", 0, key="stocks")
    bonds = st.sidebar.number_input("Bonds / Fixed Income ($)", 0, key="bonds")
    crypto = st.sidebar.number_input("Crypto Assets ($)", 0, key="crypto")

monthly_income = st.sidebar.number_input("Monthly Income ($)", 0, key="monthly_income")
monthly_expenses = st.sidebar.number_input("Monthly Expenses ($)", 1, key="monthly_expenses")

# ===============================
# Tabs for better UX
# ===============================
tab_overview, tab_portfolio, tab_simulator, tab_insights, tab_export = st.tabs(
    ["Overview", "Portfolio", "Simulator", "Insights", "Export"]
)

# ===============================
# Private Assets Form
# ===============================
with st.sidebar.expander("Add Private Asset"):
    asset_name = st.text_input("Asset Name", key="asset_name")
    asset_type = st.selectbox("Asset Type", ["Real Estate", "Vehicle", "Business Equity", "Collectible", "Other"], key="asset_type")
    asset_value = st.number_input("Estimated Market Value ($)", 0, key="asset_value")
    loan_value = st.number_input("Outstanding Loan ($)", 0, key="loan_value")
    if st.button("Add Asset", key="add_asset"):
        net_value = asset_value - loan_value
        st.session_state.private_assets_list.append({"name": asset_name, "type": asset_type, "value": net_value})
        st.success(f"{asset_name} added with net value ${net_value:,.0f}")

# Calculate private assets
private_assets = sum(asset["value"] for asset in st.session_state.private_assets_list)

# ===============================
# Overview Tab
# ===============================
with tab_overview:
    st.header("📊 Financial Overview")

    # Total wealth and savings
    total_wealth = cash + stocks + bonds + crypto + private_assets
    savings = monthly_income - monthly_expenses
    savings_rate = savings / monthly_income if monthly_income > 0 else 0
    score = calculate_wealth_score(cash, stocks, bonds, crypto, private_assets, monthly_income, monthly_expenses)

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Net Worth", f"${total_wealth:,.0f}")
    col2.metric("Monthly Savings", f"${savings:,.0f}")
    col3.metric("Savings Rate", f"{savings_rate*100:.1f}%")
    col4.metric("Wealth Wellness Score", f"{score}/100")

    # ------------------------------
    # Liquidity
    # ------------------------------
    # Simulate liquidity including monthly savings (optional)
    projected_cash = cash + max(savings, 0)  # only add positive savings
    liquidity_ratio = projected_cash / monthly_expenses  # months of expenses covered

    st.subheader("Liquidity")
    st.write(f"Months of expenses covered: **{liquidity_ratio:.2f}**")

    # Progress bar capped at 12 months
    progress = min(liquidity_ratio / 12, 1.0)
    st.progress(progress)

    # Color-coded liquidity message
    if liquidity_ratio >= 6:
        st.success("Excellent emergency fund coverage")
    elif liquidity_ratio >= 3:
        st.warning("Moderate liquidity buffer")
    else:
        st.error("Low liquidity risk")

    # ------------------------------
    # Wealth Trend Tracker
    # ------------------------------
    st.subheader("Wealth Trend")
    if st.button("Save Portfolio Snapshot", key="save_snapshot"):
        st.session_state.wealth_history.append({"date": pd.Timestamp.now(), "wealth": total_wealth})
        st.success("Snapshot saved!")

    if st.session_state.wealth_history:
        history_df = pd.DataFrame(st.session_state.wealth_history)
        fig = px.line(history_df, x="date", y="wealth", title="Wealth Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Save a snapshot to start tracking your wealth trend.")

# ===============================
# Portfolio Tab
# ===============================
with tab_portfolio:
    st.header("💼 Portfolio Composition")
    portfolio = {"Asset":["Cash","Stocks","Bonds","Crypto","Private Assets"], "Value":[cash,stocks,bonds,crypto,private_assets]}
    df = pd.DataFrame(portfolio)
    df = df[df["Value"]>0]
    if not df.empty:
        fig = px.pie(df, names="Asset", values="Value")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add assets to see portfolio composition.")

    st.subheader("Private Assets")
    if st.session_state.private_assets_list:
        for asset in st.session_state.private_assets_list:
            st.write(f"- {asset['name']} ({asset['type']}): ${asset['value']:,.0f}")
    else:
        st.info("No private assets added yet.")

# ===============================
# Simulator Tab
# ===============================
with tab_simulator:
    st.header("🔮 Monte Carlo Wealth Simulator")
    monthly_investment = st.number_input("Monthly Investment ($)", 0, value=500, key="monthly_investment")
    years = st.slider("Investment Horizon (Years)", 1, 30, 10, key="sim_years")
    expected_return = st.slider("Expected Annual Return (%)", 1, 15, 8, key="sim_return")/100
    annual_volatility = st.slider("Annual Volatility (%)", 5, 50, 15, key="sim_vol")/100
    n_simulations = st.number_input("Number of Simulations", 100, 5000, 1000, step=100, key="sim_n")
    inflation_rate = st.number_input("Expected Inflation (%)", 0, 10, 3, key="sim_inflation")/100

    median, low, high, years_axis = simulate_growth_monte_carlo(
        total_wealth, monthly_investment, years, expected_return,
        annual_volatility, n_simulations, inflation_rate
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_axis, y=high, line=dict(color='lightblue'), showlegend=False))
    fig.add_trace(go.Scatter(x=years_axis, y=low, line=dict(color='lightblue'), fill='tonexty', fillcolor='rgba(173,216,230,0.4)', name="10-90%"))
    fig.add_trace(go.Scatter(x=years_axis, y=median, line=dict(color='blue', width=3), name="Median"))
    fig.update_layout(title="Projected Wealth Over Time", xaxis_title="Years", yaxis_title="Wealth ($)", template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Projected Median Wealth", f"${median[-1]:,.0f}")

# ===============================
# Insights Tab
# ===============================
with tab_insights:
    st.header("🤖 AI Financial Insights")
    advice = generate_advice(liquidity_ratio, score)
    for tip in advice:
        st.write(f"- {tip}")

# ===============================
# Export Tab
# ===============================
with tab_export:
    st.header("📤 Export Portfolio Data")
    export_data = pd.DataFrame({
        "Cash":[cash],
        "Stocks":[stocks],
        "Bonds":[bonds],
        "Crypto":[crypto],
        "Private Assets":[private_assets],
        "Monthly Income":[monthly_income],
        "Monthly Expenses":[monthly_expenses],
        "Savings":[savings],
        "Savings Rate (%)":[savings_rate*100],
        "Total Wealth":[total_wealth]
    })
    csv = export_data.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "portfolio_data.csv", "text/csv")