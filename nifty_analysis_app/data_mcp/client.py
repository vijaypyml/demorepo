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
        """Returns the list of tickers (All active NSE if available, else Nifty 500, else fallback)."""
        import os
        import csv
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Priority 1: Full Equity List
        all_equities_path = os.path.join(base_dir, "all_equities.csv")
        tickers = []
        
        if os.path.exists(all_equities_path):
            try:
                with open(all_equities_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # EQUITY_L.csv usually has 'SYMBOL'
                        if "SYMBOL" in row:
                            tickers.append(row["SYMBOL"])
                        elif "Symbol" in row:
                             tickers.append(row["Symbol"])
                if tickers:
                    return tickers
            except Exception as e:
                print(f"Error reading All Equities CSV: {e}")

        # Priority 2: Nifty 500
        nifty500_path = os.path.join(base_dir, "nifty500.csv")
        if os.path.exists(nifty500_path):
            try:
                with open(nifty500_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "Symbol" in row:
                            tickers.append(row["Symbol"])
                        elif "SYMBOL" in row:
                            tickers.append(row["SYMBOL"])
                if tickers:
                    return tickers
            except Exception as e:
                print(f"Error reading Nifty CSV: {e}")

        # Fallback (Hardcoded sample if CSV fails)
        return [
            "ABB", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL", "ACC", "AMBUJACEM", "APOLLOHOSP", 
            "ASIANPAINT", "DMART", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BALKRISIND", "BANKBARODA", "BERGEPAINT", 
            "BEL", "BHARATFORG", "BHEL", "BPCL", "BHARTIARTL", "BOSCHLTD", "BRITANNIA", "CANBK", "CHOLAFIN", "CIPLA", 
            "COALINDIA", "COLPAL", "DLF", "DABUR", "DIVISLAB", "DRREDDY", "EICHERMOT", "GAIL", "GODREJCP", "GODREJPROP", 
            "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO", "HAL", "HINDUNILVR", "ICICIBANK", 
            "ICICIGI", "ICICIPRULI", "ITC", "IOC", "IRCTC", "IRFC", "INDUSINDBK", "NAUKRI", "INFY", "INDIGO", 
            "JSWSTEEL", "JINDALSTEL", "JIOFIN", "KOTAKBANK", "LTIM", "LT", "LICI", "M&M", "MARICO", "MARUTI", 
            "MPHASIS", "MUTHOOTFIN", "NTPC", "NESTLEIND", "ONGC", "PIIND", "PIDILITIND", "PFC", "POWERGRID", "PNB", 
            "RECLTD", "RELIANCE", "SBICARD", "SBILIFE", "SRF", "MOTHERSON", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SBIN", 
            "SUNPHARMA", "TVSMOTOR", "TATACHEM", "TATACOMM", "TCS", "TATACONSUM", "TATAELXSI", "TATAMOTORS", "TATAPOWER", "TATASTEEL", 
            "TECHM", "TITAN", "TORNTPHARM", "TRENT", "ULTRACEMCO", "UNITEDSPIR", "VBL", "VEDL", "WIPRO", "ZOMATO", "ZYDUSLIFE"
        ]
