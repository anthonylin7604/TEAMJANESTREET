# wealth_score.py
import numpy as np

def calculate_wealth_score(cash, stocks, bonds, crypto, private_assets, income, expenses):
    total_wealth = cash + stocks + bonds + crypto + private_assets
    invested_assets = np.array([cash, stocks, bonds, crypto, private_assets], dtype=float)
    
    # 1️⃣ Liquidity (40 pts max)
    months_covered = cash / expenses if expenses > 0 else 0
    if months_covered >= 6:
        liquidity_score = 40
    elif months_covered >= 3:
        liquidity_score = 20 + (months_covered - 3)/3*20
    else:
        liquidity_score = max(0, months_covered / 3 * 20)

    # 2️⃣ Diversification (30 pts max)
    weights = invested_assets / total_wealth if total_wealth > 0 else np.zeros_like(invested_assets)
    positive_weights = weights[weights > 0]
    if len(positive_weights) > 1:
        entropy = -np.sum(positive_weights * np.log(positive_weights))
        max_entropy = np.log(len(positive_weights))
        diversification_score = (entropy / max_entropy) * 30
    else:
        diversification_score = 5

    # 3️⃣ Savings Rate (30 pts max)
    savings_rate = (income - expenses) / income if income > 0 else 0
    if savings_rate >= 0.2:
        savings_score = 30
    elif savings_rate >= 0.1:
        savings_score = 15 + (savings_rate - 0.1)/0.1*15
    else:
        savings_score = max(0, savings_rate / 0.1 * 15)

    # 4️⃣ Risk Penalty
    crypto_ratio = crypto / total_wealth if total_wealth > 0 else 0
    risk_penalty = 0
    if crypto_ratio > 0.3:
        risk_penalty = min(5, (crypto_ratio - 0.3)/0.7*5)

    total_score = liquidity_score + diversification_score + savings_score - risk_penalty
    
    # ⚡ Cap total score at 100
    total_score = min(total_score, 100)
    
    return round(total_score), round(liquidity_score), round(diversification_score), round(savings_score)