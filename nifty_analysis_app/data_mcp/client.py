import yfinance as yf
import pandas as pd

class YahooFinanceClient:
    def __init__(self):
        self.tickers = {}

    def get_ticker(self, symbol):
        if symbol not in self.tickers:
            # Ensure NSE symbols have the .NS suffix if not provided
            if not symbol.endswith('.NS') and not symbol.endswith('.BO') and symbol != '^NSEI':
                 symbol = f"{symbol}.NS"
            self.tickers[symbol] = yf.Ticker(symbol)
        return self.tickers[symbol]

    def get_history(self, symbol, period="1y", interval="1d"):
        ticker = self.get_ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        if history.empty:
            return pd.DataFrame()
        return history

    def get_info(self, symbol):
        ticker = self.get_ticker(symbol)
        return ticker.info

    def get_financials(self, symbol):
        ticker = self.get_ticker(symbol)
        # Returns a dict of DataFrames
        return {
            "income_statement": ticker.financials,
            "balance_sheet": ticker.balance_sheet,
            "cash_flow": ticker.cashflow
        }
    
    def get_nifty100_tickers(self):
        # Fallback list or fetch from wikipedia/niftyindices if possible. 
        # For now, returning a hardcoded sample or dynamic list if better source found.
        # Ideally, we would scrape this. For this implementation, I will return a placeholder list
        # or rely on the user to input ANY symbol, but defaulting analysis to "NSEI" or Nifty 100 constituents.
        
        # A small sample of Nifty 100 for autocomplete purposes
        return [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", 
            "HUL", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
            "LICI", "LT", "BAJFINANCE", "HCLTECH", "ASIANPAINT"
        ]
