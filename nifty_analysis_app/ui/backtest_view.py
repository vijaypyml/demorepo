import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analysis.backtest import run_backtest

def render_backtest_tab(df):
    st.subheader("Quantitative Strategy Analysis")
    
    # --- Strategy Configuration Panel ---
    with st.expander("⚙️ Strategy Configuration", expanded=True):
        col_mode, col_space = st.columns([1, 2])
        with col_mode:
            mode = st.radio("Strategy Mode", ["Indicator Strategy", "Portfolio Strategy"], horizontal=True)
            
        st.divider()
        
        params = {}
        strategy_type = "SMA_Crossover"
        
        if mode == "Indicator Strategy":
            col_ind, col_params = st.columns([1, 2])
            
            with col_ind:
                indicator_select = st.selectbox(
                    "Select Indicator", 
                    ["SMA Crossover", "EMA Crossover", "RSI Mean Reversion", "MACD Trend", "Bollinger Bands", "Supertrend"],
                    help="Choose the technical indicator to backtest."
                )
            
            with col_params:
                if indicator_select == "SMA Crossover":
                    strategy_type = "SMA_Crossover"
                    c1, c2 = st.columns(2)
                    params['fast_period'] = c1.number_input("Fast SMA Period", min_value=1, value=50)
                    params['slow_period'] = c2.number_input("Slow SMA Period", min_value=1, value=200)
                    
                elif indicator_select == "EMA Crossover":
                    strategy_type = "EMA_Crossover"
                    c1, c2 = st.columns(2)
                    params['fast_period'] = c1.number_input("Fast EMA Period", min_value=1, value=20)
                    params['slow_period'] = c2.number_input("Slow EMA Period", min_value=1, value=50)
                    
                elif indicator_select == "RSI Mean Reversion":
                    strategy_type = "RSI_Strategy"
                    c1, c2, c3 = st.columns(3)
                    params['rsi_period'] = c1.number_input("RSI Period", min_value=2, value=14)
                    params['buy_level'] = c2.number_input("Oversold (Buy)", min_value=1, max_value=49, value=30)
                    params['sell_level'] = c3.number_input("Overbought (Sell)", min_value=51, max_value=99, value=70)

                elif indicator_select == "MACD Trend":
                    strategy_type = "MACD_Strategy"
                    c1, c2, c3 = st.columns(3)
                    params['fast_window'] = c1.number_input("Fast Window", value=12)
                    params['slow_window'] = c2.number_input("Slow Window", value=26)
                    params['signal_window'] = c3.number_input("Signal Window", value=9)
                    
                elif indicator_select == "Bollinger Bands":
                    strategy_type = "Bollinger_Bands"
                    c1, c2 = st.columns(2)
                    params['bb_window'] = c1.number_input("Window", value=20)
                    params['bb_std'] = c2.number_input("Std Dev", value=2.0, step=0.1)

                elif indicator_select == "Supertrend":
                    strategy_type = "Supertrend"
                    c1, c2 = st.columns(2)
                    params['atr_period'] = c1.number_input("ATR Period", value=10)
                    params['multiplier'] = c2.number_input("Multiplier", value=3.0, step=0.1)
        
        else:
            # Portfolio Strategy Placeholders
            st.info("Portfolio Strategies coming soon. Using Default SMA Crossover.")
            strategy_type = "SMA_Crossover"
            params = {'fast_period': 50, 'slow_period': 200}

        run_btn = st.button("🚀 Run Backtest", type="primary")

    if run_btn:
        with st.spinner("Calculating Quant Metrics..."):
            result = run_backtest(df, strategy_type=strategy_type, params=params)
            
            if not result:
                st.error("Backtest failed or returned no data.")
                return

            metrics = result["metrics"]
            data = result["data"]
            dd_series = result["drawdown_series"]
            
            # --- 1. KPI Table ---
            st.markdown("### 1. Key Performance Indicators")
            kpi_cols = st.columns(4)
            kpi_cols[0].metric("CAGR", f"{metrics['CAGR']:.2%}")
            kpi_cols[1].metric("Total Return", f"{metrics['Total Return']:.2%}")
            kpi_cols[2].metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
            kpi_cols[3].metric("Sortino Ratio", f"{metrics['Sortino Ratio']:.2f}")
            
            kpi_cols2 = st.columns(4)
            kpi_cols2[0].metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}", delta_color="inverse")
            kpi_cols2[1].metric("Calmar Ratio", f"{metrics['Calmar Ratio']:.2f}")
            kpi_cols2[2].metric("Win Rate", f"{metrics['Win Rate']:.2%}")
            kpi_cols2[3].metric("Volatility (Ann)", f"{metrics['Volatility']:.2%}", delta_color="inverse")
            
            st.info(f"**Final Verdict:** {metrics['Verdict']}")
            
            # --- 2. Visualizations ---
            st.markdown("### 2. Strategy Dashboard")
            
            # Use Matplotlib/Seaborn as requested
            sns.set_style("darkgrid")
            
            # A. Equity Curve (Log Scale)
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.plot(data.index, data['Equity_Curve'], label="Strategy Equity", color="blue")
            
            # Benchmark (Buy & Hold) for comparison
            # Normalized to start at 1
            benchmark = (1 + data['Market_Return']).cumprod()
            ax1.plot(data.index, benchmark, label="Buy & Hold", color="gray", linestyle="--", alpha=0.6)
            
            ax1.set_yscale('log')
            ax1.set_title("Equity Curve (Log Scale)")
            ax1.set_ylabel("Wealth Index")
            ax1.legend()
            st.pyplot(fig1)
            
            # B. Underwater Plot
            fig2, ax2 = plt.subplots(figsize=(10, 3))
            ax2.fill_between(dd_series.index, dd_series, 0, color='red', alpha=0.3)
            ax2.plot(dd_series.index, dd_series, color='red', linewidth=1)
            ax2.set_title("Underwater Plot (Drawdown)")
            ax2.set_ylabel("Drawdown %")
            st.pyplot(fig2)
            
            # C. Rolling Volatility (6-Month)
            fig3, ax3 = plt.subplots(figsize=(10, 3))
            rolling_vol = data['Strategy_Return'].rolling(window=126).std() * (252**0.5) # 6 months ~ 126 days
            ax3.plot(rolling_vol.index, rolling_vol, color='purple')
            ax3.set_title("6-Month Rolling Volatility")
            ax3.set_ylabel("Annualized Volatility")
            st.pyplot(fig3)
