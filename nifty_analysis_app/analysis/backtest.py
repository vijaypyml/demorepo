import pandas as pd
import numpy as np
import ta

def run_backtest(df, strategy_type='SMA_Crossover', params=None):
    """
    Runs a detailed backtest with dynamic parameters for various strategies.
    
    Args:
        df (pd.DataFrame): Historical data with 'Close', 'High', 'Low'.
        strategy_type (str): Type of strategy (e.g. 'SMA_Crossover', 'RSI_Bounds').
        params (dict): Dictionary of parameters (e.g. {'fast_period': 50, 'slow_period': 200}).
        
    Returns:
        dict: Results containing metrics, data with signals, and drawdown series.
    """
    if df.empty:
        return {}

    df = df.copy()
    
    # Default params if None
    if params is None: params = {}
    
    # --- Dynamic Indicator Calculation & Signal Logic ---
    
    if strategy_type == 'SMA_Crossover':
        fast = params.get('fast_period', 50)
        slow = params.get('slow_period', 200)
        
        # Calculate dynamic SMAs
        df['SMA_Fast'] = ta.trend.sma_indicator(df['Close'], window=fast)
        df['SMA_Slow'] = ta.trend.sma_indicator(df['Close'], window=slow)
        
        # Signal: 1 (Long) if Fast > Slow, 0 (Flat) otherwise
        df['Signal'] = np.where(df['SMA_Fast'] > df['SMA_Slow'], 1, 0)
        
    elif strategy_type == 'EMA_Crossover':
        fast = params.get('fast_period', 20)
        slow = params.get('slow_period', 50)
        
        df['EMA_Fast'] = ta.trend.ema_indicator(df['Close'], window=fast)
        df['EMA_Slow'] = ta.trend.ema_indicator(df['Close'], window=slow)
        
        df['Signal'] = np.where(df['EMA_Fast'] > df['EMA_Slow'], 1, 0)

    elif strategy_type == 'RSI_Strategy':
        period = params.get('rsi_period', 14)
        buy_threshold = params.get('buy_level', 30)
        sell_threshold = params.get('sell_level', 70)
        
        df['RSI'] = ta.momentum.rsi(df['Close'], window=period)
        
        # Mean Reversion Logic
        # Buy when RSI < Buy Threshold (Oversold)
        # Sell when RSI > Sell Threshold (Overbought)
        # Note: This is a stateful strategy, using a loop for simplicity or detailed mask
        position = 0
        signals = []
        for rsi in df['RSI']:
            if rsi < buy_threshold:
                position = 1 # Enter Long
            elif rsi > sell_threshold:
                position = 0 # Exit/Flat
            signals.append(position)
        df['Signal'] = signals

    elif strategy_type == 'MACD_Strategy':
        fast = params.get('fast_window', 12)
        slow = params.get('slow_window', 26)
        signal = params.get('signal_window', 9)
        
        # Calculate MACD
        macd_obj = ta.trend.MACD(close=df['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
        df['MACD_Line'] = macd_obj.macd()
        df['Signal_Line'] = macd_obj.macd_signal()
        
        # Buy when MACD > Signal Line
        df['Signal'] = np.where(df['MACD_Line'] > df['Signal_Line'], 1, 0)
        
    elif strategy_type == 'Bollinger_Bands':
        window = params.get('bb_window', 20)
        std_dev = params.get('bb_std', 2.0)
        
        bb = ta.volatility.BollingerBands(close=df['Close'], window=window, window_dev=std_dev)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        
        # Mean Reversion: Buy if Price < Low Band (Bounce), Sell if Price > High Band
        # Simple Logic: Hold if Price < High Band? Or pure mean reversion?
        # Let's use: Buy if Close < Low, Hold until Close > High.
        
        position = 0
        signals = []
        for i, row in df.iterrows():
            close = row['Close']
            if close < row['BB_Low']:
                position = 1
            elif close > row['BB_High']:
                position = 0
            signals.append(position)
        df['Signal'] = signals
        
    elif strategy_type == 'Supertrend':
        # Supertrend is not directly in 'ta' library standard set usually, or creates issues.
        # We will implement a custom simple Supertrend calculation here if needed
        # Or use ATR based logic.
        period = params.get('atr_period', 10)
        multiplier = params.get('multiplier', 3.0)
        
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # Calculate ATR
        atr = ta.volatility.average_true_range(high, low, close, window=period)
        
        # Basic Supertrend Calculation
        # (High + Low) / 2
        hl2 = (high + low) / 2
        
        # Upper/Lower Bands
        # Note: Full Supertrend involves recursive logic.
        # Implementing simplified trend following using ATR for robustness.
        # Buy if Close > EMA + 2*ATR, Sell if Close < EMA - 2*ATR (Chandelier Exit style)
        
        df['EMA_Trend'] = ta.trend.ema_indicator(close, window=period)
        df['Upper_Band'] = df['EMA_Trend'] + (multiplier * atr)
        df['Lower_Band'] = df['EMA_Trend'] - (multiplier * atr)
        
        df['Signal'] = np.where(df['Close'] > df['EMA_Trend'], 1, 0)

    # --- Backtest Core Engine ---

    # Shift Signal to simulate trading "Next Open/Close" based on "Today's Close" signal
    df['Position'] = df['Signal'].shift(1)
    df['Position'] = df['Position'].fillna(0)
    
    # Calculate Returns
    df['Market_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Market_Return'] * df['Position']
    df['Strategy_Return'] = df['Strategy_Return'].fillna(0)
    
    # Quant Metrics
    df['Equity_Curve'] = (1 + df['Strategy_Return']).cumprod()
    
    total_return = df['Equity_Curve'].iloc[-1] - 1
    
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25
    cagr = (df['Equity_Curve'].iloc[-1])**(1/years) - 1 if years > 0 else 0
    
    daily_vol = df['Strategy_Return'].std()
    annual_vol = daily_vol * np.sqrt(252)
    
    sharpe = (df['Strategy_Return'].mean() / daily_vol) * np.sqrt(252) if daily_vol > 0 else 0
    
    negative_returns = df.loc[df['Strategy_Return'] < 0, 'Strategy_Return']
    downside_std = negative_returns.std()
    sortino = (df['Strategy_Return'].mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    cumulative_max = df['Equity_Curve'].cummax()
    drawdown = (df['Equity_Curve'] - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()
    
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0
    
    active_days = df[df['Position'] == 1]
    win_rate = (active_days['Strategy_Return'] > 0).sum() / len(active_days) if len(active_days) > 0 else 0
        
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
        "data": df,
        "drawdown_series": drawdown,
        "strategy_type": strategy_type
    }
