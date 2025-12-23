from .client import YahooFinanceClient

client = YahooFinanceClient()

def get_stock_price_history(symbol, period="1y", interval="1d"):
    """Fetches historical price data for a given symbol."""
    return client.get_history(symbol, period, interval)

def get_stock_fundamentals(symbol):
    """Fetches fundamental info and financial statements."""
    info = client.get_info(symbol)
    financials = client.get_financials(symbol)
    return info, financials

def get_nifty_tickers():
    """Returns a list of Nifty 100 tickers."""
    return client.get_nifty100_tickers()
