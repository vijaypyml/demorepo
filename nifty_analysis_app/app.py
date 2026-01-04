import os
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
from ui.options import render_options_tab
from ui.fii_dii import render_fii_dii_tab
from ui.news_view import render_news_view

# Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

# Page Configuration
st.set_page_config(page_title="GreenChips Analytics", layout="wide", page_icon=LOGO_PATH)

# Custom CSS for Mobile Optimization
st.markdown("""
<style>
    /* Hide Streamlit Footer */
    /* Hide Streamlit Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide Deploy Button */
    .stDeployButton {
        display: none;
    }
    
    /* Adjust padding to prevent logo clipping */
    .block-container {
        padding-top: 3.5rem; /* Increased from 2rem to ~3.5rem */
        padding-bottom: 2rem;
    }
    
    /* Mobile friendly font sizes */
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
    }
    h3 {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "^NSEI" # Default to Nifty 50

# Main Layout
col_logo, col_title = st.columns([1, 15])
with col_logo:
    st.image(LOGO_PATH, use_container_width=True)
with col_title:
    st.title("Green Chips Analytics")

# --- SIDEBAR: Chatbot ---
with st.sidebar:
    render_chat()
    st.divider()
    st.subheader("⚙️ Settings")
    data_period = st.selectbox("Historical Data Period", ["1y", "2y", "5y", "10y", "max"], index=2)
    data_interval = st.selectbox("Chart Interval", ["1d", "1wk", "1mo"], index=0)

# --- MAIN AREA ---

# Navigation (Moved up for data dependencies)
views = ["Charts", "Comparison", "Fundamentals", "Backtest", "Seasonality", "Portfolio Study", "Options", "Institutional Activity 🏦", "News & Sentiment 📰"]

# Ensure current_view is initialized
if "current_view" not in st.session_state:
    st.session_state["current_view"] = "Charts"

# Navigation (Horizontal Radio behaving like Tabs)
selected_view = st.radio(
    "Navigation", 
    views, 
    index=views.index(st.session_state.get("current_view", "Charts")), 
    horizontal=True, 
    label_visibility="collapsed",
    key="current_view_radio"
)

# Sync with session state
st.session_state["current_view"] = selected_view

# Standard Analysis View
ticker = st.session_state["selected_ticker"]

# Fetch Data
with st.spinner("Fetching data..."):
    # --- Data Fetching ---
    with st.spinner(f"Fetching data for {ticker}..."):
        # Special logic for Seasonality to ensure first month is captured (Missing Month Fix)
        if selected_view == "Seasonality":
            try:
                import datetime
                from dateutil.relativedelta import relativedelta
                
                # Calculate start date based on selected period logic in seasonality_view
                # Default to 10 years if not set, or parse from period string
                # Simpler: just fetch max buffer needed (e.g. 20 years + 2 months) to cover all cases
                # or better, move this logic inside seasonality view? No, fetch happens here.
                
                # Let's assume standard period first, but we need start/end.
                # If period is "10y", we need 10y + 2 months buffer.
                
                # Parsing period text to years
                # Default "2y" from portfolio settings might track here? 
                # Actually Seasonality usually has its own selector inside the view or uses the global one?
                # The current app uses global 'period' var from sidebar/settings.
                
                # Let's map 'period' string to years
                years_map = {"1y": 1, "2y": 2, "5y": 5, "10y": 10, "max": 20} # Changed "Max" to "max" to match data_period options
                years_back = years_map.get(data_period, 10) # default 10 if unknown
                
                end_date = datetime.date.today()
                start_date = end_date - relativedelta(years=years_back) - relativedelta(months=2) # 2 month buffer
                
                df = get_stock_price_history(ticker, start=start_date, end=end_date, interval=data_interval)
            except Exception as e:
                print(f"Error calculating buffer date: {e}")
                df = get_stock_price_history(ticker, period=data_period, interval=data_interval)
        else:
            df = get_stock_price_history(ticker, period=data_period, interval=data_interval) # Use cached default
            
if not df.empty:
    # Calculate Indicators
    df = calculate_technicals(df)
    
    # Persist the active tab state
    # Using radio button instead of st.tabs because st.tabs resets on rerun by default in many cases,
    # whereas radio state is preserved in session_state.
    

    
    st.divider()
    
    # --- RENDER SELECTED VIEW ---
    
    if selected_view == "Charts":
        render_charts(ticker, df)
        # RSI Section
        render_rsi(df)
    
    elif selected_view == "Comparison":
        st.subheader("Compare with another stock")
        
        # Default value from session state if set by chat
        default_compare = st.session_state.get("compare_ticker", "INFY.NS" if ticker != "INFY.NS" else "TCS.NS")
        
        comp_ticker = st.text_input("Enter Ticker to Compare", value=default_compare)
        
        if comp_ticker:
            # Ensure proper formatting if needed
            if not comp_ticker.endswith(".NS") and not comp_ticker.endswith(".BO") and comp_ticker != "^NSEI":
                 comp_ticker = f"{comp_ticker}.NS"
            
            render_comparison_view(ticker, comp_ticker)

    elif selected_view == "Fundamentals":
        render_fundamentals_tab(ticker)
        
    elif selected_view == "Backtest":
        render_backtest_tab(df)
            
    elif selected_view == "Seasonality":
        render_seasonality_tab(df)

    elif selected_view == "Portfolio Study":
        render_portfolio_tab()
        
    elif selected_view == "Options":
        render_options_tab()

    elif selected_view == "Institutional Activity 🏦":
        render_fii_dii_tab()

    elif selected_view == "News & Sentiment 📰":
        render_news_view(ticker)

else:
    st.error(f"Could not fetch data for {ticker}. Please check the symbol.")
