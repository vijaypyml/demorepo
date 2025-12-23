import pandas as pd
import calendar

def analyze_seasonality_advanced(df):
    """
    Analyzes seasonality to produce a pivot table and detailed stats.
    Returns:
        pivot_table: DataFrame (Index=Month, Columns=Year, Values=Return)
        stats_table: DataFrame (Index=Month, Columns=[Pos, Neg, WinRate, Avg%, Total%])
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = df.copy()
    
    # Calculate Monthly Returns
    # Resample to End of Month, take last price
    monthly_prices = df['Close'].resample('ME').last()
    
    # Simple percentage change
    monthly_returns = monthly_prices.pct_change()
    
    # Create a DataFrame for processing
    m_df = pd.DataFrame(monthly_returns).rename(columns={'Close': 'Return'})
    m_df['Year'] = m_df.index.year
    m_df['Month'] = m_df.index.month
    
    # Filter out the first row (NaN from pct_change)
    m_df = m_df.dropna()

    # --- 1. PIVOT TABLE (for Heatmap) ---
    pivot_table = m_df.pivot(index='Month', columns='Year', values='Return')
    
    # Sort index reverse (Dec at bottom? User asked Jan at top, Dec at bottom. 
    # Standard pivot puts 1 at top. So that's correct.)
    
    # Transform index to Month Names
    month_names = {i: calendar.month_name[i] for i in range(1, 13)}
    pivot_table.index = pivot_table.index.map(month_names)
    
    # Ensure all 12 months are present in order
    ordered_months = list(calendar.month_name)[1:]
    pivot_table = pivot_table.reindex(ordered_months)

    # --- 2. STATISTICS TABLE ---
    stats = []
    
    for month_num in range(1, 13):
        month_name = calendar.month_name[month_num]
        month_data = m_df[m_df['Month'] == month_num]['Return']
        
        count = len(month_data)
        if count == 0:
            stats.append({'Month': month_name, 'Pos': 0, 'Neg': 0, 'Win Rate': 0, 'Avg %': 0, 'Total %': 0})
            continue
            
        pos_count = (month_data > 0).sum()
        neg_count = (month_data < 0).sum()
        win_rate = pos_count / count
        avg_ret = month_data.mean()
        total_ret = month_data.sum()
        
        stats.append({
            'Month': month_name, 
            'Pos': pos_count, 
            'Neg': neg_count, 
            'Win Rate': win_rate, 
            'Avg %': avg_ret, 
            'Total %': total_ret
        })
    
    stats_df = pd.DataFrame(stats).set_index('Month')
    
    return pivot_table, stats_df

# Keep old function signature compatibility if needed?
# Actually app.py uses analyze_seasonality(df)
# I should update app.py to use this NEW function or replace the old one.
# I'll replace the old one but with the new return signature, and update app.py to handle it.
def analyze_seasonality(df):
    return analyze_seasonality_advanced(df)

def prepare_weekly_data(df):
    """
    Prepares data with Week_of_Month (1-5) logic.
    Week 1: Days 1-7
    Week 2: Days 8-14
    Week 3: Days 15-21
    Week 4: Days 22-28
    Week 5: Days 29-End
    """
    if df.empty: return pd.DataFrame()
    
    w_df = df.copy()
    w_df['Day'] = w_df.index.day
    w_df['Month'] = w_df.index.month
    w_df['Year'] = w_df.index.year
    w_df['Month_Name'] = w_df.index.strftime('%B')
    
    # Week of Month Logic
    def get_week_of_month(day):
        if day <= 7: return 1
        elif day <= 14: return 2
        elif day <= 21: return 3
        elif day <= 28: return 4
        else: return 5
        
    w_df['Week'] = w_df['Day'].apply(get_week_of_month)
    w_df['Return'] = w_df['Close'].pct_change()
    
    # Aggregate Returns by Year, Month, Week
    # We want the cumulative return for that week?? Or average daily return?
    # Usually "Weekly Seasonality" implies the return of holding through that week.
    # Simple sum of % changes is an approximation, or product of (1+r).
    # Let's use Sum for simplicity and consistency with previous heatmaps, or compound if precision needed.
    # Group by Year, Month, Week -> Sum Returns
    weekly = w_df.groupby(['Year', 'Month', 'Month_Name', 'Week'])['Return'].sum().reset_index()
    
    return weekly

def get_yearly_drilldown(weekly_df, selected_year):
    """
    Filters for year. Returns Pivot (Month x Week) and Monthly Totals.
    """
    if weekly_df.empty: return pd.DataFrame(), pd.DataFrame()
    
    data = weekly_df[weekly_df['Year'] == selected_year]
    
    # Pivot: Index=Month_Name, Columns=Week, Values=Return
    pivot = data.pivot(index='Month_Name', columns='Week', values='Return')
    
    # Sort Months
    ordered_months = list(calendar.month_name)[1:]
    pivot = pivot.reindex(ordered_months)
    
    # Stats: Total Return per Month
    stats = data.groupby('Month_Name')['Return'].sum().reindex(ordered_months)
    
    return pivot, stats

def get_monthly_drilldown(weekly_df, selected_month_name):
    """
    Filters for month. Returns Pivot (Year x Week) and Week Stats.
    """
    if weekly_df.empty: return pd.DataFrame(), pd.DataFrame()
    
    data = weekly_df[weekly_df['Month_Name'] == selected_month_name]
    
    # Pivot: Index=Year, Columns=Week, Values=Return
    pivot = data.pivot(index='Year', columns='Week', values='Return')
    
    # Stats per Week (Across all years)
    week_stats = []
    for w in range(1, 6):
        if w in pivot.columns:
            vals = pivot[w]
            win_rate = (vals > 0).mean()
            avg_ret = vals.mean()
            week_stats.append({'Week': w, 'Win Rate': win_rate, 'Avg Return': avg_ret})
        else:
             week_stats.append({'Week': w, 'Win Rate': 0, 'Avg Return': 0})
             
    return pivot, pd.DataFrame(week_stats).set_index('Week')
