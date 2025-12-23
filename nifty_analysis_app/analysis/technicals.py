import pandas as pd
import ta

def calculate_technicals(df):
    """
    Calculates technical indicators for the given dataframe.
    Expects 'Close' column.
    """
    if df.empty:
        return df

    # SMA
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
    
    # EMA
    df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    df['MACD'] = ta.trend.macd_diff(df['Close'])
    
    # Bollinger Bands
    indicator_bb = ta.volatility.BollingerBands(close=df["Close"], window=20, window_dev=2)
    df['BB_High'] = indicator_bb.bollinger_hband()
    df['BB_Low'] = indicator_bb.bollinger_lband()
    df['BB_Mid'] = indicator_bb.bollinger_mavg()
    
    return df
