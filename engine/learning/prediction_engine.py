"""
Moteur de prévision combinant analyse technique et sentiment social.
"""
import pandas as pd
import numpy as np
from typing import List, Dict

class PredictionEngine:
    def __init__(self):
        pass

    def generate_stock_prediction(self, ticker: str, price_df: pd.DataFrame, social_data: dict) -> dict:
        """
        Génère une prévision pour un ticker donné.
        Combine RSI, SMA et Sentiment.
        """
        if price_df.empty:
            return {"ticker": ticker, "prediction": "N/A", "confidence": 0}

        # 1. Analyse Technique simple
        close = price_df["Close"]
        sma_20 = close.rolling(window=20).mean().iloc[-1]
        last_price = close.iloc[-1]
        
        # RSI simplifié
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # 2. Score de Sentiment
        sentiment_score = social_data.get("score", 0.5)
        
        # 3. Algorithme de prévision (Heuristique)
        # On définit une tendance basée sur RSI + SMA + Sentiment
        tech_score = 0
        if rsi < 30: tech_score += 0.3 # Oversold
        if rsi > 70: tech_score -= 0.3 # Overbought
        if last_price > sma_20: tech_score += 0.2 # Trend Bull
        
        total_score = (tech_score + (sentiment_score - 0.5)) * 10
        
        prediction = "HOLD"
        if total_score > 2: prediction = "BUY"
        elif total_score > 5: prediction = "STRONG BUY"
        elif total_score < -2: prediction = "SELL"
        elif total_score < -5: prediction = "STRONG SELL"
        
        confidence = min(abs(total_score) * 10, 95)
        
        # Target Price (fictif pour démo)
        target_price = last_price * (1 + total_score/100)

        return {
            "ticker": ticker,
            "last_price": round(last_price, 2),
            "target_price": round(target_price, 2),
            "prediction": prediction,
            "confidence": round(confidence, 1),
            "rsi": round(rsi, 1),
            "sentiment": social_data.get("sentiment"),
            "sentiment_score": social_data.get("score"),
            "analysis": f"RSI is {round(rsi, 1)}. Sentiment on X is {social_data.get('sentiment')}."
        }

    def predict_batch(self, tickers: List[str], data_dict: Dict[str, pd.DataFrame], social_dict: Dict[str, dict]) -> List[dict]:
        predictions = []
        for ticker in tickers:
            if ticker in data_dict and ticker in social_dict:
                pred = self.generate_stock_prediction(ticker, data_dict[ticker], social_dict[ticker])
                predictions.append(pred)
        return predictions
