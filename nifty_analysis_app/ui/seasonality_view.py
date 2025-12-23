import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from analysis.seasonality import analyze_seasonality

def render_seasonality_tab(df):
    st.subheader("Seasonality Analysis: Monthly Returns")
    
    heatmap_data, stats_data = analyze_seasonality(df)
    
    if heatmap_data.empty:
        st.warning("Not enough data to generate seasonality analysis.")
        return

    # User Request: Heatmap with specific layout + Side Metrics
    
    # Create a layout with 2 columns: Heatmap (Wide), Stats (Narrow)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### Monthly Performance Heatmap")
        
        # Setup Figure
        # Height depends on number of months (12) but fixed is fine. Width depends on Years.
        num_years = len(heatmap_data.columns)
        width = max(8, num_years * 0.8) 
        fig, ax = plt.subplots(figsize=(width, 6))
        
        # Seaborn Heatmap
        sns.heatmap(heatmap_data, ax=ax, cmap="RdYlGn", center=0, annot=True, fmt=".1%", 
                    cbar_kws={'label': 'Monthly Return'}, linewidths=.5, linecolor='gray')
        
        ax.set_title("Monthly Returns (%)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Month")
        
        st.pyplot(fig)

    with col2:
        st.markdown("#### Month Stats")
        # Format the stats table nicely
        # Win Rate as %, Avg/Total as %
        display_stats = stats_data.copy()
        display_stats['Win Rate'] = display_stats['Win Rate'].apply(lambda x: f"{x:.0%}")
        display_stats['Avg %'] = display_stats['Avg %'].apply(lambda x: f"{x:.2%}")
        display_stats['Total %'] = display_stats['Total %'].apply(lambda x: f"{x:.2%}")
        
        st.dataframe(display_stats, height=600)
    
    # --- Summary Text ---
    best_month = stats_data['Avg %'].idxmax()
    worst_month = stats_data['Avg %'].idxmin()
    best_avg = stats_data.loc[best_month, 'Avg %']
    worst_avg = stats_data.loc[worst_month, 'Avg %']
    best_win = stats_data.loc[best_month, 'Win Rate']
    
    st.info(f"""
    **Analysis Summary:**
    - **Best Month:** {best_month} (Avg: {best_avg:.2%}, Win Rate: {best_win:.0%})
    - **Worst Month:** {worst_month} (Avg: {worst_avg:.2%})
    """)

    st.divider()
    st.subheader("🔍 Deep Dive: Weekly Seasonality")
    
    from analysis.seasonality import prepare_weekly_data, get_yearly_drilldown, get_monthly_drilldown
    import calendar
    
    w_df = prepare_weekly_data(df)
    
    drill_type = st.radio("Select Drill-Down View", ["Yearly Analysis", "Monthly Seasonality"], horizontal=True)
    
    if drill_type == "Yearly Analysis":
        years = sorted(w_df['Year'].unique(), reverse=True)
        sel_year = st.selectbox("Select Year", years)
        
        pivot, stats = get_yearly_drilldown(w_df, sel_year)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            if not pivot.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(pivot, ax=ax, cmap="RdYlGn", center=0, annot=True, fmt=".1%", cbar=False)
                ax.set_title(f"Weekly Returns - {sel_year}")
                ax.set_xlabel("Week of Month")
                st.pyplot(fig)
            else:
                st.warning("No data for selected year.")
                
        with c2:
            st.write("**Monthly Totals**")
            st.dataframe(stats.apply(lambda x: f"{x:.2%}"), height=400)

    else: # Monthly Seasonality
        months = list(calendar.month_name)[1:]
        sel_month = st.selectbox("Select Month", months)
        
        pivot, stats = get_monthly_drilldown(w_df, sel_month)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            if not pivot.empty:
                # Dynamic height based on years
                h = max(6, len(pivot)*0.3)
                fig, ax = plt.subplots(figsize=(8, h))
                sns.heatmap(pivot, ax=ax, cmap="RdYlGn", center=0, annot=True, fmt=".1%", cbar=False)
                ax.set_title(f"Weekly Profile - {sel_month} (All Years)")
                ax.set_ylabel("Year")
                ax.set_xlabel("Week of Month")
                st.pyplot(fig)
            else:
                st.warning("No data for selected month.")
                
        with c2:
            st.write("**Week Stats**")
            disp_stats = stats.copy()
            disp_stats['Win Rate'] = disp_stats['Win Rate'].apply(lambda x: f"{x:.0%}")
            disp_stats['Avg Return'] = disp_stats['Avg Return'].apply(lambda x: f"{x:.2%}")
            st.dataframe(disp_stats)
