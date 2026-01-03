
import nsepython as nse
import json

def debug_nse_structure():
    symbol = "RELIANCE"
    print(f"Fetching raw EQUITY quote for {symbol} via nsefetch...")
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        if hasattr(nse, 'nsefetch'):
            data = nse.nsefetch(url)
        else:
            print("nsefetch not found in nsepython module.")
            return

        # Print top level keys
        print("Keys found:", data.keys())
        
        # Check for specific keys we need
        print("\n--- Industry Info ---")
        print(json.dumps(data.get('industryInfo', {}), indent=2))
        
        print("\n--- Security Wise Trade Details ---")
        print(json.dumps(data.get('securityWiseTradeDetails', {}), indent=2))
        
        print("\n--- Metadata ---")
        print(json.dumps(data.get('metadata', {}), indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_nse_structure()
