# wealth_score.py

def calculate_wealth_score(cash, stocks, bonds, crypto, private_assets, income, expenses):
    """
    Compute a Wealth Wellness Score combining:
    - Liquidity (emergency fund)
    - Diversification (assets)
    - Savings Rate (cashflow behavior)
    - Investment Ratio (how much wealth is invested)
    Total: 100 points
    """
    total_wealth = cash + stocks + bonds + crypto + private_assets

    # -----------------
    # 1️⃣ Liquidity Score
    months = cash / expenses if expenses > 0 else 0
    if months > 6:
        liquidity_score = 25
    elif months > 3:
        liquidity_score = 15
    else:
        liquidity_score = 5

    # -----------------
    # 2️⃣ Diversification Score
    assets = [stocks, bonds, crypto, private_assets]
    active = sum(1 for a in assets if a > 0)
    diversification_score = (active / 4) * 25

    # -----------------
    # 3️⃣ Savings Rate Score
    savings_rate = (income - expenses) / income if income > 0 else 0
    if savings_rate > 0.2:
        savings_score = 25
    elif savings_rate > 0.1:
        savings_score = 15
    else:
        savings_score = 5

    # -----------------
    # 4️⃣ Investment Ratio Score
    invested = stocks + bonds + crypto + private_assets
    investment_ratio = invested / total_wealth if total_wealth > 0 else 0
    if investment_ratio > 0.7:
        invest_score = 25
    elif investment_ratio > 0.4:
        invest_score = 20
    else:
        invest_score = 10

    total_score = liquidity_score + diversification_score + savings_score + invest_score
    return round(total_score)