
import pandas as pd
from analysis.fundamentals import generate_investment_memo
from data_mcp.nse_client import NSEClient

def test_nse_integration():
    TICKER = "RELIANCE.NS"
    print(f"Fetching data for {TICKER}...")
    
    # Mock Info (since we aren't using the real yahoo client just for this test, or we could)
    # Let's mock the info part but let NSEClient fetch the real nse data
    info = {
        "revenueGrowth": 0.12,
        "primaryExchange": "NSE",
        "trailingPE": 25.0, # Let's see if it compares to sector
        "currentPrice": 2400,
        "returnOnEquity": 0.12
    }
    
    # Mock Financials (Basic valid structure)
    cols = pd.to_datetime(['2023-03-31', '2024-03-31'])
    financials = {
        'income_statement': pd.DataFrame({'Total Revenue': [1000, 1100], 'Net Income': [100, 110]}, index=cols).T,
        'balance_sheet': pd.DataFrame({'Total Debt': [500, 500], 'Stockholders Equity': [1000, 1100]}, index=cols).T,
        'cash_flow': pd.DataFrame({'Operating Cash Flow': [120, 130], 'Capital Expenditure': [-50, -50]}, index=cols).T
    }

    # Generate Report
    print("\n--- GENERATING REPORT ---")
    report = generate_investment_memo(TICKER, info, financials)
    print(report)
    
    print("\n--- DIAGNOSTICS ---")
    print(f"Sector Data: {NSEClient.get_peer_comparison_data(TICKER)}")
    print(f"Delivery Data: {NSEClient.get_delivery_metrics(TICKER)}")

if __name__ == "__main__":
    test_nse_integration()
