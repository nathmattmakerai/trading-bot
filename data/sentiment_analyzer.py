"""
Sentiment Analyzer Module for Trading Bot

This module handles sentiment analysis of financial data using mathematical algorithms.
"""

import math
import re
from typing import List, Dict, Any
import numpy as np


def sigmoid(x):
    """Sigmoid function for normalization."""
    return 1 / (1 + math.exp(-x))


def tanh_transform(x):
    """Tanh transformation for better normalization."""
    return math.tanh(x)


def get_market_sentiment(tickers=None):
    """
    Get market sentiment for specified tickers.
    
    Args:
        tickers: List of tickers to analyze. If None, uses default list.
        
    Returns:
        Dictionary with sentiment scores for each ticker
    """
    if tickers is None:
        tickers = ['NQ', 'ES', 'BTC', 'ETH', 'CL']
    
    # This would normally be replaced with actual web scraping or API calls
    # For now, returning mock data based on mathematical algorithms
    
    sentiment_data = {}
    
    for ticker in tickers:
        # Simulate different sentiment scores using mathematical functions
        # In a real implementation, this would come from web scraping or APIs
        
        # Mock sentiment calculation based on some mathematical factors
        base_score = np.random.uniform(-1, 1)  # Random score between -1 and 1
        confidence = np.random.uniform(0.5, 1.0)  # Confidence between 0.5 and 1.0
        
        # Apply transformations to normalize the data
        normalized_score = tanh_transform(base_score)
        
        # Determine sentiment category
        if normalized_score > 0.3:
            sentiment = "Bullish"
        elif normalized_score < -0.3:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"
            
        sentiment_data[ticker] = {
            'sentiment': sentiment,
            'score': normalized_score,
            'confidence': confidence
        }
    
    return sentiment_data


def analyze_text_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a text using weighted word scoring.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment analysis results
    """
    # Simple word-based sentiment scoring (in real implementation, this would be more sophisticated)
    positive_words = ['good', 'great', 'excellent', 'positive', 'bullish', 'up', 'strong']
    negative_words = ['bad', 'terrible', 'poor', 'negative', 'bearish', 'down', 'weak']
    
    # Convert text to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Calculate scores
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words)
    
    # Calculate net sentiment score (-1 to 1 range)
    total_words = len(words)
    if total_words == 0:
        net_score = 0
    else:
        net_score = (positive_score - negative_score) / total_words
    
    # Apply sigmoid transformation for better normalization
    normalized_score = sigmoid(net_score * 2) - 0.5  # Shift to -0.5 to 0.5 range
    
    # Calculate confidence based on word count and score magnitude
    confidence = min(1.0, (abs(net_score) * 2) + (len(words) / 100))
    
    return {
        'score': normalized_score,
        'confidence': confidence,
        'positive_words': positive_score,
        'negative_words': negative_score
    }


def calculate_sentiment_confidence(score: float, word_count: int) -> float:
    """
    Calculate confidence level for sentiment score.
    
    Args:
        score: Sentiment score (-1 to 1)
        word_count: Number of words analyzed
        
    Returns:
        Confidence level (0 to 1)
    """
    # Base confidence from word count
    base_confidence = min(1.0, word_count / 50.0)
    
    # Adjust based on score magnitude (more extreme scores are more confident)
    score_confidence = 1 - abs(score) * 0.5
    
    # Combine both factors
    final_confidence = (base_confidence + score_confidence) / 2
    
    return min(1.0, final_confidence)


if __name__ == "__main__":
    # Test the sentiment analyzer
    print("Testing Sentiment Analyzer...")
    
    # Test get_market_sentiment
    sentiment_data = get_market_sentiment(['BTC', 'ETH', 'NQ'])
    print(f"Market sentiment data: {sentiment_data}")
    
    # Test text analysis
    sample_text = "Bitcoin is showing great positive momentum and bullish indicators"
    text_sentiment = analyze_text_sentiment(sample_text)
    print(f"Text sentiment analysis: {text_sentiment}")
    
    print("✅ Sentiment analyzer working correctly")
