
import streamlit as st
import pandas as pd
from analysis.scanner import MarketScanner
from analysis.antigravity import AntiGravityAnalyzer

def render_market_pulse_view():
    st.header("Market Pulse & Anti-Gravity 🍏")
    
    st.markdown("""
    **Weekly Swing Analysis Report**: Identify "Top Losers" that are fundamentally strong and scientifically oversold.
    """)
    
    # Initialize Scanner
    scanner = MarketScanner()
    
    # 1. The Scan (Button to trigger because it might be slow)
    if st.button("Run Market Scan (Nifty 500)"):
        with st.spinner("Scanning the market... this may take a moment"):
            scan_results = scanner.get_market_pulse()
            st.session_state['scan_results'] = scan_results
    
    scan_results = st.session_state.get('scan_results', None)
    
    if scan_results:
        # --- Section A: Market Pulse ---
        st.subheader("1. The Market Pulse (The 'What')")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("Weekly Leaders (Last 5 Days)")
            st.dataframe(scan_results.get('weekly_gainers'), hide_index=True)
            
            st.caption("Monthly Leaders (Last 30 Days)")
            st.dataframe(scan_results.get('monthly_gainers'), hide_index=True)

        with col2:
            st.caption("Weekly Laggards (Potential Opportunities)")
            st.dataframe(scan_results.get('weekly_losers'), hide_index=True)
            
            st.caption("Monthly Laggards")
            st.dataframe(scan_results.get('monthly_losers'), hide_index=True)

        st.divider()
        
        # --- Section B & C: Anti-Gravity Analysis ---
        st.subheader("2. Anti-Gravity Candidates 🍏")
        st.markdown("Filtering 'Weekly Losers' for Quality + Statistical Bounce Probability.")
        
        weekly_losers = scan_results.get('weekly_losers')
        full_data = scan_results.get('full_data') # Ensure we have this if needed
        
        if weekly_losers is not None and not weekly_losers.empty:
            analyzer = AntiGravityAnalyzer()
            candidates = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total = len(weekly_losers)
            
            for i, row in weekly_losers.iterrows():
                ticker = row['Ticker']
                status_text.text(f"Analyzing {ticker}...")
                
                # 1. Fundamental Filter
                is_quality, reason = analyzer.check_fundamentals(ticker)
                
                if is_quality:
                    # 2. Anti-Gravity Math
                    elasticity = analyzer.calculate_elasticity(ticker)
                    
                    if elasticity and elasticity['event_count'] > 0:
                        candidates.append({
                            "Stock": ticker,
                            "Drop %": f"{row['1W %']:.1f}%",
                            "Funda": "✅ Strong",
                            "Hist. Bounce Prob": f"{elasticity['probability']:.0%}",
                            "Exp. 2-Wk Recov": f"{elasticity['avg_recovery']*100:.1f}%",
                            "Anti-Gravity Score": f"{elasticity['score']:.2f}",
                            "Events": elasticity['event_count']
                        })
                    else:
                         candidates.append({
                            "Stock": ticker,
                            "Drop %": f"{row['1W %']:.1f}%",
                            "Funda": "✅ Strong",
                            "Hist. Bounce Prob": "N/A",
                            "Exp. 2-Wk Recov": "-",
                            "Anti-Gravity Score": "0.00",
                            "Events": 0
                        })
                else:
                    # Optional: Show rejected ones? Maybe separate list.
                    # For report, we want top picks.
                    pass
                
                progress_bar.progress((i + 1) / total)
            
            status_text.empty()
            progress_bar.empty()
            
            if candidates:
                st.success(f"Identified {len(candidates)} Quality Candidates from Weekly Losers.")
                df_candidates = pd.DataFrame(candidates)
                st.dataframe(df_candidates, hide_index=True)
                
                st.info("""
                **Strategy:**
                1. **Trigger**: Stock is a Weekly Loser (>5% drop).
                2. **Filter**: Fundamentals are solid (Debt < 1, Positive Earnings).
                3. **Confirmation**: High Bounce Probability (>70%) & Score (>0.5).
                4. **Entry**: Mean Reversion setup.
                """)
            else:
                st.warning("No candidates passed the fundamental quality filter.")
        else:
            st.info("No weekly losers found to analyze.")
            
    else:
        st.info("Click 'Run Market Scan' to generate the report.")
