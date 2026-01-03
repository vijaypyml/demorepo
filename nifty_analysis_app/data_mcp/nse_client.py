import nsepython as nse
import pandas as pd
import streamlit as st

class NSEClient:
    """
    Wrapper for nsepython to fetch data robustly and cache it.
    """
    
    @staticmethod
    @st.cache_data(ttl=300) # Cache for 5 minutes
    def get_quote(symbol):
        """Fetches the full equity quote data for a symbol (e.g. RELIANCE)."""
        try:
            # Handle symbols with .NS suffix if passed
            clean_symbol = symbol.replace('.NS', '')
            # Use direct fetch for better data (Delivery, Sector PE)
            url = f"https://www.nseindia.com/api/quote-equity?symbol={clean_symbol}"
            return nse.nsefetch(url)
        except Exception as e:
            print(f"Error fetching NSE quote for {symbol}: {e}")
            return {}

    @staticmethod
    @st.cache_data(ttl=300)
    def get_trade_info(symbol):
        """Fetches trade info including delivery %."""
        try:
            data = NSEClient.get_quote(symbol)
            return data.get('securityWiseTradeDetails', {})
        except Exception as e:
            print(f"Error fetching trade info for {symbol}: {e}")
            return {}
            
    @staticmethod
    @st.cache_data(ttl=900) # Cache for 15 minutes
    def get_industry_info(symbol):
        """Fetches industry info and metadata."""
        try:
            data = NSEClient.get_quote(symbol)
            return data.get('industryInfo', {})
        except Exception as e:
            print(f"Error fetching industry info for {symbol}: {e}")
            return {}
            
    @staticmethod
    def get_delivery_metrics(symbol):
        """Returns delivery % and quantity."""
        info = NSEClient.get_trade_info(symbol)
        if not info: return 0, 0
        
        try:
            del_qty = float(info.get('deliveryQuantity', 0))
            traded_qty = float(info.get('quantityTraded', 1))
            del_pct = (del_qty / traded_qty) if traded_qty else 0
            return del_pct, del_qty
        except:
            return 0, 0

    @staticmethod
    def get_peer_comparison_data(symbol):
        """
        Gets peer data from metadata.
        """
        data = NSEClient.get_quote(symbol)
        if not data: return {}
        
        meta = data.get('metadata', {})
        industry_info = data.get('industryInfo', {})
        
        return {
            'sector_pe': meta.get('pdSectorPe', None),
            'sector_ind': meta.get('pdSectorInd', None),
            'industry': industry_info.get('industry', 'Unknown')
        }
