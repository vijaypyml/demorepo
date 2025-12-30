import streamlit as st
import pandas as pd
import plotly.express as px
from analysis.portfolio_manager import PortfolioManager

def render_portfolio_tab():
    st.header("📊 Market Portfolio Study")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.expander("⚙️ Portfolio Settings", expanded=True):
            st.subheader("Configuration")
            
            # User Limit Input: Years
            years = st.number_input("Analysis Duration (Years)", min_value=1, max_value=20, value=2)
            period = f"{years}y"
            
            # Default Tickers
            default_tickers_map = {
                "^NSEI": "Nifty 50",
                "GC=F": "Gold",
                "SI=F": "Silver",
                "SETF10GILT.NS": "SBI 10Yr Gilt (Bonds)"
            }
            
            # Additional Known Tickers for mapping
            known_tickers_map = {
                "AAPL": "Apple",
                "MSFT": "Microsoft", 
                "GOOG": "Google",
                "TSLA": "Tesla",
                "BTC-USD": "Bitcoin",
                "ETH-USD": "Ethereum",
                "^TNX": "US 10Y Yield",
                "RELIANCE.NS": "Reliance Ind",
                "TCS.NS": "TCS",
                "INFY.NS": "Infosys",
                "HDFCBANK.NS": "HDFC Bank"
            }
            
            full_ticker_map = {**default_tickers_map, **known_tickers_map}
            
            default_tickers = list(default_tickers_map.keys())
            
            # User Input: Tickers
            # Ensure session state for multiselect key exists if not already
            if "portfolio_ticker_select" not in st.session_state:
                st.session_state["portfolio_ticker_select"] = default_tickers

            tickers = st.multiselect(
                "Select Assets for Portfolio",
                options=default_tickers + ["AAPL", "MSFT", "GOOG", "TSLA", "BTC-USD", "ETH-USD", "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
                default=default_tickers,
                format_func=lambda x: full_ticker_map.get(x, x),
                key="portfolio_ticker_select"
            )
            
            # Allow custom tickers
            custom_tickers = st.text_input("Add Custom Tickers (comma separated, e.g. INFY.NS, TCS.NS)")
            if custom_tickers:
                custom_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]
                tickers.extend(custom_list)
                # Remove duplicates while preserving order
                tickers = list(dict.fromkeys(tickers))
            
            # User Input: Capital
            capital = st.number_input("Total Capital (INR)", min_value=1000.0, value=100000.0, step=1000.0)
            
            # User Input: Risk Profile
            risk_profile = st.selectbox(
                "Risk Profile",
                ["Conservative", "Moderate", "Aggressive"],
                index=1,
                help="Conservative: Minimize Volatility. Aggressive: Maximize Sharpe/Return."
            )
        
        if st.button("Analyze & Optimize Portfolio", type="primary"):
            if not tickers:
                st.warning("Please select at least one asset.")
                return

            with st.spinner(f"Fetching {period} data and optimizing..."):
                pm = PortfolioManager(tickers)
                pm.fetch_data(period=period)
                
                if pm.data.empty:
                    st.error("Could not fetch data for the selected tickers.")
                    return
                
                # 1. Metrics
                risk_metrics, effective_years, start_date, end_date = pm.calculate_risk_metrics()
                
                # Check for significant deviation from requested period
                # requested 'years' vs 'effective_years'
                if abs(years - effective_years) > 0.5:
                    limiting_names = [full_ticker_map.get(t, t) for t in pm.limiting_tickers]
                    msg = f"**Note:** Effective Analysis Period is **{effective_years:.1f} years** ({start_date.date()} to {end_date.date()}) due to limited data availability."
                    if limiting_names:
                        msg += f" Limited by: **{', '.join(limiting_names)}**."
                    st.warning(msg)
                    
                    # Offer to remove limiting tickers
                    if pm.limiting_tickers:
                        st.subheader("Remove Limiting Assets?")
                        cols = st.columns(len(pm.limiting_tickers))
                        for idx, ticker in enumerate(pm.limiting_tickers):
                             with cols[idx]:
                                 if st.button(f"Remove {full_ticker_map.get(ticker, ticker)}"):
                                     if ticker in st.session_state["portfolio_ticker_select"]:
                                         st.session_state["portfolio_ticker_select"].remove(ticker)
                                         st.rerun()
                else:
                    st.success(f"Analysis Period: {start_date.date()} to {end_date.date()} ({effective_years:.1f} years)")
                
                # 2. Allocation
                allocation = pm.allocate_capital(capital, risk_profile)
                
                # Store in session state to persist across reruns if needed (or just render directly)
                st.session_state['portfolio_metrics'] = risk_metrics
                st.session_state['portfolio_allocation'] = allocation
                st.session_state['portfolio_manager'] = pm
                st.session_state['ticker_map'] = full_ticker_map
                # Persist metadata for CAGR calculation
                st.session_state['effective_years'] = effective_years
                st.session_state['start_date'] = start_date
                st.session_state['end_date'] = end_date
    
    # Render Output if available
    if 'portfolio_manager' in st.session_state:
        pm = st.session_state['portfolio_manager']
        risk_metrics = st.session_state.get('portfolio_metrics', pd.DataFrame())
        allocation = st.session_state.get('portfolio_allocation', {})
        current_map = st.session_state.get('ticker_map', {})
        effective_years = st.session_state.get('effective_years', 0)
        
        with col2:
            st.subheader("Asset Performance Metrics")
            
            # Use mapped names for display if verification passes
            display_metrics = risk_metrics.copy()
            display_metrics.index = [current_map.get(t, t) for t in display_metrics.index]
            
            st.dataframe(display_metrics.style.highlight_max(axis=0, color='lightgreen').highlight_min(axis=0, color='lightcoral'))
            
            st.subheader(f"Optimized Allocation ({risk_profile})")
            
            # Display Allocation Table
            alloc_df = pd.DataFrame(list(allocation.items()), columns=['Asset', 'Allocation'])
            alloc_df['Asset Name'] = alloc_df['Asset'].map(lambda x: current_map.get(x, x))
            alloc_df['Percentage'] = (alloc_df['Allocation'] / capital) * 100
            
            # Merge with metrics to get Total Return / CAGR
            # metrics index is ticker
            metrics_df = risk_metrics.copy()
            
            # Map metrics to allocation
            alloc_df['CAGR (%)'] = alloc_df['Asset'].map(metrics_df['CAGR (%)'])
            alloc_df['Total Return (%)'] = alloc_df['Asset'].map(metrics_df['Total Return (%)'])
            
            # Calculate Projected Value
            alloc_df['Projected Value'] = alloc_df['Allocation'] * (1 + alloc_df['Total Return (%)'] / 100)
            alloc_df['Profit'] = alloc_df['Projected Value'] - alloc_df['Allocation']
            
            # Total Stats
            total_projected = alloc_df['Projected Value'].sum()
            total_profit = alloc_df['Profit'].sum()
            portfolio_abs_return_pct = (total_profit / capital) * 100
            
            # Calculate Portfolio CAGR
            # (End / Start)^(1/years) - 1
            # End = total_projected, Start = capital
            if effective_years > 0:
                portfolio_cagr = (total_projected / capital) ** (1/effective_years) - 1
                portfolio_cagr_pct = portfolio_cagr * 100
            else:
                portfolio_cagr_pct = 0.0

            # Add Total Row
            total_row = pd.DataFrame([{
                'Asset Name': '<b>TOTAL Portfolio</b>', 
                'Allocation': capital,
                'Percentage': 100.0,
                'CAGR (%)': portfolio_cagr_pct,
                'Total Return (%)': portfolio_abs_return_pct,
                'Projected Value': total_projected,
                'Profit': total_profit
            }])
            
            # Define columns order
            display_cols = ['Asset Name', 'Allocation', 'Percentage', 'CAGR (%)', 'Total Return (%)', 'Projected Value', 'Profit']
            
            # Concat
            final_df = pd.concat([alloc_df[display_cols], total_row[display_cols]], ignore_index=True)
            
            # Rename for display clarity
            final_df.rename(columns={'Total Return (%)': 'Abs. Return (%)'}, inplace=True)

            # Format
            st.write("### Allocation & Backtest Performance")
            st.dataframe(
                final_df.set_index('Asset Name').style.format({
                    'Allocation': '₹{:.2f}', 
                    'Percentage': '{:.1f}%',
                    'CAGR (%)': '{:.2f}%',
                    'Abs. Return (%)': '{:.2f}%',
                    'Projected Value': '₹{:.2f}',
                    'Profit': '₹{:.2f}'
                }).applymap(lambda x: 'font-weight: bold', subset=pd.IndexSlice['<b>TOTAL Portfolio</b>', :])
            )
            
            st.metric("Total Projected Value", f"₹{total_projected:,.2f}", 
                      delta=f"₹{total_profit:,.2f} (Abs: {portfolio_abs_return_pct:.1f}%, CAGR: {portfolio_cagr_pct:.1f}%)")
            
            # Correlation Matrix
            st.divider()
            fig_corr = pm.plot_correlation_matrix(ticker_map=current_map)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
            
        st.divider()
        
        # Charts
        st.subheader("Visualizations")
        c1, c2 = st.columns(2)
        
        # Pass ticker_map to plot_portfolio
        fig_donut, fig_bar = pm.plot_portfolio(allocation, risk_metrics, ticker_map=current_map)
        
        with c1:
            st.plotly_chart(fig_donut, use_container_width=True)
            
        with c2:
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # Line Charts (Normalized & Raw)
        fig_norm, fig_raw = pm.plot_performance_charts(ticker_map=current_map)
        
        if fig_norm:
            st.plotly_chart(fig_norm, use_container_width=True)
            
        if fig_raw:
            st.plotly_chart(fig_raw, use_container_width=True)
            
        # Drawdown Chart
        fig_dd = pm.plot_drawdown_chart(ticker_map=current_map)
        if fig_dd:
            st.plotly_chart(fig_dd, use_container_width=True)
