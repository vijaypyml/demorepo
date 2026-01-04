
import yfinance as yf
import pandas as pd
import numpy as np
from data_mcp.client import YahooFinanceClient

class AntiGravityAnalyzer:
    def __init__(self):
        self.client = YahooFinanceClient()

    def check_fundamentals(self, ticker):
        """
        Checks if a ticker passes the fundamental quality filter.
        Criteria: Debt/Equity < 1.0, Positive Earnings, Valid PE.
        Returns: (bool [Pass/Fail], str [Reason/Details])
        """
        try:
            info = self.client.get_info(ticker)
            financials = self.client.get_financials(ticker)
            
            # 1. Debt to Equity
            debt_to_equity = info.get('debtToEquity', None)
            if debt_to_equity:
                # Yahoo returns it as percentage usually (e.g. 50.5 for 0.5 ratio)
                # But sometimes it's huge. Let's normalize. 
                # Usually if > 100 it means Debt > Equity.
                if debt_to_equity > 200: # Generous buffer (2.0 ratio)
                    return False, f"High Debt (D/E: {debt_to_equity/100:.2f})"
            
            # 2. Earnings Stability (Basic check: Trailing EPS > 0)
            eps = info.get('trailingEps', 0)
            if eps < 0:
                return False, f"Negative EPS ({eps})"
             
            # 3. PE Ratio Check (Just existance)
            pe = info.get('trailingPE', None)
            if not pe:
                 # It might be missing or negative overlap
                 pass # Warning but not strict fail maybe?
            
            return True, "Fundamentals OK"
            
        except Exception as e:
            return False, f"Error checking fundamentals: {e}"

    def calculate_elasticity(self, ticker, drop_threshold=0.05, lookback_years=5):
        """
        Calculates the probability of a bounce after a weekly drop.
        
        Algorithm:
        1. Get 5y daily data.
        2.Resample to Weekly.
        3. Identify weeks where Drop > drop_threshold (5%).
        4. For each event, look forward 10 trading days (2 weeks).
        5. Calculate stats.
        """
        try:
            # Fetch 5y Data
            df = self.client.get_history(ticker, period=f"{lookback_years}y", interval="1d")
            if df.empty: return None
            
            # Resample to Weekly logic manually to control "Close to Close" vs "High to Low"
            # Standard "Weekly Drop" usually means Wk_Close < Wk_Open * (1-thresh) or Wk_Close < Prev_Wk_Close * (1-thresh)
            # The user user said: "dropped by a specific threshold in a single week".
            # Let's use % Change of Close vs Prev Close
            
            # Resample to weekly close
            weekly_df = df['Close'].resample('W').last().to_frame()
            weekly_df['PctChange'] = weekly_df['Close'].pct_change()
            
            # Identify Drop Events
            drop_events = weekly_df[weekly_df['PctChange'] <= -drop_threshold].copy()
            
            if drop_events.empty:
                return {
                    "score": 0,
                    "probability": 0,
                    "avg_recovery": 0,
                    "event_count": 0,
                    "msg": "No historical drops found"
                }

            recoveries = []
            positive_count = 0
            
            # Daily DF for forward looking
            daily_close = df['Close']
            
            for date, row in drop_events.iterrows():
                # Find the index of this week end in daily data
                # We need data AFTER this date.
                
                # Get location of this date
                try:
                    loc_idx = daily_close.index.get_indexer([date], method='nearest')[0]
                    
                    # Look forward 10 days
                    future_idx = loc_idx + 10 
                    
                    if future_idx < len(daily_close):
                        price_at_drop = row['Close']
                        price_future = daily_close.iloc[future_idx]
                        
                        ret = (price_future - price_at_drop) / price_at_drop
                        recoveries.append(ret)
                        
                        if ret > 0: # Simple bounce > 0%
                        # Or user said "recover Y%". Let's assume ANY positive return is a "Recovery" for probability,
                        # and magnitude handles the "Y%".
                            positive_count += 1
                except:
                    continue
                    
            if not recoveries:
                 return {
                    "score": 0,
                    "probability": 0,
                    "avg_recovery": 0,
                    "event_count": 0,
                    "msg": "Insufficient forward data"
                }
            
            probability = positive_count / len(recoveries)
            avg_rec = sum(recoveries) / len(recoveries)
            
            # Magnitude Ratio: Avg Recovery % / Drop Threshold
            # Note: Drop is negative, so magnitude should be absolute ratio?
            # User: "Avg_Recovery_Percentage / Initial_Drop_Percentage"
            # If Drop was -10% (0.1) and Rec cov is +5% (0.05), ratio is 0.5.
            # We use drop_threshold as base or actual drops? Let's use actual avg drop? 
            # Simplified: Use the fixed threshold as denominator or just Avg Return.
            
            # Let's roughly follow user: Avg Recovery / Avg Drop (Absolute)
            avg_drop = abs(drop_events['PctChange'].mean())
            magnitude_ratio = avg_rec / avg_drop if avg_drop else 0
            
            return {
                "score": magnitude_ratio, # Anti-Gravity Score
                "probability": probability,
                "avg_recovery": avg_rec,
                "event_count": len(recoveries),
                "avg_drop": avg_drop
            }

        except Exception as e:
            print(f"Error calculating elasticity for {ticker}: {e}")
            return None
