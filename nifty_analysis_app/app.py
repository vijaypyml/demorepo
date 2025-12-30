import streamlit as st
import pandas as pd
from ui.chat import render_chat
from ui.charts import render_charts, render_rsi
from ui.comparison import render_comparison_view
from ui.fundamentals_view import render_fundamentals_tab
from ui.seasonality_view import render_seasonality_tab
from data_mcp.tools import get_stock_price_history
from analysis.technicals import calculate_technicals
from analysis.backtest import run_backtest
from analysis.seasonality import analyze_seasonality
from ui.backtest_view import render_backtest_tab
from ui.portfolio_view import render_portfolio_tab

# Page Configuration
st.set_page_config(page_title="GreenChips Analytics", layout="wide", page_icon="assets/logo.png")

# Initialize Session State
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "^NSEI" # Default to Nifty 50

# Main Layout
st.title("GreenChips Analytics")

# --- SIDEBAR: Chatbot ---
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    render_chat()
    st.divider()
    st.subheader("⚙️ Settings")
    data_period = st.selectbox("Historical Data Period", ["1y", "2y", "5y", "10y", "max"], index=2)
    data_interval = st.selectbox("Chart Interval", ["1d", "1wk", "1mo"], index=0)

# --- MAIN AREA ---

# Standard Analysis View
ticker = st.session_state["selected_ticker"]
st.subheader(f"Analysis: {ticker}")

# Fetch Data
with st.spinner("Fetching data..."):
    # Default to 2y for better backtesting/seasonality context
    df = get_stock_price_history(ticker, period=data_period, interval=data_interval)

if not df.empty:
    # Calculate Indicators
    df = calculate_technicals(df)
    
    # Tabs for different Views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Charts", "Comparison", "Fundamentals", "Backtest", "Seasonality", "Portfolio Study"])
    
    # --- TAB 1: CHARTS ---
    with tab1:
        render_charts(ticker, df)
        # RSI Section
        render_rsi(df)
    
    # --- TAB 2: COMPARISON ---
    with tab2:
        st.subheader("Compare with another stock")
        
        # Default value from session state if set by chat
        default_compare = st.session_state.get("compare_ticker", "INFY.NS" if ticker != "INFY.NS" else "TCS.NS")
        
        comp_ticker = st.text_input("Enter Ticker to Compare", value=default_compare)
        
        if comp_ticker:
            # Ensure proper formatting if needed
            if not comp_ticker.endswith(".NS") and not comp_ticker.endswith(".BO") and comp_ticker != "^NSEI":
                 comp_ticker = f"{comp_ticker}.NS"
            
            render_comparison_view(ticker, comp_ticker)

    # --- TAB 3: FUNDAMENTALS ---
    with tab3:
        render_fundamentals_tab(ticker)
        
    # --- TAB 4: BACKTEST ---
    with tab4:
        render_backtest_tab(df)
            
    # --- TAB 5: SEASONALITY ---
    with tab5:
        render_seasonality_tab(df)

    # --- TAB 6: PORTFOLIO STUDY ---
    with tab6:
        render_portfolio_tab()

else:
    st.error(f"Could not fetch data for {ticker}. Please check the symbol.")
