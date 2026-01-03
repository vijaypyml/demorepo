import pandas as pd
import numpy as np
import math
from data_mcp.nse_client import NSEClient

def generate_investment_memo(ticker, info, financials):
    """
    Generates a comprehensive investment memo acting as a Senior Equity Research Analyst.
    Output is formatted as a Markdown Dashboard.
    """
    if not info: info = {}
    
    # --- Fetch NSE Context (Live) ---
    nse_data = NSEClient.get_peer_comparison_data(ticker)
    delivery_pct, delivery_qty = NSEClient.get_delivery_metrics(ticker)
    
    sector_pe = float(nse_data.get('sector_pe')) if nse_data.get('sector_pe') else None
    industry_name = nse_data.get('industry', 'Unknown')
    
    if not financials:
        return "Insufficient data to generate report. Financial statements are missing."

    income_stmt = financials.get('income_statement', pd.DataFrame())
    balance_sheet = financials.get('balance_sheet', pd.DataFrame())
    cash_flow = financials.get('cash_flow', pd.DataFrame())
    
    # Check if we have ANY data tables
    if income_stmt.empty and balance_sheet.empty and cash_flow.empty:
         return "Insufficient data to generate report. All financial tables are empty."

    # Pre-processing
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

    # --- Data Extraction Helpers ---
    latest_is = income_stmt.iloc[:, -1] if not income_stmt.empty else pd.Series()
    prev_is = income_stmt.iloc[:, -2] if not income_stmt.empty and len(income_stmt.columns) > 1 else pd.Series()
    
    latest_bs = balance_sheet.iloc[:, -1] if not balance_sheet.empty else pd.Series()
    latest_cf = cash_flow.iloc[:, -1] if not cash_flow.empty else pd.Series()

    # --- 1. The 4 Pillars Analysis & Scoring (0-10) ---
    
    # Pillar 1: Growth
    p1_score = 0
    growth_notes = []
    
    # Revenue Growth
    rev_curr = latest_is.get("Total Revenue", 0)
    rev_prev = prev_is.get("Total Revenue", 0)
    if rev_curr and rev_prev:
        yoy_growth = (rev_curr - rev_prev) / rev_prev
    else:
        yoy_growth = info.get("revenueGrowth", 0)

    rev_cagr_3y = info.get("revenueGrowth", 0) # Fallback if no deep history
    
    # Conflict Check
    trend_emoji = "➖"
    if yoy_growth > 0.15:
        p1_score += 4
        trend_emoji = "↗️"
        growth_notes.append(f"Strong YoY Growth: {yoy_growth:.1%}")
    elif yoy_growth > 0.05:
        p1_score += 2
        trend_emoji = "↗️"
        growth_notes.append(f"Moderate Growth: {yoy_growth:.1%}")
    elif yoy_growth < 0:
        p1_score -= 2
        trend_emoji = "↘️"
        growth_notes.append(f"Revenue Declining: {yoy_growth:.1%}")

    # Net Income Growth
    ni_curr = latest_is.get("Net Income", 0)
    ni_prev = prev_is.get("Net Income", 0)
    ni_growth = (ni_curr - ni_prev) / abs(ni_prev) if ni_prev else 0
    
    if ni_growth > 0.20: p1_score += 4
    elif ni_growth > 0.10: p1_score += 2
    
    # Cap score
    p1_score = min(10, max(0, p1_score + 2)) # Base 2

    # Pillar 2: Profitability
    p2_score = 0
    prof_notes = []
    
    gross_margin = (latest_is.get("Gross Profit", 0) / rev_curr) if rev_curr else 0
    net_margin = (ni_curr / rev_curr) if rev_curr else 0
    roe = info.get("returnOnEquity", 0)
    
    # Contextualize ROE
    if roe > 0.20:
        p2_score += 4
        prof_notes.append(f"Stellar ROE: {roe:.1%} (Premium)")
    elif roe > 0.15:
        p2_score += 3
        prof_notes.append(f"Solid ROE: {roe:.1%} (Good)")
    elif roe < 0.05:
        p2_score -= 1
        prof_notes.append(f"Weak ROE: {roe:.1%} (Lagging)")
        
    # Margins
    if net_margin > 0.15: p2_score += 3
    elif net_margin > 0.08: p2_score += 1
    
    p2_score = min(10, max(0, p2_score + 2))

    # Pillar 3: Financial Health
    p3_score = 0
    health_notes = []
    
    total_debt = latest_bs.get("Total Debt", 0)
    total_equity = latest_bs.get("Stockholders Equity", 1) # Avoid div/0
    debt_equity_ratio = total_debt / total_equity if total_equity else 100
    
    curr_assets = latest_bs.get("Current Assets", 0)
    curr_liab = latest_bs.get("Current Liabilities", 0)
    current_ratio = curr_assets / curr_liab if curr_liab else 0
    
    if debt_equity_ratio < 0.5:
        p3_score += 4
        health_notes.append("Fortress Balance Sheet (D/E < 0.5)")
    elif debt_equity_ratio < 1.0:
        p3_score += 2
        health_notes.append("Manageable Debt")
    elif debt_equity_ratio > 2.0:
        p3_score -= 2
        health_notes.append("High Leverage Warning")

    if current_ratio > 1.5: p3_score += 2
    elif current_ratio < 1.0: p3_score -= 2
    
    # OCF Coverage
    ocf = latest_cf.get("Operating Cash Flow", 0)
    if ocf > total_debt * 0.2: p3_score += 2 # Can pay 20% debt in 1 year
    
    p3_score = min(10, max(0, p3_score + 2))

    # Pillar 4: Valuation (Enhanced with NSE)
    p4_score = 0
    val_notes = []
    
    pe = info.get("trailingPE", None)
    peg = info.get("pegRatio", None)
    
    # Compare with Sector PE if available
    if pe and sector_pe:
        pe_discount = (pe - sector_pe) / sector_pe
        if pe_discount < -0.2:
            p4_score += 4; val_notes.append(f"Discount vs Sector (PE {pe:.1f}x vs {sector_pe:.1f}x)")
        elif pe_discount > 0.2:
            p4_score -= 2; val_notes.append(f"Premium vs Sector (PE {pe:.1f}x vs {sector_pe:.1f}x)")
        else:
            p4_score += 2; val_notes.append("In-line with Sector")
    elif pe:
        # Fallback to absolute check
        if pe < 15: p4_score += 4; val_notes.append("Undervalued (PE < 15)")
        elif pe < 25: p4_score += 2; val_notes.append("Fair Value (PE 15-25)")
        else: p4_score -= 2; val_notes.append("Premium Valuation (PE > 25)")
    
    if peg and peg < 1.0: p4_score += 3; val_notes.append("Growth at Reasonable Price (PEG < 1)")
    
    p4_score = min(10, max(0, p4_score + 3))

    # --- 2. Red Flags & Risks ---
    red_flags = []
    
    # Strict OCF/Net Income Rule
    quality_ratio = (ocf / ni_curr) if ni_curr else 0
    if quality_ratio < 0.7:
        red_flags.append(f"🛑 **Poor Earnings Quality**: OCF/Net Income is {quality_ratio:.2f} (< 0.7). Profit may be paper-only.")
        
    if debt_equity_ratio > 2.5:
        red_flags.append(f"⚠️ **Excessive Leverage**: Debt is {debt_equity_ratio:.1f}x Equity.")
        
    if yoy_growth < -0.05 and rev_cagr_3y > 0.05:
        red_flags.append("⚠️ **Growth Reversal**: Long-term trend is up, but short-term revenue is falling.")
        
    if delivery_pct < 0.20:
        red_flags.append(f"⚠️ **Low Delivery Volume**: Only {delivery_pct:.1%} marked for delivery (Speculative Interest).")

    # --- 3. Valuation & Verdict ---
    # Intrinsic Value Heuristic (Simplified DCF/Graham)
    intrinsic_val = 0
    margin_of_safety = 0
    val_method = "N/A"
    
    current_price = info.get("currentPrice", 0)
    eps = info.get("trailingEps", 0)
    book_val = info.get("bookValue", 1)
    
    if eps > 0 and book_val > 0:
        # Graham Number: Sqrt(22.5 * EPS * BVPS)
        try:
            graham_num = math.sqrt(22.5 * eps * book_val)
            intrinsic_val = graham_num
            val_method = "Graham Number"
        except: pass
    elif eps > 0 and yoy_growth > 0:
        # PEG Approximation: Fair PE = Growth Rate (capped at 30)
        fair_pe = min(yoy_growth * 100, 30)
        intrinsic_val = eps * fair_pe
        val_method = "PEG-implied"
        
    if intrinsic_val > 0 and current_price > 0:
        margin_of_safety = (intrinsic_val - current_price) / intrinsic_val

    # Final Score & Verdict
    total_score = p1_score + p2_score + p3_score + p4_score
    max_score = 40
    percentage_score = total_score / max_score
    
    if percentage_score > 0.75: 
        verdict = "STRONG BUY 🟢"
        verdict_desc = "High Conviction | Quality Compounder"
    elif percentage_score > 0.5: 
        verdict = "ACCUMULATE 🟡"
        verdict_desc = "Good Fundamentals | Fair Price"
    elif percentage_score > 0.3: 
        verdict = "HOLD 🟠"
        verdict_desc = "Watch Risks | Limited Upside"
    else: 
        verdict = "AVOID 🔴"
        verdict_desc = "deteriorating Fundamentals | Expensive"

    if red_flags and "STRONG BUY" in verdict:
        verdict = "ACCUMULATE (Risks Present) 🟡"

    # --- 4. Dashboard Construction ---
    
    # Conviction Badge
    conviction_badge = "🤔 Low Conviction"
    if delivery_pct > 0.60: conviction_badge = "💎 **High Conviction (Heavy Accumulation)**"
    elif delivery_pct > 0.40: conviction_badge = "🖐️ Moderate Conviction"
    
    dashboard = f"""
# 🏁 Analyst Verdict: {verdict}
**target:** {verdict_desc}  
**Intrinsic Value (~):** {format_currency(intrinsic_val)} ({val_method}) | **MoS:** {margin_of_safety:.1%}
**Market Conviction:** {conviction_badge} (Delivery: {delivery_pct:.1%})

---

## 🏛️ The 4 Pillars of Quality
| Pillar | Score (0-10) | Rating | Key Interaction |
| :--- | :--- | :--- | :--- |
| **Growth** | **{p1_score}**/10 | {get_rating_emoji(p1_score)} | {growth_notes[0] if growth_notes else 'Stable'} |
| **Profitability** | **{p2_score}**/10 | {get_rating_emoji(p2_score)} | {prof_notes[0] if prof_notes else 'Average Margins'} |
| **Health** | **{p3_score}**/10 | {get_rating_emoji(p3_score)} | {health_notes[0] if health_notes else 'Standard Leverage'} |
| **Valuation** | **{p4_score}**/10 | {get_rating_emoji(p4_score)} | {val_notes[0] if val_notes else 'Market Priced'} |

---

## 🚦 Risks & Red Flags
{chr(10).join([f"- {flag}" for flag in red_flags]) if red_flags else "✅ **Clean Scan**: No major quantitative red flags detected."}

---

## 📊 Deep Dive Data
### Key Ratios (Contextualized)
| Metric | Value | Industry/Benchmark | Verification |
| :--- | :--- | :--- | :--- |
| **P/E Ratio** | {pe if pe else 0:.1f}x | {f'{sector_pe:.1f}x' if sector_pe else 'N/A'} (Sector) | {get_context_label(pe, sector_pe, inverse=True) if sector_pe else 'N/A'} |
| **ROE** | {roe:.1%} | 15.0% | {get_context_label(roe, 0.15)} |
| **Current Ratio** | {current_ratio:.2f} | 1.50 | {get_context_label(current_ratio, 1.5)} |
| **Debt/Equity** | {debt_equity_ratio:.2f} | 1.00 | {get_context_label(debt_equity_ratio, 1.0, inverse=True)} |
| **Industry** | {industry_name} | - | - |

### Recent Trend (Last Reported)
- **Revenue**: {format_currency(rev_curr)} ({trend_emoji} {yoy_growth:+.1%})
- **Net Income**: {format_currency(ni_curr)} ({'↗️' if ni_growth>0 else '↘️'} {ni_growth:+.1%})
- **Free Cash Flow**: {format_currency(latest_cf.get('Operating Cash Flow', 0) + latest_cf.get('Capital Expenditure', 0))}

"""
    return {
        "dashboard": dashboard,
        "positives": growth_notes + prof_notes + health_notes + val_notes,
        "negatives": red_flags
    }

def get_rating_emoji(score):
    if score >= 8: return "🟢 Excellent"
    if score >= 6: return "🟢 Good"
    if score >= 4: return "🟡 Average"
    return "🔴 Weak"

def get_context_label(value, benchmark, inverse=False):
    if value is None or benchmark is None: return "N/A"
    try:
        diff = (value - benchmark) / benchmark
        if inverse: diff = -diff
        
        if diff > 0.2: return "✅ Premium/Strong"
        if diff < -0.2: return "🔻 Discount/Weak"
        return "➖ In-line"
    except: return "N/A"

def format_currency(val):
    try:
        val = float(val)
    except:
        return "N/A"
        
    if abs(val) >= 1e9:
        return f"{val/1e9:.2f}B"
    elif abs(val) >= 1e6:
        return f"{val/1e6:.2f}M"
    else:
        return f"{val:,.2f}"

def analyze_fundamentals(ticker, info, financials):
    # Simplified version for chat, or just redirect
    full_report = generate_investment_memo(ticker, info, financials)
    
    if isinstance(full_report, str):
        # Handle error case where string was returned
        return {
            "summary": full_report,
            "details": full_report,
            "positives": [],
            "negatives": []
        }
        
    return {
        "summary": f"Analyst Report for {ticker} generated (with Live NSE Data).",
        "details": full_report["dashboard"],
        "positives": full_report["positives"],
        "negatives": full_report["negatives"]
    }
