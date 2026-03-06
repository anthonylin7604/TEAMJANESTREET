def generate_advice(liquidity_ratio, diversification_score, savings_rate=None):
    advice = []

    # Liquidity
    if liquidity_ratio < 3:
        advice.append("⚠️ Liquidity is low. Build an emergency fund covering at least 3–6 months of expenses.")
    elif 3 <= liquidity_ratio < 6:
        advice.append("⚠️ Moderate liquidity. Consider adding more cash for emergencies.")
    elif liquidity_ratio > 12:
        advice.append("💡 You hold a large amount of idle cash. Consider investing for better returns.")

    # Diversification
    if diversification_score < 50:
        advice.append("📊 Portfolio is concentrated. Diversify across more asset classes to reduce risk.")
    elif diversification_score >= 75:
        advice.append("✅ Diversification is strong. Now focus on optimizing returns.")

    # Savings rate
    if savings_rate is not None:
        if savings_rate < 0.1:
            advice.append("💰 Savings rate is low. Aim to save at least 10–20% of your income.")
        elif savings_rate > 0.3:
            advice.append("🚀 Excellent savings rate! You can explore higher-yield investments.")

    # Positive reinforcement
    if not advice:
        advice.append("🎉 Financial health looks good. Continue monitoring and investing consistently.")
    
    # General tip
    advice.append("💡 Review your portfolio periodically and adjust based on goals and market conditions.")

    return advice