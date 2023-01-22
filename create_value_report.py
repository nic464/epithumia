import yfinance as yf
import pandas as pd
import numpy as np


table = pd.DataFrame([], columns=["roic","multiple","industry"])
tickers = pd.read_csv("tickers.csv", header=None)

def append_ticker(symbol):
    ticker = yf.Ticker(symbol)

    # - free cash flow
    fcf = ticker.cashflow.loc["Free Cash Flow"][0]
    # - enterprise value
    ev = ticker.info["marketCap"] + ticker.balance_sheet.loc["Total Debt"][0] - ticker.balance_sheet.loc["Cash And Cash Equivalents"][0]

    # - net operating profit after tax
    try:
        dividends = ticker.cash_flow.loc["Cash Dividends Paid"][0]
    except:
        dividends = 0
    nopat = ticker.income_stmt.loc["Net Income"][0] - dividends
    # - return on invested capital
    roic = (nopat / ticker.balance_sheet.loc["Invested Capital"][0]) * 100

    table.loc[symbol] = [roic, ev/fcf, ticker.info["industry"]]

for t in tickers[0]:
    print(f"Calling API for {t} information...")
    try:
        append_ticker(t)
    except:
        print("Failed API call")

# Create an indicator that rewards high roic and low multiples
table["indicator"] = table["roic"] * (1 / table["multiple"])

# Calculate industry averages of our indicator, then calculate the distance of each company from that industry average
industry_means = table[["industry", "indicator"]].groupby("industry").mean().rename(columns={"indicator":"industry_indicator"})
distance = pd.merge(table.reset_index(), industry_means, on="industry")
distance["distance"] = distance["indicator"] - distance["industry_indicator"]

# Detect the most positive and most negative distance for each industry
min = distance[["industry", "distance"]].groupby("industry").min().rename(columns={"distance":"min_distance"})
max = distance[["industry", "distance"]].groupby("industry").max().rename(columns={"distance":"max_distance"})

# Label each company as the "Leader" or "Laggard" of their industry based on our indicator
distance_tracking = pd.merge(distance, pd.merge(min, max, on="industry"), on="industry")
distance_tracking["report"] = np.where(distance_tracking["distance"] == distance_tracking["min_distance"], "Laggard", np.where(distance_tracking["distance"] == distance_tracking["max_distance"], "Leader", "0"))

# Filter to only the interesting companies and clean up for a report
distance_tracking = distance_tracking[distance_tracking["report"] != "0"].set_index("index")[["industry", "report", "roic", "multiple", "indicator", "distance"]].sort_values(["industry", "distance"])
distance_tracking = distance_tracking[distance_tracking["distance"] != 0]
distance_tracking.to_csv("report.csv")