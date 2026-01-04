
import yfinance as yf
import pandas as pd
import os

def get_universe():
    try:
        # Try to load Nifty 500 from CSV
        # Adjusted path for running from app root d:\Vijay GCP\demorepo\nifty_analysis_app
        csv_path = os.path.join("data_mcp", "nifty500.csv")
        
        print(f"Checking CSV at: {os.path.abspath(csv_path)}")
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print(f"CSV Columns: {df.columns.tolist()}")
            if 'Symbol' in df.columns:
                tickers = df['Symbol'].tolist()
                return [f"{t}.NS" if not str(t).endswith('.NS') else t for t in tickers]
            elif 'SYMBOL' in df.columns:
                tickers = df['SYMBOL'].tolist()
                return [f"{t}.NS" if not str(t).endswith('.NS') else t for t in tickers]
        else:
            print("CSV not found.")
            
        return ["RELIANCE.NS", "TCS.NS", "INFY.NS"] # Fallback
    except Exception as e:
        print(f"Error loading universe: {e}")
        return ["RELIANCE.NS"]

def scan():
    tickers = get_universe()
    print(f"Loaded {len(tickers)} tickers.")
    if not tickers: return
    
    # Test with top 5
    tickers = tickers[:5]
    print(f"Scanning: {tickers}")
    
    try:
        data = yf.download(tickers, period="2mo", interval="1d", group_by='ticker', threads=True, progress=False)
        print("Data Downloaded.")
        print(f"Data Shape: {data.shape}")
        print(f"Data Columns: {data.columns}")
        
        results = []
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                   df = data
                else:
                   df = data[ticker]
                
                print(f"Processing {ticker}...")
                print(df.tail())
                
                vol_col = 'Volume'
                close_col = 'Adj Close'
                
                if close_col not in df.columns:
                    close_col = 'Close'

                if df.empty:
                    print("Empty DF")
                    continue
                
                curr_price = df[close_col].iloc[-1]
                avg_vol = df[vol_col].tail(20).mean()
                
                print(f"Price: {curr_price}, Vol: {avg_vol}")
                
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    scan()
