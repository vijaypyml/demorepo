
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis.news_sentiment import NewsAnalyzer

def render_news_view(ticker):
    st.header(f"News & Sentiment Analysis: {ticker}")
    
    analyzer = NewsAnalyzer()
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["Market Pulse", "Social Buzz"])
    
    with tab1:
        st.subheader("Latest News")
        with st.spinner("Fetching latest news..."):
            news_items = analyzer.fetch_news(ticker)
        
        if news_items:
            # Prepare text for analysis
            news_texts = [item.get('title', '') + " " + item.get('body', '') for item in news_items]
            
            # Sentiment Analysis
            df_sentiment = analyzer.analyze_sentiment(news_texts)
            
            if not df_sentiment.empty:
                avg_polarity = df_sentiment['polarity'].mean()
                st.metric("Overall News Sentiment", f"{avg_polarity:.2f}", 
                         delta="Bullish" if avg_polarity > 0.05 else "Bearish" if avg_polarity < -0.05 else "Neutral")
            
            # Display News Cards
            for item in news_items:
                with st.expander(item.get('title', 'No Title')):
                    st.write(item.get('body', ''))
                    st.caption(f"Source: {item.get('source', 'Unknown')} | [Read More]({item.get('url', '#')})")
            
            # Word Cloud
            st.subheader("News Word Cloud")
            wc = analyzer.generate_wordcloud(news_texts)
            if wc:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
        else:
            st.info("No recent news found.")

    with tab2:
        st.subheader("Social Media Aggregation")
        platform = st.selectbox("Select Platform", ["twitter", "youtube", "reddit", "facebook", "instagram", "linkedin"])
        
        with st.spinner(f"Searching {platform}..."):
            social_items = analyzer.fetch_social(ticker, platform)
            
        if social_items:
             # Prepare text for analysis
            social_texts = [item.get('title', '') + " " + item.get('body', '') for item in social_items]
            
            # Sentiment
            df_social_sent = analyzer.analyze_sentiment(social_texts)
            if not df_social_sent.empty:
                avg_social_pol = df_social_sent['polarity'].mean()
                st.metric(f"{platform.capitalize()} Sentiment", f"{avg_social_pol:.2f}")

            for item in social_items:
                st.markdown(f"**[{item.get('title', 'Post')}]({item.get('href', '#')})**")
                st.write(item.get('body', ''))
                st.divider()
        else:
            st.info(f"No recent buzz found on {platform}.")
