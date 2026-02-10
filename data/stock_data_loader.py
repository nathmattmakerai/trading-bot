"""
Loader pour les données actions et sentiment via Yahoo Finance.
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
import datetime

class StockDataLoader:
    def __init__(self):
        pass

    def get_stock_data(self, tickers: List[str], period: str = "1mo", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Récupère les données historiques pour une liste de tickers.
        """
        data = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval)
                if not df.empty:
                    data[ticker] = df
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
        return data

    def get_stock_info(self, ticker: str) -> dict:
        """
        Récupère les informations fondamentales d'une action.
        """
        try:
            stock = yf.Ticker(ticker)
            return stock.info
        except:
            return {}

    def get_stock_news(self, ticker: str) -> List[dict]:
        """
        Récupère les dernières actualités pour un ticker.
        """
        try:
            stock = yf.Ticker(ticker)
            return stock.news
        except:
            return []
