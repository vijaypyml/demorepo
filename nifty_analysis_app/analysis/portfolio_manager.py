
import yfinance as yf
import pandas as pd
import numpy as np
import scipy.optimize as sco
import plotly.graph_objects as go
try:
    from pypfopt import expected_returns, risk_models, EfficientFrontier, objective_functions
    HAS_PYPFOPT = True
except ImportError:
    HAS_PYPFOPT = False
    print("PyPortfolioOpt not found. Using fallback methods.")

class PortfolioManager:
    """
    A class to manage portfolio analysis, risk metric calculation, and capital allocation.
    """
    def __init__(self, tickers):
        """
        Initialize with a list of tickers.
        """
        self.tickers = tickers
        self.data = pd.DataFrame()
        self.limiting_tickers = []
        self.risk_free_rate = 0.04 # Approximation for India 10Y or US 10Y depending on context, using constant for now

    def fetch_data(self, period="2y"):
        """
        Fetches adjusted close prices for the initialization tickers.
        """
        try:
            # Download data
            data = yf.download(self.tickers, period=period, auto_adjust=True)
            
            # yfinance returns a MultiIndex if multiple tickers, or single level if one.
            # We want just the 'Close' prices. 
            # Note: auto_adjust=True returns 'Close' as adjusted already.
            
            if 'Close' in data.columns and isinstance(data.columns, pd.MultiIndex):
                 self.data = data['Close']
            elif 'Close' in data.columns:
                 self.data = data['Close'] # Single ticker case often behaves differently, but here we expect multiple
            else:
                # If auto_adjust=True, sometimes it just gives columns as tickers directly if only Close is returned?
                # Let's handle standard yf.download structure
                if isinstance(data.columns, pd.MultiIndex):
                     # If we have (Price, Ticker) levels
                     if 'Close' in data.columns.get_level_values(0):
                         self.data = data['Close']
                     else:
                         self.data = data # Fallback
                else:
                    self.data = data # Fallback
            
            # Identify Limiting Assets (those that force the start date to be later)
            # Find the first valid index for each column
            first_valid_indices = self.data.apply(lambda col: col.first_valid_index())
            if not first_valid_indices.empty:
                max_start = first_valid_indices.max()
                self.limiting_tickers = first_valid_indices[first_valid_indices == max_start].index.tolist()
            else:
                self.limiting_tickers = []

            # Drop missing data
            self.data = self.data.dropna()
            return self.data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def calculate_risk_metrics(self):
        """
        Computes Sharpe Ratio, Sortino Ratio, and Max Drawdown for each asset.
        Returns a DataFrame.
        """
        if self.data.empty:
            return pd.DataFrame()

        # Daily Returns
        daily_returns = self.data.pct_change().dropna()
        
        metrics = {}
        
        for ticker in self.data.columns:
            r = daily_returns[ticker]
            
            # Annualized measurements (assuming 252 trading days)
            ann_mean = r.mean() * 252
            ann_std = r.std() * np.sqrt(252)
            
            # Sharpe Ratio
            if ann_std != 0:
                sharpe = (ann_mean - self.risk_free_rate) / ann_std
            else:
                sharpe = 0.0
            
            # Sortino Ratio (Downside deviation)
            downside_returns = r[r < 0]
            downside_std = downside_returns.std() * np.sqrt(252)
            if downside_std != 0:
                sortino = (ann_mean - self.risk_free_rate) / downside_std
            else:
                sortino = 0.0
                
            # Max Drawdown
            cumulative = (1 + r).cumprod()
            peak = cumulative.cummax()
            drawdown = (cumulative - peak) / peak
            max_drawdown = drawdown.min()
            
            # Calmar Ratio
            # Annualized Return / Abs(Max Drawdown)
            if max_drawdown != 0:
                calmar = ann_mean / abs(max_drawdown)
            else:
                calmar = 0.0
            
            # Total Return
            start_price = self.data[ticker].iloc[0]
            end_price = self.data[ticker].iloc[-1]
            total_return = (end_price - start_price) / start_price
            
            # CAGR
            # Number of years = Total Days / 365.25
            days = (self.data.index[-1] - self.data.index[0]).days
            years_val = days / 365.25
            if years_val > 0 and start_price > 0 and end_price > 0:
                cagr = (end_price / start_price) ** (1/years_val) - 1
            else:
                cagr = 0.0

            metrics[ticker] = {
                "Sharpe Ratio": round(sharpe, 2),
                "Sortino Ratio": round(sortino, 2),
                "Calmar Ratio": round(calmar, 2),
                "Max Drawdown (%)": round(max_drawdown * 100, 2),
                "Total Return (%)": round(total_return * 100, 2),
                "CAGR (%)": round(cagr * 100, 2)
            }
        # Identify Limiting Assets
        max_start_date = self.data.index[0]
        limiting_assets = []
        
        # We need raw data start dates to know which ones were cut off?
        # self.data is already dropped. 
        # But we know that self.data starts at max_start_date.
        # We can check which columns have valid data closest to this start date?
        # Actually, since we did dropna(), ALL columns have valid data at index[0].
        # But some might have had data EARLIER that was dropped because OTHER columns didn't.
        # Wait, dropna() drops rows where ANY col is NaN. 
        # So the asset that STARTS LATEST determines index[0].
        # We can check which column started exactly at index[0] (or close to it) in the RAW download?
        # But we don't have raw download anymore. 
        # Let's verify by just assuming if data exists at index[0], it's valid.
        
        # To identify "Limiting Asset", we need to see which one forces the start date.
        # It's the one(s) whose first valid index in the ORIGINAL fetch was the latest.
        # Since we don't store original fetch, we can't be 100% sure without re-fetching or inspecting pre-dropna.
        # Let's modify fetch_data to find this?
        # Or simpler: In calculate_risk_metrics, we just return the effective start date (already doing).
        # To "Ask to remove it", we need to know WHICH one.
        
        # Let's do a quick individual check for the tickers in the list:
        # We can just iterate self.tickers and check their start dates if we assume calculate_risk_metrics is called right after fetch?
        # No, that's expensive.
        # Let's modify fetch_data to store "original_start_dates" per ticker?
        
        return pd.DataFrame(metrics).T, years_val, self.data.index[0], self.data.index[-1]

    def allocate_capital(self, total_capital, risk_profile):
        """
        Allocates capital based on risk profile using Mean-Variance Optimization or Heuristics.
        
        risk_profile: 'Conservative', 'Moderate', 'Aggressive'
        """
        if self.data.empty:
            return {}

    
        if not HAS_PYPFOPT:
            # Custom Score-Based Allocation
            try:
                metrics = self.calculate_risk_metrics()
                if metrics.empty: 
                    return {}
                
                scores = pd.Series(dtype=float)
                
                # Normalize metrics for scoring
                # We want positive scores.
                
                if risk_profile == "Conservative":
                    # Goal: Low MDD, High Sortino
                    # Score = Sortino / (abs(MDD) + epsilon)
                    # Note: MDD is negative usually? In my calc: (cumulative - peak) / peak -> negative logic?
                    # metric returned: "Max Drawdown": round(max_drawdown, 4) -> This is likely negative number (e.g. -0.20)
                    # Let's check calculate_risk_metrics logic: 
                    # drawdown = (cumulative - peak) / peak -> negative
                    # max_drawdown = drawdown.min() -> negative
                    
                    # We want to minimize magnitude of MDD.
                    # Score ~ Sortino + 1/|MDD|
                    # Simple heuristic: Rank them? 
                    # Let's use weighted score: 0.7 * (1 - Normalized_MDD_Rank) + 0.3 * Normalized_Sortino_Rank ?
                    # Let's map raw values to weights directly.
                    
                    # Convert percentage back to decimal for this heuristic to maintain original scale logic
                    mdd = metrics["Max Drawdown (%)"].abs() / 100.0
                    sortino = metrics["Sortino Ratio"]
                    
                    # Create a score: Higher Sortino is good. Lower MDD (abs) is good.
                    # Add small epsilon to avoid div by zero
                    score = (sortino + 1) / (mdd + 0.01) 
                    
                elif risk_profile == "Aggressive":
                    # Goal: High Sharpe, High Volatility OK.
                    sharpe = metrics["Sharpe Ratio"]
                    # Just weight by Sharpe (clipping negatives)
                    score = sharpe.clip(lower=0)
                    
                else: # Moderate
                    # Balanced
                    score = metrics["Sharpe Ratio"].clip(lower=0) + metrics["Sortino Ratio"].clip(lower=0)
                
                # Normalize scores to summing to 1
                total_score = score.sum()
                
                if total_score == 0:
                    weights = pd.Series(1/len(metrics), index=metrics.index)
                else:
                    weights = score / total_score
                
                # Double check to ensure weights sum to 1 (handle floating point errors)
                weights = weights / weights.sum()
                
                return {ticker: round(w * total_capital, 2) for ticker, w in weights.items() if w > 0}
                
            except Exception as e:
                print(f"Fallback allocation failed: {e}. Using equal weights.")
                n = len(self.data.columns)
                equal_weight = 1.0 / n
                return {ticker: round(equal_weight * total_capital, 2) for ticker in self.data.columns}

        # Calculate expected returns and sample covariance
        mu = expected_returns.mean_historical_return(self.data)
        S = risk_models.sample_cov(self.data)

        # Optimize for Maximal Sharpe Ratio
        ef = EfficientFrontier(mu, S)
        
        weights = {}

        try:
            if risk_profile == "Aggressive":
                # Maximize Sharpe Ratio
                weights = ef.max_sharpe(risk_free_rate=self.risk_free_rate)
            elif risk_profile == "Conservative":
                # Min Volatility
                weights = ef.min_volatility()
            else: # Moderate
                 # Maximize Quadratic Utility with some risk aversion
                 # Or just a mix. Let's try efficient risk? 
                 # For simplicity, let's use max_sharpe but with a volatility constraint if possible, 
                 # or simply max_quadratic_utility.
                 # Let's stick to a robust simple proxy: Max Sharpe often is too aggressive for 'Moderate'.
                 # Let's use max_quadratic_utility with a default risk_aversion parameter.
                 weights = ef.max_quadratic_utility(risk_aversion=1) 
                 
            cleaned_weights = ef.clean_weights()
            
            # Allocate capital
            allocation = {ticker: round(weight * total_capital, 2) for ticker, weight in cleaned_weights.items() if weight > 0}
            return allocation
            
        except Exception as e:
            # Fallback if optimization fails
            print(f"Optimization failed: {e}. Using equal weights.")
            n = len(self.data.columns)
            equal_weight = 1.0 / n
            return {ticker: round(equal_weight * total_capital, 2) for ticker in self.data.columns}

    def plot_portfolio(self, allocation, current_metrics, ticker_map=None):
        """
        Returns Plotly figures for Allocation (Donut) and Comparison (Bar).
        ticker_map: Dictionary mapping ticker symbols to human-readable names.
        """
        if ticker_map is None:
            ticker_map = {}
            
        # Helper to get name
        def get_name(ticker):
            return ticker_map.get(ticker, ticker)

        # Donut Chart for Allocation
        labels = [get_name(t) for t in allocation.keys()]
        values = list(allocation.values())
        
        # Create hover text with original ticker
        hover_text = [f"{t}: {get_name(t)}" for t in allocation.keys()]
        
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, hovertext=hover_text)])
        fig_donut.update_layout(title_text="Recommended Allocation")
        
        # Bar Chart for Sharpe Ratios
        bar_x = [get_name(t) for t in current_metrics.index]
        fig_bar = go.Figure(data=[
            go.Bar(name='Sharpe Ratio', x=bar_x, y=current_metrics['Sharpe Ratio'], text=current_metrics.index)
        ])
        fig_bar.update_layout(title_text="Asset Efficiency (Sharpe Ratio)")
        
        
        return fig_donut, fig_bar

    def plot_performance_charts(self, ticker_map=None):
        """
        Returns two Plotly figures: Normalized Performance and Raw Prices.
        ticker_map: Dictionary mapping ticker symbols to human-readable names.
        """
        if self.data.empty:
            return None, None
            
        if ticker_map is None:
            ticker_map = {}
            
        def get_name(ticker):
            return ticker_map.get(ticker, ticker)

        # 1. Normalized Chart (Base 100)
        normalized_data = self.data / self.data.iloc[0] * 100
        
        fig_norm = go.Figure()
        for col in normalized_data.columns:
            fig_norm.add_trace(go.Scatter(x=normalized_data.index, y=normalized_data[col], mode='lines', name=get_name(col)))
            
        fig_norm.update_layout(
            title="Portfolio Components Performance (Rebased to 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Value",
            hovermode="x unified"
        )
        
        
        # 2. Daily Returns Chart (replacing Raw Prices)
        daily_returns = self.data.pct_change() * 100
        daily_returns = daily_returns.dropna() # First row will be NaN
        
        fig_raw = go.Figure() # Variable name kept same to avoid breaking UI unpacking for now, but logic changed
        for col in daily_returns.columns:
            fig_raw.add_trace(go.Scatter(
                x=daily_returns.index, 
                y=daily_returns[col], 
                mode='lines', 
                name=get_name(col), 
                visible='legendonly',
                hovertemplate='%{y:.2f}%'
            ))
            
        fig_raw.update_layout(
            title="Daily Returns (%) - Volatility View",
            xaxis_title="Date",
            yaxis_title="Daily Change (%)",
            hovermode="x unified",
            legend_title="Click to Toggle"
        )
        
        return fig_norm, fig_raw

    def plot_drawdown_chart(self, ticker_map=None):
        """
        Returns a Plotly figure showing historical drawdowns (%).
        """
        if self.data.empty:
            return None
            
        if ticker_map is None:
            ticker_map = {}
            
        def get_name(ticker):
            return ticker_map.get(ticker, ticker)

        # Calculate Drawdown
        # Drawdown = (Price - Rolling Max) / Rolling Max
        rolling_max = self.data.cummax()
        drawdown = (self.data - rolling_max) / rolling_max * 100
        
        fig_dd = go.Figure()
        for col in drawdown.columns:
            fig_dd.add_trace(go.Scatter(
                x=drawdown.index, 
                y=drawdown[col], 
                mode='lines', 
                name=get_name(col),
                hovertemplate='%{y:.2f}%'
            ))
            
        fig_dd.update_layout(
            title="Historical Drawdown (%)",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            hovermode="x unified"
        )
        
        return fig_dd

    def plot_correlation_matrix(self, ticker_map=None):
        """
        Returns a Plotly Figure heatmap of the correlation matrix.
        """
        if self.data.empty:
            return None
            
        if ticker_map is None:
            ticker_map = {}
            
        def get_name(ticker):
            return ticker_map.get(ticker, ticker)
            
        # Calculate Correlation of Daily Returns
        returns = self.data.pct_change().dropna()
        corr_matrix = returns.corr()
        
        # Rename index/columns for display
        display_labels = [get_name(t) for t in corr_matrix.index]
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=display_labels,
            y=display_labels,
            colorscale='RdBu', 
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps = False
        ))
        
        fig.update_layout(
            title="Correlation Matrix (Daily Returns)",
            height=600,
            width=800
        )
        
        return fig
