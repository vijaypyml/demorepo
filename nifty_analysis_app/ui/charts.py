import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_charts(ticker, df):
    """
    Renders the main chart with optional indicators.
    """
    if df.empty:
        st.warning("No data to display.")
        return

    # Chart Type Selection
    chart_type = st.selectbox("Chart Type", ["Candlestick", "Line"], key="chart_type_select")
    
    # Indicator Selection
    indicators = st.multiselect("Indicators", ["SMA 50", "SMA 200", "EMA 20", "Bollinger Bands"], key="indicators_select")

    # Create Subplots (Main + Volume? Or RSI?)
    # Let's add a separate row for RSI/MACD if we want, for now just Main Chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=(f"{ticker} Price", "Volume"), 
                        row_width=[0.2, 0.7])

    # Price Chart
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'], name="OHLC"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='blue', width=2), name="Close"), row=1, col=1)

    # Add Indicators
    if "SMA 50" in indicators and 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name="SMA 50"), row=1, col=1)
    if "SMA 200" in indicators and 'SMA_200' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='red', width=1), name="SMA 200"), row=1, col=1)
    if "EMA 20" in indicators and 'EMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='green', width=1), name="EMA 20"), row=1, col=1)
        
    if "Bollinger Bands" in indicators and 'BB_High' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_High'], line=dict(color='gray', width=1, dash='dash'), name="BB High"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Low'], line=dict(color='gray', width=1, dash='dash'), name="BB Low", fill='tonexty'), row=1, col=1)

    # Volume Chart
    colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, height=600, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

def render_rsi(df):
    if 'RSI' not in df.columns:
        return
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple')))
    
    # Add 70/30 lines
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    
    fig.update_layout(height=200, title="RSI", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
