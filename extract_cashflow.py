import yfinance as yf
import pandas as pd


table = pd.DataFrame([], columns=["roic","multiple","industry"])

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
    roic = nopat / ticker.balance_sheet.loc["Invested Capital"][0]

    table.loc[symbol] = [roic, ev/fcf, ticker.info["industry"]]

append_ticker("MSFT")
append_ticker("DIS")
append_ticker("NFLX")
append_ticker("WBD")
append_ticker("PARA")
append_ticker("CMCSA")