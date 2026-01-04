
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
            
            for ticker in tickers:
                try:
                    # Handle single ticker vs multi ticker structure
                    if len(tickers) == 1:
                        df = data
                        vol_col = 'Volume'
                        close_col = 'Adj Close'
                    else:
                        df = data[ticker]
                        vol_col = 'Volume'
                        close_col = 'Adj Close' # or 'Close' if Adj Close not available
                    
                    if df.empty: continue
                    
                    # Ensure we have data
                    if len(df) < 5: continue
                    
                    curr_price = df[close_col].iloc[-1]
                    avg_vol = df[vol_col].tail(20).mean()
                    
                    # Filter: Volume > $500k approx (say 4 Cr INR or just > 50k shares to be safe)
                    # Let's use value: Price * Vol roughly. 
                    # 500k USD ~ 4 Crores INR.
                    # Let's just use a simple liquidity filter: Avg Vol > 50,000 shares
                    if avg_vol < 10000: continue 

                    # 1 Week Return (5 trading days)
                    wk_start = df[close_col].iloc[-6] # 5 days ago
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
                    
                except Exception as e:
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
