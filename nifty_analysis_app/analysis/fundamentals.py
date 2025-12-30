import pandas as pd
import numpy as np

def generate_investment_memo(ticker, info, financials):
    """
    Generates a comprehensive investment memo acting as a Senior Equity Research Analyst.
    """
    if not financials:
        return "Insufficient data to generate report. Financial statements are missing."
        
    if not info:
        info = {} # Fallback to empty if info failed

    income_stmt = financials.get('income_statement', pd.DataFrame())
    balance_sheet = financials.get('balance_sheet', pd.DataFrame())
    cash_flow = financials.get('cash_flow', pd.DataFrame())
    
    # Check if we have ANY data tables
    if income_stmt.empty and balance_sheet.empty and cash_flow.empty:
         return "Insufficient data to generate report. All financial tables are empty."

    # Pre-processing: ensure columns are datetime and sorted ascending
    try:
        def clean_df(df):
            if df.empty: return df
            df.columns = pd.to_datetime(df.columns)
            return df.sort_index(axis=1)

        income_stmt = clean_df(income_stmt)
        balance_sheet = clean_df(balance_sheet)
        cash_flow = clean_df(cash_flow)
    except Exception as e:
        return f"Error processing financial dates: {e}"

    # --- 1. Executive Summary & Verdict ---
    score = 0
    highlights = []
    lowlights = []
    
    # Revenue Growth Check
    rev_growth = info.get("revenueGrowth", 0)
    if rev_growth > 0.15:
        score += 2
        highlights.append(f"Strong top-line growth of {rev_growth:.1%}")
    elif rev_growth > 0.05:
        score += 1
    elif rev_growth < 0:
        score -= 1
        lowlights.append("Declining revenue trend")

    # Profitability Check
    profit_margin = info.get("profitMargins", 0)
    if profit_margin > 0.20:
        score += 2
        highlights.append(f"High profit margins of {profit_margin:.1%}")
    elif profit_margin < 0.05:
        score -= 1
        lowlights.append("Thinning profit margins")

    # Debt Check
    debt_equity = info.get("debtToEquity", 100)
    if isinstance(debt_equity, str): debt_equity = 100 # Fallback
    if debt_equity < 50:
        score += 1
        highlights.append(f"Conservative balance sheet (D/E: {debt_equity})")
    elif debt_equity > 150:
        score -= 1
        lowlights.append(f"Elevated leverage (D/E: {debt_equity})")

    verdict_text = "Stable"
    if score >= 4: verdict_text = "Strong Buy / Outperform"
    elif score >= 2: verdict_text = "Accumulate / Stable"
    elif score <= 0: verdict_text = "Distressed / Underperform"

    summary_section = f"""
### 1. Executive Summary
**Verdict: {verdict_text}**

**Highlights (Bullish):**
{chr(10).join([f"- {h}" for h in highlights]) if highlights else "- Stable operations with no major outliers."}

**Lowlights (Bearish):**
{chr(10).join([f"- {l}" for l in lowlights]) if lowlights else "- No significant immediate red flags."}
"""

    # --- 2. Income Statement Analysis ---
    inc_section = "### 2. Income Statement Analysis (Profitability & Growth)\n"
    if not income_stmt.empty and len(income_stmt.columns) >= 2:
        latest = income_stmt.iloc[:, -1]
        prev = income_stmt.iloc[:, -2]
        
        # Revenue
        rev_curr = latest.get("Total Revenue", 0)
        rev_prev = prev.get("Total Revenue", 0)
        rev_chg = (rev_curr - rev_prev) / rev_prev if rev_prev else 0
        inc_section += f"- **Revenue Trends**: Revenue {'grew' if rev_chg>0 else 'declined'} by {rev_chg:.1%} YoY.\n"
        
        # Margins
        gross = latest.get("Gross Profit", 0)
        op_income = latest.get("Operating Income", 0)
        net = latest.get("Net Income", 0)
        
        gross_margin = (gross / rev_curr) if rev_curr else 0
        op_margin = (op_income / rev_curr) if rev_curr else 0
        net_margin = (net / rev_curr) if rev_curr else 0
        
        inc_section += f"- **Margins**: Gross Margin: {gross_margin:.1%}, Operating Margin: {op_margin:.1%}, Net Margin: {net_margin:.1%}.\n"
    else:
        inc_section += "- Insufficient historical data for detailed trend analysis.\n"

    # --- 3. Balance Sheet Analysis ---
    bs_section = "### 3. Balance Sheet Analysis (Solvency & Liquidity)\n"
    if not balance_sheet.empty:
        latest_bs = balance_sheet.iloc[:, -1]
        
        total_cash = latest_bs.get("Cash And Cash Equivalents", 0)
        total_debt = latest_bs.get("Total Debt", 0)
        net_debt = total_debt - total_cash
        
        curr_assets = latest_bs.get("Current Assets", 0)
        curr_liab = latest_bs.get("Current Liabilities", 0)
        curr_ratio = (curr_assets / curr_liab) if curr_liab else 0
        
        bs_section += f"- **Financial Strength**: Cash: {format_currency(total_cash)}, Total Debt: {format_currency(total_debt)}. Net Debt: {format_currency(net_debt)}.\n"
        bs_section += f"- **Liquidity**: Current Ratio is {curr_ratio:.2f} ({'Healthy' if curr_ratio>1.5 else 'Tight' if curr_ratio<1 else 'Adequate'}).\n"
    
    # --- 4. Cash Flow Statement Analysis ---
    cf_section = "### 4. Cash Flow Statement Analysis (Cash Generation)\n"
    if not cash_flow.empty and not income_stmt.empty:
        latest_cf = cash_flow.iloc[:, -1]
        ocf = latest_cf.get("Operating Cash Flow", 0)
        capex = latest_cf.get("Capital Expenditure", 0)
        fcf = ocf + capex # Capex is usually negative
        
        net_income = income_stmt.iloc[:, -1].get("Net Income", 0)
        quality_ratio = (ocf / net_income) if net_income else 0
        
        cf_section += f"- **Quality of Earnings**: OCF/Net Income is {quality_ratio:.2f}. ({'High Quality' if quality_ratio > 1 else 'Low Quality - Aggressive Accounting?'}).\n"
        cf_section += f"- **Free Cash Flow**: The company generated {format_currency(fcf)} in FCF.\n"

    # --- 5. Key Fundamental Ratios ---
    roe = info.get("returnOnEquity", 0)
    roic = 0 # Need complex calc, skipping for now
    interest_coverage = "N/A" # Need Interest Expense
    
    ratios_section = f"""
### 5. Key Fundamental Ratios
| Ratio | Value | Interpretation |
| :--- | :--- | :--- |
| **ROE** | {roe:.1%} | {'Efficient use of equity' if roe > 0.15 else 'Low return'} |
| **Debt/Equity** | {debt_equity} | {'Leveraged' if debt_equity > 100 else 'Conservative'} |
| **P/E Ratio** | {info.get('trailingPE', 'N/A')} | Market Valuation |
"""

    # --- 6. Risks ---
    risks_section = "### 6. Risks & Red Flags\n"
    has_risks = False
    if score < 0:
        risks_section += "- **Summary**: Financial scoring logic indicates underperformance.\n"
        has_risks = True
    if debt_equity > 200:
        risks_section += "- **High Leverage**: Debt levels are concerningly high relative to equity.\n"
        has_risks = True
        
    if not has_risks:
        risks_section += "- No major red flags detected in the quantitative screening.\n"

    # --- 7. Final Verdict ---
    final_section = f"""
### 7. Final Verdict
**Rating: {verdict_text}**

Based on the analysis of the financial statements and key ratios, the company shows **{'strong' if score>=2 else 'weak' if score<=0 else 'stable'}** fundamentals.
- **Suitability**: {'Growth Investors' if rev_growth > 0.15 else 'Value/Dividend Investors' if profit_margin > 0 else 'Speculative'}
"""

    full_memo = summary_section + "\n" + inc_section + "\n" + bs_section + "\n" + cf_section + "\n" + ratios_section + "\n" + risks_section + "\n" + final_section
    return full_memo

def format_currency(val):
    if abs(val) >= 1e9:
        return f"{val/1e9:.2f}B"
    elif abs(val) >= 1e6:
        return f"{val/1e6:.2f}M"
    else:
        return f"{val:,.2f}"

# Keep the old simple function for backward compatibility if needed, using the new logic wrapper?
# Or just let the old function coexist if chat.py uses it. 
# For now, I'll update chat.py to use this NEW function if the user asks for "Fundamentals".
# But wait, chat.py uses `analyze_fundamentals`. I should probably rename/keep `analyze_fundamentals` for the simple chat summary 
# and use `generate_investment_memo` for the deep dive tab.

def analyze_fundamentals(ticker, info, financials):
    # This is the old function logic, kept for lightweight chat responses
    # Re-construct simple dict return
    # We can either parse the memo or just give a pointer.
    # For a better UX, let's give a pointer so we don't duplicate logic.
    
    return {
        "summary": "Full Investment Memo available in 'Fundamentals' tab.",
        "positives": ["See 'Fundamentals' tab for details."],
        "negatives": [],
        "metrics": {}
    }
