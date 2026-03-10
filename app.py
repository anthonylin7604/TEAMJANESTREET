import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import numpy as np
from streamlit_option_menu import option_menu

from wealth_score import calculate_wealth_score
from ai_insights import generate_advice
from simulator import simulate_growth_monte_carlo
from data_simulation import generate_historical_data

st.set_page_config(page_title="Wealth Wellness Hub", layout="wide")

# ===============================
# Styling
# ===============================

st.markdown("""
<style>
.main { background-color:#f7f9fc; }
[data-testid="metric-container"] {
    background-color:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.05);
}
h1,h2,h3{ margin-top:0.5rem; }
.stButton>button{ border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ===============================
# Header
# ===============================

st.title("💰 Wealth Wellness Hub")
st.caption("Your personal financial health dashboard")
st.divider()

# ===============================
# Instructions
# ===============================

with st.expander("📘 How to Use Wealth Wellness Hub"):

    st.markdown("""
**Step 1 — Connect Accounts**

Use the sidebar to connect financial accounts and track other assets:

- 🏦 Bank Account → Cash balance  
- 📈 Stock Broker → Stocks and bonds  
- 🪙 Crypto Wallet → Cryptocurrency holdings 
- 🏠 Private Assets → Real Estate, Vehicles, etc.
- 💵 Monthly Income and Expenditure

Click **Connect Accounts** to load financial data.

**Step 2 — Review Dashboard**

View:

- Net worth
- Portfolio allocation
- Liquidity health
- Wealth score

**Step 3 — Explore Portfolio**

Use the **Portfolio page** to analyze asset allocation and historical values.

**Step 4 — Run Simulations**

The **Simulator page** projects future wealth using Monte Carlo simulations.
""")

# ===============================
# Session State Initialization
# ===============================
if "connected_data" not in st.session_state:
    st.session_state.connected_data = {}

if "private_assets_list" not in st.session_state:
    st.session_state.private_assets_list = []

if "historical_data" not in st.session_state:
    st.session_state.historical_data = None  # initialize to None

if "score_history" not in st.session_state:
    st.session_state.score_history = []
# ===============================
# Sidebar
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
# Connect Accounts
# ===============================

connect_bank = st.sidebar.checkbox("🏦 Bank Account")
connect_broker = st.sidebar.checkbox("📈 Stock Broker")
connect_crypto = st.sidebar.checkbox("🪙 Crypto Wallet")

if st.sidebar.button("Connect Accounts"):

    with st.spinner("Fetching account data..."):
        time.sleep(1)

    if connect_bank:
        st.session_state.connected_data["cash"] = np.random.randint(30000,35000)

    if connect_broker:
        st.session_state.connected_data["stocks"] = np.random.randint(32000,57000)
        st.session_state.connected_data["bonds"] = np.random.randint(21000,35000)

    if connect_crypto:
        st.session_state.connected_data["crypto"] = np.random.randint(4000,42000)

    # generate historical dataset
    st.session_state.historical_data = generate_historical_data()

    st.success("Accounts connected successfully!")

# ===============================
# Financial Inputs
# ===============================

cash = st.session_state.connected_data.get("cash",0)
stocks = st.session_state.connected_data.get("stocks",0)
bonds = st.session_state.connected_data.get("bonds",0)
crypto = st.session_state.connected_data.get("crypto",0)

monthly_income = st.sidebar.number_input("Monthly Income",0)
monthly_expenses = st.sidebar.number_input("Monthly Expenses",1)

# ===============================
# Private Assets
# ===============================

with st.sidebar.expander("Add Private Asset"):

    asset_name = st.text_input("Asset Name")

    asset_type = st.selectbox(
        "Asset Type",
        ["Real Estate","Vehicle","Business Equity","Collectible","Other"]
    )

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

# Calculate wealth score and store sub-scores
score, liq_pts, div_pts, sav_pts = calculate_wealth_score(
    cash, stocks, bonds, crypto,
    private_assets, monthly_income, monthly_expenses
)

# Store sub-scores in session state for the overview gauge display
st.session_state["sub_scores"] = (liq_pts, div_pts, sav_pts)

projected_cash = cash + max(savings,0)
liquidity_ratio = projected_cash / monthly_expenses if monthly_expenses>0 else 0

# ===============================
# OVERVIEW PAGE
# ===============================
if selected == "Overview":
    st.subheader("📊 Financial Overview")

    # Top metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Net Worth", f"${total_wealth:,.0f}")
    col2.metric("Monthly Savings", f"${savings:,.0f}")
    col3.metric("Savings Rate", f"{savings_rate*100:.1f}%")
    st.divider()

    # -----------------------
    # Compute last month's score from historical data
    # -----------------------
    last_month_score = 0
    if st.session_state.historical_data is not None and len(st.session_state.historical_data) >= 2:
        last_row = st.session_state.historical_data.iloc[-2]
        last_month_score, _, _, _ = calculate_wealth_score(
            cash=last_row['cash'],
            stocks=last_row['stocks'],
            bonds=last_row['bonds'],
            crypto=last_row['crypto'],
            private_assets=private_assets,  # current value
            income=monthly_income,
            expenses=monthly_expenses
        )
        last_month_score = min(last_month_score, 100)

    # Current wealth score capped
    score = min(score, 100)
    score_change = score - last_month_score

    # -----------------------
    # Wealth Score Gauge + Liquidity Bar
    # -----------------------
    col1, col2 = st.columns([1,1])

    # Wealth Score Gauge
    with col1:
        st.subheader("Wealth Score")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={'suffix': "/100"},
            gauge={
                'axis': {'range':[0,100]},
                'bar': {'color': "blue"},
                'steps': [
                    {'range':[0,40], 'color':'lightcoral'},
                    {'range':[40,70], 'color':'khaki'},
                    {'range':[70,100], 'color':'lightgreen'}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'thickness':0.75, 'value': score}
            }
        ))
        gauge.update_layout(height=300, margin=dict(t=20,b=20))
        st.plotly_chart(gauge, use_container_width=True)
        st.metric("Change from last month", f"{score_change:+d} pts", delta=f"{score_change:+d}")

    # Liquidity Health Bar
    with col2:
        st.subheader("Emergency Fund Coverage")
        st.write("Months Covered")
        progress = min(liquidity_ratio / 12, 1)
        bar_length = int(progress * 100)
        st.markdown(f"""
        <div style="background-color:#e0e0e0; border-radius:10px; width:100%; height:25px;">
            <div style="background-color:#00cc96; width:{bar_length}%; height:100%; border-radius:10px;"></div>
        </div>
        """, unsafe_allow_html=True)
        st.write(f"{liquidity_ratio:.2f} months")
        if liquidity_ratio >= 6:
            st.success("Strong emergency fund")
        elif liquidity_ratio >= 3:
            st.warning("Moderate liquidity")
        else:
            st.error("Low liquidity")

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
        # Make pie chart larger and more readable
        fig = px.pie(
            df,
            names="Asset",
            values="Value",
            hole=0.35,  # slightly smaller hole for bigger slices
            title="Portfolio Allocation"
        )
        fig.update_traces(
            textinfo="label+percent",
            textposition="inside",
            textfont_size=16  # bigger text inside slices
        )
        fig.update_layout(
            template="plotly_white",
            height=550,  # increase height for more space
            margin=dict(t=60, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True, key="portfolio_pie")

    st.divider()

    
    st.subheader("📊 Historical Portfolio Value")

    if "historical_data" in st.session_state:

        df = st.session_state.historical_data

        timeframe = st.selectbox(
            "Select Time Range",
            ["1 Year","3 Years","5 Years"]
        )

        if timeframe == "1 Year":
            df = df.tail(12)
        elif timeframe == "3 Years":
            df = df.tail(36)

        fig = px.line(
            df,
            x="date",
            y=["cash", "stocks", "crypto"],
            labels={"value": "Amount ($)", "variable": "Asset Type"},  
            title="Portfolio Value Over Time"
        )
        fig.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True, key="historical_chart")

# ===============================
# SIMULATOR
# ===============================

if selected == "Simulator":

    st.subheader("📈 Monte Carlo Wealth Simulator")

    monthly_investment = st.number_input("Monthly Investment ($)")
    years = st.slider("Investment Horizon",1,100,10)

    annual_return = st.slider("Expected Return (%)",1,15,8)/100
    annual_volatility = st.slider("Volatility (%)",5,40,15)/100
    inflation_rate = st.slider("Inflation (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.01, format="%.2f")/100

    median,low,high,years_axis = simulate_growth_monte_carlo(
        total_wealth,
        monthly_investment,
        years,
        annual_return,  
        annual_volatility,
        1000,
        inflation_rate
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years_axis,
        y=high,
        line=dict(color="lightblue"),
        name="90th Percentile"
    ))

    fig.add_trace(go.Scatter(
        x=years_axis,
        y=low,
        fill="tonexty",
        line=dict(color="lightblue"),
        fillcolor="rgba(173,216,230,0.4)",
        name="10th Percentile"
    ))

    fig.add_trace(go.Scatter(
        x=years_axis,
        y=median,
        line=dict(color="blue",width=3),
        name="Median Projection"
    ))

    fig.update_layout(
        template="plotly_white",
        title="Projected Portfolio Growth",
        height=500
    )

    st.plotly_chart(fig,use_container_width=True)

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
        "Total Wealth":[total_wealth]
    })

    csv = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "portfolio_data.csv",
        "text/csv"
    )