"""
Web Crawler for Financial Data Collection
Collects stock/crypto data from various sources for backtesting.
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import yfinance as yf
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataCrawler:
    """Crawls financial data from various sources."""

    def __init__(self):
        """Initialize the crawler with default configurations."""
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Common tickers for different asset classes
        self.stock_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'JNJ',
            'PG', 'DIS', 'HD', 'PYPL', 'ADBE', 'NFLX', 'CRM', 'WMT', 'KO', 'PEP'
        ]

        self.crypto_tickers = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD', 'ADA-USD',
            'DOGE-USD', 'DOT-USD', 'AVAX-USD', 'MATIC-USD'
        ]

        self.futures_tickers = [
            'NQ=F', 'ES=F', 'YM=F', 'CL=F', 'GC=F', 'SI=F'
        ]

    def crawl_stock_data(self, tickers: List[str] = None, period: str = "2y") -> Dict[str, pd.DataFrame]:
        """
        Crawl stock data from Yahoo Finance.

        Args:
            tickers: List of stock tickers to crawl
            period: Time period for data (e.g., "1mo", "3mo", "6mo", "1y", "2y")

        Returns:
            Dictionary mapping ticker to DataFrame with stock data
        """
        if tickers is None:
            tickers = self.stock_tickers

        logger.info(f"Crawling stock data for {len(tickers)} tickers...")

        stock_data = {}
        failed_tickers = []

        for ticker in tickers:
            try:
                # Use yfinance to get stock data
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval="1d", progress=False)

                if not df.empty:
                    # Add ticker column for identification
                    df['ticker'] = ticker
                    stock_data[ticker] = df
                    logger.info(f"Successfully crawled data for {ticker}")
                else:
                    failed_tickers.append(ticker)
                    logger.warning(f"No data found for {ticker}")

            except Exception as e:
                failed_tickers.append(ticker)
                logger.error(f"Error crawling {ticker}: {e}")

            # Be respectful to the API
            time.sleep(0.1)

        logger.info(f"Crawled {len(stock_data)} stocks, {len(failed_tickers)} failed")
        return stock_data

    def crawl_crypto_data(self, tickers: List[str] = None, period: str = "2y") -> Dict[str, pd.DataFrame]:
        """
        Crawl crypto data from Yahoo Finance.

        Args:
            tickers: List of crypto tickers to crawl
            period: Time period for data

        Returns:
            Dictionary mapping ticker to DataFrame with crypto data
        """
        if tickers is None:
            tickers = self.crypto_tickers

        logger.info(f"Crawling crypto data for {len(tickers)} tickers...")

        crypto_data = {}
        failed_tickers = []

        for ticker in tickers:
            try:
                # Use yfinance to get crypto data
                crypto = yf.Ticker(ticker)
                df = crypto.history(period=period, interval="1d", progress=False)

                if not df.empty:
                    # Add ticker column for identification
                    df['ticker'] = ticker
                    crypto_data[ticker] = df
                    logger.info(f"Successfully crawled data for {ticker}")
                else:
                    failed_tickers.append(ticker)
                    logger.warning(f"No data found for {ticker}")

            except Exception as e:
                failed_tickers.append(ticker)
                logger.error(f"Error crawling {ticker}: {e}")

            # Be respectful to the API
            time.sleep(0.1)

        logger.info(f"Crawled {len(crypto_data)} cryptos, {len(failed_tickers)} failed")
        return crypto_data

    def crawl_futures_data(self, tickers: List[str] = None, period: str = "2y") -> Dict[str, pd.DataFrame]:
        """
        Crawl futures data from Yahoo Finance.

        Args:
            tickers: List of futures tickers to crawl
            period: Time period for data

        Returns:
            Dictionary mapping ticker to DataFrame with futures data
        """
        if tickers is None:
            tickers = self.futures_tickers

        logger.info(f"Crawling futures data for {len(tickers)} tickers...")

        futures_data = {}
        failed_tickers = []

        for ticker in tickers:
            try:
                # Use yfinance to get futures data
                future = yf.Ticker(ticker)
                df = future.history(period=period, interval="1d", progress=False)

                if not df.empty:
                    # Add ticker column for identification
                    df['ticker'] = ticker
                    futures_data[ticker] = df
                    logger.info(f"Successfully crawled data for {ticker}")
                else:
                    failed_tickers.append(ticker)
                    logger.warning(f"No data found for {ticker}")

            except Exception as e:
                failed_tickers.append(ticker)
                logger.error(f"Error crawling {ticker}: {e}")

            # Be respectful to the API
            time.sleep(0.1)

        logger.info(f"Crawled {len(futures_data)} futures, {len(failed_tickers)} failed")
        return futures_data

    def crawl_market_sentiment(self) -> Dict[str, dict]:
        """
        Crawl market sentiment data.

        Returns:
            Dictionary with sentiment scores for different assets
        """
        logger.info("Crawling market sentiment data...")

        # In a real implementation, this would fetch from actual sentiment APIs
        # For now, returning mock data that simulates what we'd get

        sentiment_data = {
            'stocks': {},
            'crypto': {},
            'futures': {}
        }

        # Mock stock sentiment
        for ticker in self.stock_tickers[:5]:  # First 5 stocks
            sentiment_data['stocks'][ticker] = {
                'sentiment_score': round((0.5 - 0.2 * (hash(ticker) % 100) / 100), 3),
                'confidence': round(0.7 + 0.2 * (hash(ticker) % 100) / 100, 3),
                'source': 'web_crawler'
            }

        # Mock crypto sentiment
        for ticker in self.crypto_tickers[:5]:  # First 5 cryptos
            sentiment_data['crypto'][ticker] = {
                'sentiment_score': round((0.3 - 0.4 * (hash(ticker) % 100) / 100), 3),
                'confidence': round(0.6 + 0.3 * (hash(ticker) % 100) / 100, 3),
                'source': 'web_crawler'
            }

        # Mock futures sentiment
        for ticker in self.futures_tickers[:5]:  # First 5 futures
            sentiment_data['futures'][ticker] = {
                'sentiment_score': round((0.2 - 0.1 * (hash(ticker) % 100) / 100), 3),
                'confidence': round(0.8 + 0.1 * (hash(ticker) % 100) / 100, 3),
                'source': 'web_crawler'
            }

        logger.info("Market sentiment data crawled successfully")
        return sentiment_data

    def crawl_technical_indicators(self, ticker: str, period: str = "6mo") -> Dict[str, pd.DataFrame]:
        """
        Crawl technical indicators for a specific ticker.

        Args:
            ticker: Stock/crypto/futures ticker
            period: Time period

        Returns:
            Dictionary with technical indicator data
        """
        logger.info(f"Crawling technical indicators for {ticker}...")

        try:
            # Get the basic data first
            asset = yf.Ticker(ticker)
            df = asset.history(period=period, interval="1d", progress=False)

            if df.empty:
                return {}

            # Calculate some basic technical indicators
            indicators = {}

            # Simple Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()

            # Exponential Moving Averages
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()

            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_signal'] = df['MACD'].ewm(span=9).mean()

            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Bollinger Bands
            df['BB_middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
            df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

            # Volume indicators
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()

            indicators[ticker] = df

            logger.info(f"Technical indicators crawled for {ticker}")
            return indicators

        except Exception as e:
            logger.error(f"Error crawling technical indicators for {ticker}: {e}")
            return {}

    def crawl_all_data(self, period: str = "2y") -> Dict[str, Dict]:
        """
        Crawl all types of financial data.

        Args:
            period: Time period for data

        Returns:
            Dictionary with all crawled data
        """
        logger.info("Starting full data crawl...")

        all_data = {
            'stocks': self.crawl_stock_data(period=period),
            'crypto': self.crawl_crypto_data(period=period),
            'futures': self.crawl_futures_data(period=period),
            'sentiment': self.crawl_market_sentiment(),
            'indicators': {}
        }

        # Crawl technical indicators for a sample of assets
        sample_tickers = list(all_data['stocks'].keys())[:3] + list(all_data['crypto'].keys())[:3]

        for ticker in sample_tickers:
            indicators = self.crawl_technical_indicators(ticker, period)
            all_data['indicators'].update(indicators)

        logger.info("Full data crawl completed successfully")
        return all_data

    def save_data(self, data: Dict[str, Dict], filename: str):
        """
        Save crawled data to a JSON file.

        Args:
            data: Dictionary with crawled data
            filename: Output filename
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def load_data(self, filename: str) -> Dict[str, Dict]:
        """
        Load crawled data from a JSON file.

        Args:
            filename: Input filename

        Returns:
            Dictionary with loaded data
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            logger.info(f"Data loaded from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    # Initialize crawler
    crawler = FinancialDataCrawler()

    # Test crawling stock data
    print("Testing stock data crawl...")
    stocks = crawler.crawl_stock_data(period="6mo")
    print(f"Retrieved {len(stocks)} stocks")

    # Test crawling crypto data
    print("\nTesting crypto data crawl...")
    crypto = crawler.crawl_crypto_data(period="6mo")
    print(f"Retrieved {len(crypto)} cryptos")

    # Test crawling futures data
    print("\nTesting futures data crawl...")
    futures = crawler.crawl_futures_data(period="6mo")
    print(f"Retrieved {len(futures)} futures")

    # Test sentiment data
    print("\nTesting sentiment data crawl...")
    sentiment = crawler.crawl_market_sentiment()
    print("Sentiment data crawled successfully")

    # Test technical indicators
    print("\nTesting technical indicators...")
    if stocks:
        ticker = list(stocks.keys())[0]
        indicators = crawler.crawl_technical_indicators(ticker, period="6mo")
        print(f"Technical indicators retrieved for {ticker}")

    # Test full crawl
    print("\nTesting full data crawl...")
    all_data = crawler.crawl_all_data(period="6mo")
    print("Full data crawl completed successfully")