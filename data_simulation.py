import numpy as np
import pandas as pd

def generate_historical_data(years=5):

    months = years * 12

    dates = pd.date_range(end=pd.Timestamp.today(), periods=months, freq="M")

    cash = np.cumsum(np.random.normal(200, 100, months)) + 20000
    stocks = np.cumsum(np.random.normal(500, 800, months)) + 15000
    crypto = np.cumsum(np.random.normal(300, 1200, months)) + 5000

    df = pd.DataFrame({
        "date": dates,
        "cash": cash,
        "stocks": stocks,
        "crypto": crypto
    })

    df["total"] = df["cash"] + df["stocks"] + df["crypto"]

    return df