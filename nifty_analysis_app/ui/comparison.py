import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_mcp.tools import get_stock_fundamentals, get_stock_price_history
from analysis.fundamentals import analyze_fundamentals

def render_comparison_view(sym1, sym2):
    if not sym1 or not sym2:
        st.error("Need two tickers to compare.")
        return

    st.subheader(f"⚔️ Comparison: {sym1} vs {sym2}")
    
    # --- PRICE PERFORMANCE CHART ---
    st.subheader("Comparative Chart")
    
    metric = st.selectbox("Metric to Plot", ["Relative Return", "RSI", "Closing Price"])
    
    # Fetch histories
    df1 = get_stock_price_history(sym1, period="1y")
    df2 = get_stock_price_history(sym2, period="1y")
    
    if not df1.empty and not df2.empty:
        # Calculate Correlation
        # align indices
        combined = pd.DataFrame({'s1': df1['Close'], 's2': df2['Close']}).dropna()
        corr = combined['s1'].pct_change().corr(combined['s2'].pct_change())
        
        st.metric(f"Correlation (Daily Returns) - {sym1} vs {sym2}", f"{corr:.2f}")

        fig = go.Figure()
        
        if metric == "Relative Return":
            # Normalize to start at 0%
            df1['Norm'] = (df1['Close'] / df1['Close'].iloc[0]) - 1
            df2['Norm'] = (df2['Close'] / df2['Close'].iloc[0]) - 1
            
            fig.add_trace(go.Scatter(x=df1.index, y=df1['Norm'], name=sym1, line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df2.index, y=df2['Norm'], name=sym2, line=dict(color='orange')))
            fig.update_layout(yaxis_tickformat='.0%', title="Cumulative Return (1 Year)")

        elif metric == "RSI":
            import ta
            # Calculate RSI
            df1['RSI'] = ta.momentum.rsi(df1['Close'], window=14)
            df2['RSI'] = ta.momentum.rsi(df2['Close'], window=14)
            
            fig.add_trace(go.Scatter(x=df1.index, y=df1['RSI'], name=sym1, line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df2.index, y=df2['RSI'], name=sym2, line=dict(color='orange')))
            
            # Add 70/30 lines
            fig.add_hline(y=70, line_dash="dash", line_color="gray")
            fig.add_hline(y=30, line_dash="dash", line_color="gray")
            fig.update_layout(title="Relative Strength Index (14)")

        elif metric == "Closing Price":
             fig.add_trace(go.Scatter(x=df1.index, y=df1['Close'], name=sym1, line=dict(color='blue')))
             fig.add_trace(go.Scatter(x=df2.index, y=df2['Close'], name=sym2, line=dict(color='orange')))
             fig.update_layout(title="Closing Price")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not fetch price history for comparison.")

def display_key_metrics(info):
    pass # Deprecated for now based on user request to keep only chart
