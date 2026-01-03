import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from analysis.fii_dii import FIIDIIManager

def render_fii_dii_tab():
    st.header("🏦 Institutional Activity (FII/DII)")
    
    # 1. Timeframe Selection
    timeframe = st.selectbox("Select Timeframe", ["Daily", "Weekly", "Monthly", "Yearly"], index=0)
    
    # Fetch Data
    with st.spinner(f"Fetching {timeframe} Institutional Data..."):
        df = FIIDIIManager.get_historical_data(timeframe)
        
    if df.empty:
        st.error("No data available.")
        return

    # 2. Key Insights
    st.divider()
    latest = df.iloc[-1]
    last_date = latest['Date'].strftime('%d-%b-%Y')
    
    fii_net = latest['FII Net']
    dii_net = latest['DII Net']
    total_flow = fii_net + dii_net
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Date", last_date)
    col1.caption(FIIDIIManager.get_market_verdict(df))
    
    col2.metric("FII Net Flow", f"₹ {fii_net:,.0f} Cr", delta=fii_net, delta_color="normal")
    col3.metric("DII Net Flow", f"₹ {dii_net:,.0f} Cr", delta=dii_net, delta_color="normal")
    col4.metric("Total Institutional", f"₹ {total_flow:,.0f} Cr", delta=total_flow, delta_color="normal")
    
    # 3. Charts
    st.divider()
    
    # Chart 1: Net Flows Comparison
    st.subheader(f"📊 {timeframe} Net Flows: FII vs DII")
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=df['Date'], y=df['FII Net'], name='FII Net', marker_color='red'))
    fig_bar.add_trace(go.Bar(x=df['Date'], y=df['DII Net'], name='DII Net', marker_color='blue'))
    fig_bar.update_layout(barmode='group', xaxis_title="Date", yaxis_title="Net Flow (₹ Cr)", hovermode="x unified")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Chart 2: Market Correlation (Flow vs Nifty)
    st.subheader(f"📈 Market Reaction: Impact on Nifty 50")
    
    fig_dual = go.Figure()
    
    # Bar for Total Flow
    fig_dual.add_trace(go.Bar(x=df['Date'], y=df['FII Net'] + df['DII Net'], name='Total Inst. Flow', marker_color='gray', opacity=0.3))
    
    # Line for Nifty
    fig_dual.add_trace(go.Scatter(x=df['Date'], y=df['Nifty Price'], name='Nifty 50', mode='lines', line=dict(color='purple', width=2), yaxis='y2'))
    
    fig_dual.update_layout(
        xaxis_title="Date",
        yaxis=dict(title="Net Flow (₹ Cr)"),
        yaxis2=dict(title="Nifty 50 Level", overlaying='y', side='right'),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_dual, use_container_width=True)
    
    # 4. Data Table
    with st.expander("View Historical Data"):
        st.dataframe(df.sort_values('Date', ascending=False).style.format({
            'FII Net': "{:,.2f}",
            'DII Net': "{:,.2f}",
            'Nifty Price': "{:,.2f}"
        }), use_container_width=True)
