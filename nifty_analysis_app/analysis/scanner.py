
import yfinance as yf
import pandas as pd
import os
from data_mcp.tools import get_nifty_tickers
import streamlit as st

class MarketScanner:
    def __init__(self):
        self.tickers = self._get_universe()

    def _get_universe(self):
        """
        Returns the list of tickers to scan. 
        Defaults to Nifty 500 if available, else falls back to Nifty 100.
        """
        try:
            # Try to load Nifty 500 from CSV
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to app dir then data_mcp
            csv_path = os.path.join(os.path.dirname(current_dir), "data_mcp", "nifty500.csv")
            
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                # Assume 'Symbol' column exists and needs '.NS' appended if not present
                if 'Symbol' in df.columns:
                    tickers = df['Symbol'].tolist()
                    return [f"{t}.NS" if not str(t).endswith('.NS') else t for t in tickers]
                elif 'SYMBOL' in df.columns:
                    tickers = df['SYMBOL'].tolist()
                    return [f"{t}.NS" if not str(t).endswith('.NS') else t for t in tickers]
            
            # Fallback
            return get_nifty_tickers()
        except Exception as e:
            print(f"Error loading universe: {e}")
            return get_nifty_tickers()

    @st.cache_data(ttl=3600) # Cache for 1 hour to avoid spamming YF
    def get_market_pulse(_self):
        """
        Scans the universe for Monthly and Weekly performance.
        Returns a dict with 4 DataFrames: monthly_gainers, monthly_losers, weekly_gainers, weekly_losers.
        """
        tickers = _self.tickers
        if not tickers:
            return {}

        # Batch download 40 days of data to cover 30 days + weekends
        try:
            # Download 'Adj Close' and 'Volume'
            data = yf.download(tickers, period="2mo", interval="1d", group_by='ticker', threads=True, progress=False)
            
            # If multi-level columns (Ticker, OHLCV), accessing is tricky.
            # yfinance returns MultiIndex columns: (Ticker, PriceType)
            
            results = []
            
            # Check column levels to determine structure
            is_multi_ticker = len(tickers) > 1
            
            for ticker in tickers:
                try:
                    df = pd.DataFrame() # Sentinel
                    
                    if not is_multi_ticker:
                         df = data
                    else:
                        # Multi-level columns
                        # Case 1: Ticker is Top Level (group_by='ticker') -> data[ticker] works
                        if isinstance(data.columns, pd.MultiIndex) and ticker in data.columns.get_level_values(0):
                            df = data[ticker]
                        # Case 2: Price is Top Level -> data.xs(ticker, level=1, axis=1)
                        elif isinstance(data.columns, pd.MultiIndex) and ticker in data.columns.get_level_values(1):
                             df = data.xs(ticker, level=1, axis=1)
                        # Case 3: Flat Columns but we have prefix? Unlikely with 1d interval.
                        
                    if df.empty: 
                        # print(f"Empty data for {ticker}")
                        continue
                    
                    # Normalize columns
                    # If single level, columns are 'Open', 'Close' etc.
                    
                    # Check needed columns
                    current_cols = df.columns.tolist()
                    close_col = 'Adj Close' if 'Adj Close' in current_cols else 'Close'
                    vol_col = 'Volume'
                    
                    if close_col not in current_cols or vol_col not in current_cols:
                        # print(f"Missing columns for {ticker}: {current_cols}")
                        continue

                    # Ensure we have enough rows
                    if len(df) < 5: 
                         continue
                    
                    curr_price = df[close_col].iloc[-1]
                    avg_vol = df[vol_col].tail(20).mean()
                    
                    # Filter
                    if avg_vol < 10000: continue 

                    # 1 Week Return (5 trading days)
                    wk_start = df[close_col].iloc[-6] 
                    wk_ret = (curr_price - wk_start) / wk_start
                    
                    # 1 Month Return (20 trading days)
                    mo_idx = -21 if len(df) >= 21 else 0
                    mo_start = df[close_col].iloc[mo_idx] 
                    mo_ret = (curr_price - mo_start) / mo_start
                    
                    results.append({
                        "Ticker": ticker,
                        "Price": curr_price,
                        "1W %": wk_ret * 100,
                        "1M %": mo_ret * 100,
                        "Volume": avg_vol
                    })
                    
                except Exception as ex:
                    print(f"Error processing {ticker}: {ex}")
                    continue
            
            res_df = pd.DataFrame(results)
            if res_df.empty: return {}
            
            # Sorts
            res_df = res_df.sort_values("1M %", ascending=False)
            
            return {
                "monthly_gainers": res_df.head(10)[["Ticker", "Price", "1M %", "Volume"]],
                "monthly_losers": res_df.tail(10).sort_values("1M %", ascending=True)[["Ticker", "Price", "1M %", "Volume"]],
                "weekly_gainers": res_df.sort_values("1W %", ascending=False).head(10)[["Ticker", "Price", "1W %", "Volume"]],
                "weekly_losers": res_df.sort_values("1W %", ascending=True).head(10)[["Ticker", "Price", "1W %", "Volume"]],
                "full_data": res_df # Return full scan provided for checking Anti-Gravity on all losers
            }
            
        except Exception as e:
            st.error(f"Scan failed: {e}")
            return {}
