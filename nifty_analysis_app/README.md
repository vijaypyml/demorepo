# Nifty 100 Analysis App

## Overview
The **Nifty 100 Analysis App** is a comprehensive stock analysis tool built with Streamlit. It provides users with powerful tools to analyze Nifty 100 stocks, offering interactive charts, technical indicators, fundamental data, peer comparison, backtesting, and seasonality analysis.

## Features
- **Interactive Charts**: Visualize stock price history with customizable time periods (1y, 2y, 5y, 10y, max) and intervals (Daily, Weekly, Monthly). Includes Bollinger Bands and RSI.
- **Peer Comparison**: Compare the performance of the selected stock against other stocks (e.g., INFY vs TCS).
- **Fundamental Analysis**: View key financial metrics and fundamental data for the selected stock.
- **Backtesting**: Run backtests on the stock data with metrics like CAGR, Sharpe Ratio, Sortino Ratio, Max Drawdown, and more. Visualize Equity Curves and Underwater Plots.
- **Seasonality Analysis**: Explore monthly and weekly seasonality patterns with heatmaps and detailed statistics.
- **AI Chatbot**: Integrated sidebar chatbot for quick queries (simulated).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd nifty_analysis_app
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

2.  **Navigate the App:**
    -   Use the **Sidebar** to select the data period and chart interval.
    -   Use the **Search Bar** (if available) or interact with the default Nifty 50 ticker.
    -   Switch between tabs: **Charts**, **Comparison**, **Fundamentals**, **Backtest**, and **Seasonality** to explore different aspects of the analysis.

## Project Structure
-   `app.py`: The main entry point of the Streamlit application.
-   `analysis/`: Contains logic for technicals, backtesting, and seasonality analysis.
-   `ui/`: Contains UI components and render functions for different views.
-   `data_mcp/`: Data fetching tools.
-   `requirements.txt`: List of Python dependencies.

## Technologies Used
-   **Streamlit**: For the web application framework.
-   **yfinance**: For fetching historical stock data.
-   **Pandas**: For data manipulation and analysis.
-   **Plotly**: For interactive charting.
-   **TA-Lib (ta)**: For technical analysis indicators.
-   **Seaborn/Matplotlib**: For statistical data visualization.
