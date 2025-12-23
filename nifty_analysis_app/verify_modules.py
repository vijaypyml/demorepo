import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from data_mcp.tools import get_stock_price_history, get_stock_fundamentals, get_nifty_tickers
from analysis.technicals import calculate_technicals
from analysis.backtest import run_backtest
from analysis.seasonality import analyze_seasonality

def verify():
    print("Verifying Project Modules...")
    
    # 1. Test Data Fetching
    print("1. Testing Data Fetching (TCS.NS)...")
    try:
        df = get_stock_price_history("TCS.NS", period="1mo")
        if df.empty:
            print("   WARNING: DataFrame is empty!")
        else:
            print(f"   Success. Rows fetched: {len(df)}")
            
        info, financials = get_stock_fundamentals("TCS.NS")
        if not info:
            print("   WARNING: Info is empty.")
        else:
            print("   Success. Info fetched.")
    except Exception as e:
        print(f"   FAILED: {e}")
        return

    # 2. Test Technicals
    print("\n2. Testing Technicals...")
    try:
        df_tech = calculate_technicals(df)
        if 'SMA_50' in df_tech.columns:
            print("   Success. SMA_50 Calculated.")
        else:
            print("   FAILED: SMA_50 missing.")
    except Exception as e:
        print(f"   FAILED: {e}")

    # 3. Test Backtest
    print("\n3. Testing Backtest...")
    try:
        res = run_backtest(df_tech, "RSI_Bounds")
        print(f"   Success. Return: {res['cumulative_return']}")
    except Exception as e:
        print(f"   FAILED: {e}")

    # 4. Test Seasonality
    print("\n4. Testing Seasonality...")
    try:
        sl = analyze_seasonality(df_tech)
        print(f"   Success. Seasonality rows: {len(sl)}")
    except Exception as e:
        print(f"   FAILED: {e}")

if __name__ == "__main__":
    verify()
