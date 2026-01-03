import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from analysis.option_chain import OptionChainAnalyzer

def render_options_tab():
    st.header("🎲 Option Chain Analytics")
    
    # 1. Inputs
    col1, col2 = st.columns([1, 2])
    with col1:
        instrument = st.selectbox("Select Instrument", ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "TCS.NS"])
    
    # Fetch Data
    with st.spinner(f"Fetching Option Chain for {instrument}..."):
        payload = OptionChainAnalyzer.fetch_option_chain(instrument)
        
        if not payload:
            st.error("Failed to fetch option chain data. Please try again later.")
            return

        # Expiry Selection
        expiry_dates = OptionChainAnalyzer.get_expiry_dates(payload)
        if not expiry_dates:
             st.error("No expiry dates found.")
             return
             
        selected_expiry = st.selectbox("Select Expiry Date", expiry_dates)
    
    # Process Data
    df, pcr, total_ce, total_pe, max_pain, spot_price = OptionChainAnalyzer.process_option_chain(payload, selected_expiry)
    
    if df.empty:
        st.warning("No data found for this expiry.")
        return

    # 2. Summary Dashboard
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Spot Price", f"{spot_price:,.2f}")
    
    pcr_color = "normal"
    pcr_delta = "Neutral"
    if pcr > 1.2: pcr_delta = "Bullish"; pcr_color = "inverse"
    elif pcr < 0.7: pcr_delta = "Bearish"; pcr_color = "off"
    
    m2.metric("PCR (Put/Call Ratio)", f"{pcr:.2f}", delta=pcr_delta, delta_color="normal" if pcr_delta=="Neutral" else "inverse" if pcr_delta=="Bullish" else "off") # off is red usually
    
    m3.metric("Max Pain", f"{max_pain:,.0f}")
    m4.metric("Total OI", f"{(total_ce + total_pe)/1e6:.2f} M")
    
    # 3. Charts
    st.subheader("📊 Open Interest Analysis")
    
    # Filter for relevant strikes (near spot)
    center_strike_idx = (df['Strike'] - spot_price).abs().idxmin()
    # Show +/- 10 strikes
    start_idx = max(0, center_strike_idx - 10)
    end_idx = min(len(df), center_strike_idx + 10)
    plot_df = df.iloc[start_idx:end_idx]
    
    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(x=plot_df['Strike'], y=plot_df['CE OI'], name='Call OI', marker_color='red'))
    fig_oi.add_trace(go.Bar(x=plot_df['Strike'], y=plot_df['PE OI'], name='Put OI', marker_color='green'))
    fig_oi.update_layout(title="Total Open Interest vs Strike", barmode='group', xaxis_title="Strike Price", yaxis_title="Open Interest")
    st.plotly_chart(fig_oi, use_container_width=True)
    
    # OI Change Chart
    st.subheader("📉 Change in Open Interest (Intraday Buildup)")
    fig_change = go.Figure()
    fig_change.add_trace(go.Bar(x=plot_df['Strike'], y=plot_df['CE Change OI'], name='Call OI Change', marker_color='salmon'))
    fig_change.add_trace(go.Bar(x=plot_df['Strike'], y=plot_df['PE Change OI'], name='Put OI Change', marker_color='lightgreen'))
    fig_change.update_layout(title="Change in OI vs Strike", barmode='group', xaxis_title="Strike Price", yaxis_title="OI Change")
    st.plotly_chart(fig_change, use_container_width=True)
    
    # 4. Data Table
    with st.expander("View Option Chain Data"):
        display_df = df[['CE OI', 'CE Change OI', 'CE LTP', 'Strike', 'PE LTP', 'PE Change OI', 'PE OI']]
        st.dataframe(display_df.style.background_gradient(subset=['CE OI', 'PE OI'], cmap="Blues"), use_container_width=True)
