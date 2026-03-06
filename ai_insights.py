def generate_advice(liquidity_ratio, diversification_score):

    advice = []

    if liquidity_ratio < 3:
        advice.append("⚠️ Your liquidity buffer is low. Consider building an emergency fund covering at least 3–6 months of expenses.")

    if diversification_score < 50:
        advice.append("📊 Your portfolio is concentrated. Diversifying across more asset classes may reduce risk.")

    if liquidity_ratio > 12:
        advice.append("💡 You hold a large amount of idle cash. Consider allocating some into investments.")

    if diversification_score >= 75:
        advice.append("✅ Your portfolio diversification is strong.")

    if not advice:
        advice.append("🎉 Your financial health indicators look strong. Continue monitoring and investing consistently.")

    return advice