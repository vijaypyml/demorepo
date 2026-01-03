import pandas as pd
import numpy as np
import nsepython as nse
from datetime import datetime, timedelta
import streamlit as st

class FIIDIIManager:
    
    @staticmethod
    def fetch_daily_activity():
        """
        Fetches the latest FII/DII stats from NSE.
        Returns a dictionary or None.
        """
        try:
            # Try getting raw data
            # nse_fii_dii() returns a list of dictionaries usually
            data = nse.nse_fii_dii()
            return data
        except Exception as e:
            print(f"Error fetching FII/DII data: {e}")
            return None

    @staticmethod
    def get_historical_data(timeframe="Daily"):
        """
        Generates realistic historical data for FII/DII trends.
        Since public APIs often block deep historical queries, we simulate this 
        based on realistic market patterns for demonstration.
        
        Timeframe: Daily, Weekly, Monthly, Yearly
        """
        days = 365 if timeframe == "Daily" else 365*2 # 1 or 2 years of context
        dates = pd.date_range(end=datetime.today(), periods=days, freq='B') # Business days
        
        # Base trends
        np.random.seed(42)
        trend = np.linspace(18000, 24500, days) + np.random.normal(0, 200, days)
        
        # Simulate Flows correlated to trend
        # FIIs tend to follow momentum, DIIs often contrarian
        fii_flows = []
        dii_flows = []
        market_prices = []
        
        price = trend[0]
        
        for i in range(days):
            # Random Shock
            shock = np.random.normal(0, 100)
            
            # FII Flow (Random + Momentum)
            fii_net = np.random.normal(0, 1500) + (shock * 5)
            
            # DII Flow (Counter-balance FII often)
            dii_net = np.random.normal(0, 1200) - (fii_net * 0.4) 
            
            # Price Impact
            net_flow = fii_net + dii_net
            price_change = (net_flow / 50000) * price * 0.05 # Simple impact model
            price = price * (1 + (np.random.normal(0, 0.005))) + (shock/10)
            
            # Adjust price to stay somewhat tethered to the "trend" baseline to avoid random walk wandering too far
            price = (price * 0.95) + (trend[i] * 0.05)
            
            fii_flows.append(fii_net)
            dii_flows.append(dii_net)
            market_prices.append(price)
            
        df = pd.DataFrame({
            'Date': dates,
            'FII Net': fii_flows,
            'DII Net': dii_flows,
            'Nifty Price': market_prices
        })
        
        # Resampling based on Timeframe
        if timeframe == "Weekly":
            df = df.resample('W', on='Date').agg({
                'FII Net': 'sum',
                'DII Net': 'sum',
                'Nifty Price': 'last'
            }).reset_index()
            
        elif timeframe == "Monthly":
            df = df.resample('M', on='Date').agg({
                'FII Net': 'sum',
                'DII Net': 'sum',
                'Nifty Price': 'last'
            }).reset_index()
            
        elif timeframe == "Yearly":
            df = df.resample('Y', on='Date').agg({
                'FII Net': 'sum',
                'DII Net': 'sum',
                'Nifty Price': 'last'
            }).reset_index()
            
        return df

    @staticmethod
    def get_market_verdict(df):
        """Generates a text verdict based on recent flows."""
        if df.empty: return "No Data"
        
        recent = df.iloc[-1]
        fii = recent['FII Net']
        dii = recent['DII Net']
        
        if fii > 0 and dii > 0:
            return "🚀 Bullish: Broad Buying Support"
        elif fii < 0 and dii < 0:
            return "🐻 Bearish: Broad Selling Pressure"
        elif fii > 0 and dii < 0:
            return "📈 FII Driven Rally (DII Profit Booking)"
        else:
            return "🛡️ DII Supporting Market (FII Selling)"
