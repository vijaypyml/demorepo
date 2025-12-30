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

    def _retry_on_rate_limit(self, func, *args, **kwargs):
        """Retries a function call upon YFRateLimitError with exponential backoff."""
        import time
        import random
        
        retries = 3
        delay = 1.0
        
        for attempt in range(retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check for rate limit error string or type (yfinance specific or generic exception text)
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "too many requests" in error_msg or "429" in error_msg:
                    if attempt < retries:
                        sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                        continue
                raise e

    def get_history(self, symbol, period="1y", interval="1d"):
        def _fetch():
            ticker = self.get_ticker(symbol)
            return ticker.history(period=period, interval=interval)
            
        history = self._retry_on_rate_limit(_fetch)
        if history.empty:
            return pd.DataFrame()
        return history

    def get_info(self, symbol):
        def _fetch():
            ticker = self.get_ticker(symbol)
            return ticker.info
        return self._retry_on_rate_limit(_fetch)

    def get_financials(self, symbol):
        def _fetch():
            ticker = self.get_ticker(symbol)
            # Accessing properties triggers the fetch
            return {
                "income_statement": ticker.financials,
                "balance_sheet": ticker.balance_sheet,
                "cash_flow": ticker.cashflow
            }
        return self._retry_on_rate_limit(_fetch)
    
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
