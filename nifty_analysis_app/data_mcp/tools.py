import streamlit as st
from .client import YahooFinanceClient
import pandas as pd
import os

client = YahooFinanceClient()

@st.cache_data(ttl=3600)
def get_all_equities():
    """Reads all equities from CSV and returns a list of symbols with .NS suffix."""
    try:
        # Assuming the CSV is in the same directory as this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "all_equities.csv")
        
        df = pd.read_csv(csv_path)
        # Clean column names just in case
        df.columns = [c.strip() for c in df.columns]
        
        if 'SYMBOL' in df.columns:
            # Add .NS suffix and return unique list
            return [f"{s}.NS" for s in df['SYMBOL'].unique()]
        else:
            st.error("Column 'SYMBOL' not found in all_equities.csv")
            return []
    except Exception as e:
        st.error(f"Error reading all_equities.csv: {e}")
        return []

@st.cache_data(ttl=3600)
def get_stock_price_history(symbol, period="1y", interval="1d", start=None, end=None):
    """Fetches historical price data for a given symbol."""
    return client.get_history(symbol, period, interval, start, end)

@st.cache_data(ttl=86400)
def get_stock_fundamentals(symbol):
    """Fetches fundamental info and financial statements."""
    info = client.get_info(symbol)
    financials = client.get_financials(symbol)
    return info, financials

def get_nifty_tickers():
    """Returns a list of Nifty 100 tickers."""
    return client.get_nifty100_tickers()
