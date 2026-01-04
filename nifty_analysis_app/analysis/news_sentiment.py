
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from duckduckgo_search import DDGS
import time

class NewsAnalyzer:
    def __init__(self):
        self.ddgs = DDGS()

    def fetch_news(self, ticker, limit=10):
        """Fetches news specifically using the 'news' backend of DuckDuckGo."""
        query = f"{ticker} stock news India"
        try:
            # timelimit='w' for past week to cover yesterday and today + buffer
            results = self.ddgs.news(query, max_results=limit, timelimit="w")
            return results
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def fetch_social(self, ticker, platform="twitter", limit=5):
        """
        Fetches 'social' content by searching for the ticker on specific platforms.
        Note: This is a search-based approximation since direct scraping is blocked.
        """
        site_map = {
            "twitter": "site:twitter.com",
            "youtube": "site:youtube.com",
            "reddit": "site:reddit.com",
            "facebook": "site:facebook.com",
            "instagram": "site:instagram.com",
            "linkedin": "site:linkedin.com"
        }
        site_query = site_map.get(platform, "")
        if not site_query:
            # Fallback if platform not in map
            site_query = f'site:{platform}.com'
            
        query = f"{site_query} {ticker} stock market"
        
        try:
            # using 'text' backend for general web search with time limit
            # timelimit='w' (past week) ensures we get recent discussions including yesterday/today
            results = self.ddgs.text(query, max_results=limit, timelimit="w")
            return results
        except Exception as e:
            print(f"Error fetching social for {platform}: {e}")
            return []

    def analyze_sentiment(self, texts):
        """
        Analyzes sentiment of a list of text strings.
        Returns a DataFrame with polarity and subjectivity.
        """
        if not texts:
            return pd.DataFrame()
            
        data = []
        for t in texts:
            if not t: continue
            blob = TextBlob(t)
            data.append({
                "text": t,
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
                "verdict": self._get_verdict(blob.sentiment.polarity)
            })
            
        return pd.DataFrame(data)

    def _get_verdict(self, polarity):
        if polarity > 0.1: return "Bullish"
        if polarity < -0.1: return "Bearish"
        return "Neutral"

    def generate_wordcloud(self, text_list):
        """Generates a WordCloud object from a list of texts."""
        if not text_list:
            return None
            
        combined_text = " ".join(text_list)
        # Create a simple word cloud
        wc = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
        return wc
