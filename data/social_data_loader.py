"""
Loader pour les données sociales (X/Twitter).
Note: L'accès à l'API X nécessite normalement une clé API. 
Ce module fournit une structure pour l'analyse de sentiment.
"""
import random
from typing import List, Dict

class SocialDataLoader:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def get_x_sentiment(self, ticker: str) -> dict:
        """
        Analyse le sentiment sur X pour un ticker donné.
        Simulation pour la démo si pas d'API.
        """
        # Dans une version réelle, on utiliserait Tweepy ou un scrapper
        # Ici on simule un score basé sur des mots clés fictifs
        
        sentiments = ["Positive", "Neutral", "Negative", "Bullish", "Bearish"]
        weights = [0.4, 0.3, 0.1, 0.15, 0.05] # Légèrement biaisé positif pour la démo
        
        chosen = random.choices(sentiments, weights=weights)[0]
        score = random.uniform(0.5, 0.9) if "Positive" in chosen or "Bullish" in chosen else random.uniform(0.1, 0.4)
        
        return {
            "ticker": ticker,
            "platform": "X (Twitter)",
            "sentiment": chosen,
            "score": round(score, 2),
            "volume_24h": random.randint(500, 5000),
            "top_hashtags": [f"#{ticker}", "#Trading", "#StockMarket"]
        }

    def get_batch_sentiment(self, tickers: List[str]) -> Dict[str, dict]:
        return {ticker: self.get_x_sentiment(ticker) for ticker in tickers}
