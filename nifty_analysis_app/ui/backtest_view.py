import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analysis.backtest import run_backtest

def render_backtest_tab(df):
    st.subheader("Quantitative Strategy Analysis")
    
    # Strategy Selection
    col1, col2 = st.columns([1, 3])
    with col1:
        strategy = st.selectbox("Select Strategy", ["SMA_Crossover", "RSI_Bounds"], key="bt_strat_select")
        run_btn = st.button("Run Quantitative Analysis")
    
    if run_btn:
        with st.spinner("Calculating Quant Metrics..."):
            result = run_backtest(df, strategy_type=strategy)
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
            
            # --- 3. Stress Test / Best & Worst ---
            st.markdown("### 3. Stress Test & Psychology")
            
            # Best/Worst Month (Approximate by resampling)
            monthly_ret = data['Strategy_Return'].resample('ME').sum()
            best_m = monthly_ret.max()
            worst_m = monthly_ret.min()
            
            col_s1, col_s2 = st.columns(2)
            col_s1.write(f"**Best Month:** {best_m:.2%}")
            col_s2.write(f"**Worst Month:** {worst_m:.2%}")
