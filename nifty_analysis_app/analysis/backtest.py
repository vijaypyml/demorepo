import pandas as pd
import numpy as np

def run_backtest(df, strategy_type='SMA_Crossover'):
    """
    Runs a detailed backtest and calculates quantitative risk metrics.
    """
    if df.empty:
        return {}

    df = df.copy()
    df['Signal'] = 0
    
    # --- Strategy Logic ---
    if strategy_type == 'SMA_Crossover':
        # Buy/Hold when SMA50 > SMA200
        # Ensure columns exist, else calc them
        if 'SMA_50' not in df.columns: from analysis.technicals import calculate_technicals; df = calculate_technicals(df)
        
        df['Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0)
    
    elif strategy_type == 'RSI_Bounds':
        if 'RSI' not in df.columns: from analysis.technicals import calculate_technicals; df = calculate_technicals(df)
        
        # Simple Mean Reversion Logic
        # 1 = Long, 0 = Flat
        # Enter Long if RSI < 30, Exit if RSI > 70
        position = 0
        signals = []
        for rsi in df['RSI']:
            if rsi < 30:
                position = 1
            elif rsi > 70:
                position = 0
            signals.append(position)
        df['Signal'] = signals

    # Shift Signal to simulate trading "Next Open/Close" based on "Today's Close" signal
    df['Position'] = df['Signal'].shift(1)
    
    # Calculate Returns
    df['Market_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Market_Return'] * df['Position']
    df['Strategy_Return'] = df['Strategy_Return'].fillna(0)
    
    # --- Quantitative Metrics Calculation ---
    
    # 1. Equity Curve
    df['Equity_Curve'] = (1 + df['Strategy_Return']).cumprod()
    
    # 2. Total Return
    total_return = df['Equity_Curve'].iloc[-1] - 1
    
    # 3. CAGR
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25
    cagr = (df['Equity_Curve'].iloc[-1])**(1/years) - 1 if years > 0 else 0
    
    # 4. Volatility (Annualized)
    daily_vol = df['Strategy_Return'].std()
    annual_vol = daily_vol * np.sqrt(252)
    
    # 5. Sharpe Ratio (assuming 0% risk free)
    sharpe = (df['Strategy_Return'].mean() / daily_vol) * np.sqrt(252) if daily_vol > 0 else 0
    
    # 6. Sortino Ratio
    negative_returns = df.loc[df['Strategy_Return'] < 0, 'Strategy_Return']
    downside_std = negative_returns.std()
    sortino = (df['Strategy_Return'].mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    # 7. Max Drawdown
    cumulative_max = df['Equity_Curve'].cummax()
    drawdown = (df['Equity_Curve'] - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()
    
    # 8. Calmar Ratio
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # 9. Win Rate
    # Filter for days where we were in the market
    active_days = df[df['Position'] == 1]
    if len(active_days) > 0:
        win_rate = (active_days['Strategy_Return'] > 0).sum() / len(active_days)
    else:
        win_rate = 0
        
    # 10. Longest Drawdown Duration
    is_underwater = drawdown < 0
    # Group consecutive True values
    # This is a bit complex for a one-liner, skipping exact day count for now or doing simple approx
    
    # Pain to Profit Verdict
    verdict = "Investable"
    if calmar < 0.2 or max_drawdown < -0.3:
        verdict = "High Risk / Speculative"
    if sharpe < 0.5:
        verdict = "Poor Risk-Adjusted Returns"
    
    return {
        "metrics": {
            "Total Return": total_return,
            "CAGR": cagr,
            "Volatility": annual_vol,
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Max Drawdown": max_drawdown,
            "Calmar Ratio": calmar,
            "Win Rate": win_rate,
            "Verdict": verdict
        },
        "data": df, # Contains Equity_Curve, Drawdown (needs calc), etc.
        "drawdown_series": drawdown,
        "strategy_type": strategy_type
    }
