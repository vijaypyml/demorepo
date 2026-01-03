import pandas as pd
import numpy as np
import nsepython as nse
import streamlit as st

class OptionChainAnalyzer:
    @staticmethod
    def _generate_mock_payload(symbol):
        """Generates a realistic mock payload for testing/fallback."""
        spot = 24500 if "NIFTY" in symbol else 52000 if "BANK" in symbol else 2500
        step = 50 if "NIFTY" in symbol else 100 if "BANK" in symbol else 20
        
        strikes = [spot + (i * step) for i in range(-20, 21)]
        records = []
        
        for k in strikes:
            # Simulate OI distribution (bell curve-ish)
            dist = 1 - abs(k - spot)/(10*step)
            oi_base = max(1000, 100000 * dist)
            
            records.append({
                'strikePrice': k,
                'expiryDate': '15-Jan-2026',
                'CE': {
                    'strikePrice': k,
                    'expiryDate': '15-Jan-2026',
                    'openInterest': int(oi_base * (0.8 if k < spot else 1.2)),
                    'changeinOpenInterest': int(oi_base * 0.1),
                    'lastPrice': max(5, (spot - k) if k < spot else 0) + 50
                },
                'PE': {
                    'strikePrice': k,
                    'expiryDate': '15-Jan-2026',
                    'openInterest': int(oi_base * (1.2 if k < spot else 0.8)),
                    'changeinOpenInterest': int(oi_base * 0.1 * (-1 if k > spot else 1)),
                    'lastPrice': max(5, (k - spot) if k > spot else 0) + 50
                }
            })
            
        return {
            'records': {
                'expiryDates': ['15-Jan-2026', '22-Jan-2026', '29-Jan-2026'],
                'data': records,
                'underlyingValue': spot
            }
        }

    @staticmethod
    @st.cache_data(ttl=60) # Cache for 1 minute as options change fast
    def fetch_option_chain(symbol):
        """
        Fetches option chain data for a symbol.
        """
        try:
            # Handle indices
            if symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
                url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            else:
                # Stock symbols need .NS removed if present
                clean_symbol = symbol.replace('.NS', '')
                url = f"https://www.nseindia.com/api/option-chain-equities?symbol={clean_symbol}"
            
            data = nse.nsefetch(url)
            if not data:
                print(f"Warning: Empty data for {symbol}, using mock.")
                return OptionChainAnalyzer._generate_mock_payload(symbol)
            return data
        except Exception as e:
            print(f"Error fetching option chain for {symbol}: {e}")
            return OptionChainAnalyzer._generate_mock_payload(symbol)

    @staticmethod
    def get_expiry_dates(payload):
        if not payload: return []
        return payload.get('records', {}).get('expiryDates', [])

    @staticmethod
    def process_option_chain(payload, expiry_date):
        """
        Processes raw payload to get a DataFrame for a specific expiry.
        Calculates PCR and identifies Max Pain.
        """
        if not payload: return pd.DataFrame(), 0, 0, 0, 0

        data = payload.get('records', {}).get('data', [])
        current_price = payload.get('records', {}).get('underlyingValue', 0)
        
        # Filter by expiry
        filtered_data = [rec for rec in data if rec['expiryDate'] == expiry_date]
        
        chain_list = []
        total_pe_oi = 0
        total_ce_oi = 0
        
        # Max Pain Calculation Helpers
        strikes = []
        ce_oi_map = {}
        pe_oi_map = {}

        for rec in filtered_data:
            strike = rec.get('strikePrice')
            strikes.append(strike)
            
            ce = rec.get('CE', {})
            pe = rec.get('PE', {})
            
            ce_oi = ce.get('openInterest', 0)
            pe_oi = pe.get('openInterest', 0)
            
            ce_oi_chg = ce.get('changeinOpenInterest', 0)
            pe_oi_chg = pe.get('changeinOpenInterest', 0)
            
            total_ce_oi += ce_oi
            total_pe_oi += pe_oi
            
            ce_oi_map[strike] = ce_oi
            pe_oi_map[strike] = pe_oi
            
            chain_list.append({
                'Strike': strike,
                'CE OI': ce_oi,
                'CE Change OI': ce_oi_chg,
                'CE LTP': ce.get('lastPrice', 0),
                'PE LTP': pe.get('lastPrice', 0),
                'PE Change OI': pe_oi_chg,
                'PE OI': pe_oi,
            })
            
        df = pd.DataFrame(chain_list)
        pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
        # Max Pain Calculation
        # Max Pain is the strike where option writers (sellers) lose the least money.
        # Loss for CE writer at Strike K = Max(0, Spot - K) * OI
        # Loss for PE writer at Strike K = Max(0, K - Spot) * OI
        # We simulate "Spot" landing at each strike price.
        
        min_loss = float('inf')
        max_pain_strike = 0
        
        for assumption_strike in strikes:
            total_loss = 0
            for k in strikes:
                # Call Writers Loss if market ends at assumption_strike
                if assumption_strike > k:
                    total_loss += (assumption_strike - k) * ce_oi_map.get(k, 0)
                
                # Put Writers Loss if market ends at assumption_strike
                if assumption_strike < k:
                    total_loss += (k - assumption_strike) * pe_oi_map.get(k, 0)
            
            if total_loss < min_loss:
                min_loss = total_loss
                max_pain_strike = assumption_strike
                
        return df, pcr, total_ce_oi, total_pe_oi, max_pain_strike, current_price
