import streamlit as st
from data_mcp.tools import get_stock_fundamentals, get_stock_price_history, get_nifty_tickers
from analysis.fundamentals import analyze_fundamentals
# Ideally we import the LLM client here if we had one.

def render_chat():
    st.subheader("🤖 Analyst Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I can analyze Nifty 100 stocks. Try 'Analyze TCS' or 'Compare RELIANCE'"}]

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask me about a stock..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # ---------------------------------------------------------
        # SIMPLE "MOCK LLM" PARSER
        # ---------------------------------------------------------
        # In a real scenario, this would be an API call to Gemini/OpenAI
        # Here we just look for keywords.
        
        response_text = "I didn't understand that. Please specify a ticker like 'Analyze TCS'."
        
        # Normalize prompt
        p_upper = prompt.upper()
        
        # Detect Ticker
        # We can try to match against our list or just look for CAPS words that look like tickers
        words = p_upper.split()
        target_ticker = None
        
        # Check against known list first
        known_tickers = get_nifty_tickers()
        for t in known_tickers:
            if t in p_upper:
                target_ticker = t
                break
        
        if not target_ticker:
            # Fallback: check for any word > 2 chars that looks like a ticker
            # This is naive but works for a demo
            for w in words:
                if w.isalpha() and len(w) > 2 and w not in ["ANALYZE", "STOCK", "SHOW", "ME", "THE", "ABOUT", "WHAT", "GIVE", "FUNDAMENTALS"]:
                    target_ticker = w
                    break
        
        if target_ticker:
            st.session_state["selected_ticker"] = target_ticker
            
            # Decide action
            if "COMPARE" in p_upper:
                # Naive extract 2 tickers
                # Split words, check against rules
                found_tickers = []
                for w in words:
                    # Clean punctuation
                    w_clean = w.strip(",.")
                    if w_clean in known_tickers:
                        found_tickers.append(w_clean)
                        continue
                    
                    # Fallback heuristic
                    if w_clean.isalpha() and len(w_clean) > 2 and w_clean not in ["COMPARE", "WITH", "AND", "VS", "BETWEEN", "STOCK", "STOCKS"]:
                        # Avoid duplicates
                        if w_clean not in found_tickers:
                           found_tickers.append(w_clean)
                
                if len(found_tickers) >= 2:
                    st.session_state["selected_ticker"] = found_tickers[0]
                    st.session_state["compare_ticker"] = found_tickers[1]
                    response_text = f"Comparing {found_tickers[0]} vs {found_tickers[1]}. Check the 'Comparison' tab."
                else:
                    response_text = "I need two distinct tickers to compare. Try 'Compare TCS vs INFY'."

            elif "FUNDAMENTAL" in p_upper or "ANALYZE" in p_upper or "PROS" in p_upper:
                st.session_state["selected_ticker"] = target_ticker
                # Clear comparison if just analyzing one
                if "compare_ticker" in st.session_state:
                    del st.session_state["compare_ticker"]
                
                # Fetch Data
                with st.spinner(f"Analyzing {target_ticker}..."):
                    info, financials = get_stock_fundamentals(target_ticker)
                    analysis = analyze_fundamentals(target_ticker, info, financials)
                    
                    response_text = f"**Analysis for {target_ticker}**\n\n"
                    response_text += f"{analysis['summary']}\n\n"
                    
                    if analysis['positives']:
                        response_text += "**✅ Positives:**\n" + "\n".join([f"- {x}" for x in analysis['positives']]) + "\n\n"
                    
                    if analysis['negatives']:
                        response_text += "**❌ Negatives:**\n" + "\n".join([f"- {x}" for x in analysis['negatives']])
                    
                    st.session_state['analysis_result'] = analysis
            
            else:
                st.session_state["selected_ticker"] = target_ticker
                # Clear comparison
                if "compare_ticker" in st.session_state:
                    del st.session_state["compare_ticker"]
                    
                response_text = f"I've loaded the charts for {target_ticker}. Ask 'Analyze {target_ticker}' for fundamental insights."

        # Update Chat
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.chat_message("assistant").write(response_text)
        
        # Trigger Rerun to update charts on the right (Streamlit quirk: need to rerun to propagate session state to other cols immediately if they are outside this func scope, 
        # but since we call render_chart typically AFTER or separate, we might rely on auto-rerun or st.experimental_rerun())
        st.rerun()
