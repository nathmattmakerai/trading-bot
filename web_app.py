"""FTMO Futures Bot - Web Interface"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
from datetime import datetime
import json
import os
import logging

# Configure logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from main import TradingBot
    from config.rules_v1 import vv1_FROZEN
    # Import our enhanced sentiment analysis
    from data.sentiment_analyzer import get_market_sentiment
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    exit(1)

app = Flask(__name__)
CORS(app)
bot = None

# Rate Limiting
RATE_LIMIT_FILE = "rate_limit.json"
RATE_LIMIT_MAX = 100
RATE_LIMIT_WINDOW = 86400

def load_rate_limit_data():
    if os.path.exists(RATE_LIMIT_FILE):
        try:
            with open(RATE_LIMIT_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"count": 0, "reset_time": datetime.now().timestamp()}
    return {"count": 0, "reset_time": datetime.now().timestamp()}

def save_rate_limit_data(data):
    try:
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def check_rate_limit():
    data = load_rate_limit_data()
    current_time = datetime.now().timestamp()
    
    if current_time - data["reset_time"] > RATE_LIMIT_WINDOW:
        data = {"count": 0, "reset_time": current_time}
        save_rate_limit_data(data)
        return True, 0
    
    if data["count"] >= RATE_LIMIT_MAX:
        return False, data["count"]
    
    data["count"] += 1
    save_rate_limit_data(data)
    return True, data["count"]

def get_rate_limit_status():
    data = load_rate_limit_data()
    current_time = datetime.now().timestamp()
    time_remaining = max(0, RATE_LIMIT_WINDOW - (current_time - data["reset_time"]))
    return {"count": data["count"], "max": RATE_LIMIT_MAX, "time_remaining": int(time_remaining)}

CONFIG_FILE = "config_editable.json"

def load_editable_config():
    """Load editable configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Return default config from vv1_FROZEN
    cfg = {}
    for k, v in vv1_FROZEN.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if not isinstance(v2, dict):
                    cfg[k2] = v2
    return cfg

def save_editable_config(config):
    """Save editable configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def init_bot():
    global bot
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    logger.info("Initializing TradingBot...")
    try:
        bot = TradingBot(starting_balance=10000.0)
        logger.info("TradingBot initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize TradingBot: {e}")
        raise

def get_sp500_news():
    return [
        {"title": "S&P 500 jumps 1.2% on positive data", "source": "CNBC", "time": "Today"},
        {"title": "Tech stocks lead gains", "source": "Bloomberg", "time": "Today"},
        {"title": "Market breadth improves", "source": "Reuters", "time": "Today"},
        {"title": "VIX falls to 3-month low", "source": "MarketWatch", "time": "Today"},
        {"title": "Earnings beat expectations", "source": "CNBC", "time": "Today"},
        {"title": "Index closes at record high", "source": "Bloomberg", "time": "Today"},
        {"title": "Fed signals patience", "source": "Reuters", "time": "Today"},
        {"title": "Market sentiment improves", "source": "MarketWatch", "time": "Today"},
        {"title": "Strong employment data", "source": "CNBC", "time": "Today"},
        {"title": "Inflation concerns ease", "source": "Bloomberg", "time": "Today"}
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    init_bot()
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    try:
        init_bot()
        return jsonify({"status": "ok", "message": "System is running"})
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/backtest/run', methods=['POST'])
def backtest_run():
    """Run a backtest with the specified parameters"""
    logger.info("Backtest run endpoint called")
    try:
        init_bot()
        # Get JSON data from request
        d = request.get_json()
        if not d:
            logger.warning("No JSON data received in backtest request")
            return jsonify({"ok": False, "err": "Invalid JSON data"}), 400
        
        # Validate required parameters
        required_fields = ['inst', 'st', 'ed']
        for field in required_fields:
            if field not in d:
                logger.warning(f"Missing required field: {field}")
                return jsonify({"ok": False, "err": f"Missing required field: {field}"}), 400
        
        instrument = d['inst']
        start_date = d['st']
        end_date = d['ed']
        
        logger.info(f"Starting backtest for {instrument} from {start_date} to {end_date}")
        
        # Run the backtest
        result = bot.backtest(instrument, start_date, end_date)
        
        logger.info("Backtest completed successfully")
        return jsonify({"ok": True, "res": result})
        
    except Exception as e:
        error_msg = f"Error during backtest: {str(e)}"
        logger.error(error_msg, exc_info=True)  # Log the full traceback
        return jsonify({"ok": False, "err": error_msg}), 500

@app.route('/api/conf')
def conf():
    return jsonify(load_editable_config())

@app.route('/api/save-config', methods=['POST'])
def save_config():
    try:
        config_data = request.json
        if save_editable_config(config_data):
            return jsonify({"success": True, "message": "Configuration saved"})
        else:
            return jsonify({"success": False, "message": "Failed to save configuration"})
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/test')
def test():
    try:
        init_bot()
        return jsonify({"success": True, "msg": "System Ready"})
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return jsonify({"success": False, "err": str(e)})

@app.route('/api/evolve', methods=['POST'])
def evolve():
    try:
        init_bot()
        d = request.json
        
        # Get evolution parameters from request
        instrument = d.get('inst', 'NQ')
        start_date = d.get('st', '2024-01-01')
        end_date = d.get('ed', '2024-06-30')
        generations = d.get('gens', 1000)
        population_size = d.get('pop', 50)
        mutation_rate = d.get('mut', 0.1)
        
        # Run evolutionary backtest
        result = bot.evolve_backtest(
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            generations=generations,
            population_size=population_size,
            mutation_rate=mutation_rate
        )
        
        return jsonify({"ok": True, "res": result})
    except Exception as e:
        error_msg = f"Error in evolve: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"ok": False, "err": error_msg}), 500

@app.route('/api/news')
def news():
    return jsonify({"news": get_sp500_news()})

# Global error handlers to ensure JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"ok": False, "err": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({"ok": False, "err": "Endpoint not found"}), 404


# Rate Limiting
RATE_LIMIT_FILE = "rate_limit.json"
RATE_LIMIT_MAX = 100
RATE_LIMIT_WINDOW = 86400

def load_rate_limit_data():
    if os.path.exists(RATE_LIMIT_FILE):
        try:
            with open(RATE_LIMIT_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"count": 0, "reset_time": datetime.now().timestamp()}
    return {"count": 0, "reset_time": datetime.now().timestamp()}

def save_rate_limit_data(data):
    try:
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def check_rate_limit():
    data = load_rate_limit_data()
    current_time = datetime.now().timestamp()
    
    if current_time - data["reset_time"] > RATE_LIMIT_WINDOW:
        data = {"count": 0, "reset_time": current_time}
        save_rate_limit_data(data)
        return True, 0
    
    if data["count"] >= RATE_LIMIT_MAX:
        return False, data["count"]
    
    data["count"] += 1
    save_rate_limit_data(data)
    return True, data["count"]

def get_rate_limit_status():
    data = load_rate_limit_data()
    current_time = datetime.now().timestamp()
    time_remaining = max(0, RATE_LIMIT_WINDOW - (current_time - data["reset_time"]))
    return {"count": data["count"], "max": RATE_LIMIT_MAX, "time_remaining": int(time_remaining)}

CONFIG_FILE = "config_editable.json"

def load_editable_config():
    """Load editable configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Return default config from vv1_FROZEN
    cfg = {}
    for k, v in vv1_FROZEN.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if not isinstance(v2, dict):
                    cfg[k2] = v2
    return cfg

def save_editable_config(config):
    """Save editable configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def init_bot():
    global bot
    bot = TradingBot(starting_balance=10000.0)

def get_sp500_news():
    return [
        {"title": "S&P 500 jumps 1.2% on positive data", "source": "CNBC", "time": "Today"},
        {"title": "Tech stocks lead gains", "source": "Bloomberg", "time": "Today"},
        {"title": "Market breadth improves", "source": "Reuters", "time": "Today"},
        {"title": "VIX falls to 3-month low", "source": "MarketWatch", "time": "Today"},
        {"title": "Earnings beat expectations", "source": "CNBC", "time": "Today"},
        {"title": "Index closes at record high", "source": "Bloomberg", "time": "Today"},
        {"title": "Fed signals patience", "source": "Reuters", "time": "Today"},
        {"title": "Market sentiment improves", "source": "MarketWatch", "time": "Today"},
        {"title": "Dividend stocks rally", "source": "CNBC", "time": "Today"},
        {"title": "Analysts raise targets", "source": "Bloomberg", "time": "Today"},
    ]

def get_market_overview():
    return {
        "S&P 500": {"price": 5234.78, "change": "+1.23%"},
        "Nasdaq": {"price": 16834.56, "change": "+1.56%"},
        "Dow Jones": {"price": 42234.12, "change": "+0.98%"},
        "VIX": {"price": 14.23, "change": "-2.15%"}
    }

def get_x_news():
    """Fetch tweets/posts from X about markets and trading"""
    # Demo data - can be replaced with real X API integration
    return [
        {"text": "📈 Market surge continues as tech stocks lead rally. VIX down to 14.2", "author": "@MarketNews", "likes": 1234, "time": "2m ago"},
        {"text": "🚀 Fed signals patience on rates. Positive outlook for equities.", "author": "@Bloomberg", "likes": 2156, "time": "15m ago"},
        {"text": "💡 Breakout alert: ES consolidating above key resistance. Watch for confirmation.", "author": "@TradingView", "likes": 892, "time": "32m ago"},
        {"text": "📊 Options flow shows institutional bullish positioning. Buy signals accumulating.", "author": "@OptionAnalytics", "likes": 765, "time": "45m ago"},
        {"text": "⚡ Earnings beat rate: 78% of S&P 500 companies exceed expectations this quarter.", "author": "@CNBC", "likes": 3421, "time": "1h ago"},
        {"text": "🎯 Technical setup forming on daily chart. RSI oversold conditions reverting.", "author": "@ChartPatterns", "likes": 1547, "time": "1h ago"},
        {"text": "💰 Sector rotation: Growth stocks outperforming. Momentum building.", "author": "@WallStreet", "likes": 2098, "time": "2h ago"},
        {"text": "🔔 Economic calendar: CPI data next week could impact direction. Prepare hedges.", "author": "@EconNews", "likes": 1876, "time": "2h ago"},
        {"text": "📈 NQ showing strength. Nasdaq futures up 0.8%. Tech momentum intact.", "author": "@FuturesWatch", "likes": 945, "time": "3h ago"},
        {"text": "⭐ Market breadth improving. More stocks above 200-day MA. Bullish signal.", "author": "@TechnicalAnalyst", "likes": 1654, "time": "3h ago"},
    ]

# Portfolio Management
HOLDINGS_FILE = "holdings.json"

def load_holdings():
    """Load user's stock holdings"""
    if os.path.exists(HOLDINGS_FILE):
        try:
            with open(HOLDINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    # Default holdings if file doesn't exist - 10 tracked stocks
    return {
        "TSLA": {"qty": 20, "price": 248.9, "profile": "Très volatile - gros mouvements", "volatility": "EXTREME", "risk": "High"},
        "NVDA": {"qty": 15, "price": 878.5, "profile": "Volatile avec tendance IA forte", "volatility": "HIGH", "risk": "Medium"},
        "AMD": {"qty": 30, "price": 165.2, "profile": "Bon pour swings techniques", "volatility": "HIGH", "risk": "Medium-High"},
        "COIN": {"qty": 25, "price": 125.8, "profile": "Dépend du marché crypto - très volatile", "volatility": "EXTREME", "risk": "High"},
        "AAPL": {"qty": 50, "price": 195.5, "profile": "Stable avec tendance propre", "volatility": "MEDIUM", "risk": "Low"},
        "MSFT": {"qty": 30, "price": 415.2, "profile": "Excellent pour trend following", "volatility": "MEDIUM", "risk": "Low"},
        "GOOGL": {"qty": 20, "price": 142.8, "profile": "Mouvements réguliers", "volatility": "MEDIUM", "risk": "Low-Medium"},
        "V": {"qty": 40, "price": 285.6, "profile": "Stable avec peu de bruit", "volatility": "LOW", "risk": "Low"},
        "KO": {"qty": 60, "price": 61.2, "profile": "Défensive - très stable", "volatility": "LOW", "risk": "Very Low"},
        "BRK.B": {"qty": 10, "price": 410.5, "profile": "Solide avec faible volatilité", "volatility": "LOW", "risk": "Very Low"},
    }

def save_holdings(holdings):
    """Save user's stock holdings"""
    try:
        with open(HOLDINGS_FILE, 'w') as f:
            json.dump(holdings, f, indent=2)
        return True
    except:
        return False

def get_holdings_news():
    """Get news for holdings"""
    holdings = load_holdings()
    news_data = {}
    
    stock_news = {
        "AAPL": [
            {"title": "Apple announces new AI features in upcoming iOS", "source": "CNBC", "sentiment": "positive"},
            {"title": "AAPL stock hits new record high", "source": "Bloomberg", "sentiment": "positive"},
            {"title": "Apple services revenue beats expectations", "source": "Reuters", "sentiment": "positive"},
        ],
        "MSFT": [
            {"title": "Microsoft AI integration boosts Q1 earnings", "source": "Bloomberg", "sentiment": "positive"},
            {"title": "Copilot adoption exceeds forecasts", "source": "CNBC", "sentiment": "positive"},
            {"title": "Azure cloud growth accelerates", "source": "Reuters", "sentiment": "positive"},
        ],
        "GOOGL": [
            {"title": "Google search dominance challenged by AI competitors", "source": "Reuters", "sentiment": "negative"},
            {"title": "Alphabet revenue growth meets expectations", "source": "Bloomberg", "sentiment": "neutral"},
            {"title": "YouTube advertising rebounds strongly", "source": "CNBC", "sentiment": "positive"},
        ],
        "NVDA": [
            {"title": "NVDA stock rallies on strong AI demand", "source": "CNBC", "sentiment": "positive"},
            {"title": "Nvidia GPU orders surge amid AI boom", "source": "Bloomberg", "sentiment": "positive"},
            {"title": "Data center segment drives record profits", "source": "Reuters", "sentiment": "positive"},
        ],
        "TSLA": [
            {"title": "Tesla Q1 deliveries exceed analyst estimates", "source": "Reuters", "sentiment": "positive"},
            {"title": "Elon Musk announces new Gigafactory expansion", "source": "CNBC", "sentiment": "positive"},
            {"title": "Tesla stock volatility continues amid market shifts", "source": "Bloomberg", "sentiment": "neutral"},
        ],
    }
    
    for ticker in holdings.keys():
        if ticker in stock_news:
            news_data[ticker] = stock_news[ticker]
        else:
            news_data[ticker] = [{"title": f"No recent news for {ticker}", "source": "System", "sentiment": "neutral"}]
    
    return news_data

def get_yahoo_finance_news():
    """Get live market news from Yahoo Finance (demo data)"""
    import random
    from datetime import datetime, timedelta
    
    # Demo news data simulating Yahoo Finance market data
    market_news = [
        {"title": "S&P 500 rallies 2.1% amid strong earnings reports", "source": "Yahoo Finance", "time": "now", "sentiment": "bullish", "category": "indices", "change": "+2.1%"},
        {"title": "Nasdaq 100 breaks above 16,800 resistance level", "source": "Yahoo Finance", "time": "2m ago", "sentiment": "bullish", "category": "indices", "change": "+2.45%"},
        {"title": "Tech sector leads market gains with AI momentum", "source": "Yahoo Finance", "time": "5m ago", "sentiment": "bullish", "category": "sector", "change": "+2.8%"},
        {"title": "Fed officials signal patience on rate cuts", "source": "MarketWatch", "time": "8m ago", "sentiment": "bullish", "category": "macro", "change": "N/A"},
        {"title": "Oil prices surge on supply concerns", "source": "Yahoo Finance", "time": "12m ago", "sentiment": "bearish", "category": "commodities", "change": "+3.2%"},
        {"title": "Semiconductor stocks spike on demand forecast upgrade", "source": "Reuters", "time": "15m ago", "sentiment": "bullish", "category": "sector", "change": "+4.1%"},
        {"title": "Treasury yields retreat as inflation eases", "source": "Bloomberg", "time": "18m ago", "sentiment": "bullish", "category": "fixed-income", "change": "-15 bps"},
        {"title": "Dollar weakens against major currencies", "source": "Yahoo Finance", "time": "20m ago", "sentiment": "bearish", "category": "forex", "change": "-0.8%"},
        {"title": "FOMC minutes show hawkish tone on inflation", "source": "CNBC", "time": "25m ago", "sentiment": "bearish", "category": "macro", "change": "N/A"},
        {"title": "European markets surge on economic recovery signs", "source": "Reuters", "time": "30m ago", "sentiment": "bullish", "category": "indices", "change": "+1.9%"},
    ]
    
    return market_news

def get_market_trend():
    """Get current market trend analysis"""
    return {
        "overall_trend": "BULLISH",
        "trend_strength": "STRONG",
        "sentiment": "+72%",
        "up_stocks": 2150,
        "down_stocks": 890,
        "unchanged_stocks": 260,
        "vix_level": 14.2,
        "vix_trend": "DOWN",
        "breadth": "POSITIVE",
        "volume_trend": "HIGH",
        "momentum": "POSITIVE",
        "support_level": 5180,
        "resistance_level": 5250,
        "key_levels": {
            "SPY_support": "₹512.50",
            "SPY_resistance": "₹518.20",
            "QQQ_support": "₹415.80",
            "QQQ_resistance": "₹428.50"
        }
    }

def get_predictions():
    """Get stock predictions and trading recommendations"""
    predictions = {
        "AAPL": {
            "ticker": "AAPL",
            "current_price": 195.5,
            "target_price": 210.0,
            "recommendation": "BUY",
            "confidence": "92%",
            "reason": "Strong uptrend, earnings beat, AI features driving growth",
            "technical_score": 8.5,
            "sentiment_score": 9.1,
            "momentum": "STRONG UP",
            "support": 190.0,
            "resistance": 200.0,
            "next_target": 215.0,
            "risk": "Low",
            "volatility": "MEDIUM",
            "profile": "Stable avec tendance propre",
            "timeframe": "3-6 months"
        },
        "MSFT": {
            "ticker": "MSFT",
            "current_price": 415.2,
            "target_price": 445.0,
            "recommendation": "BUY",
            "confidence": "89%",
            "reason": "AI integration success, Copilot adoption accelerating, cloud growth",
            "technical_score": 8.2,
            "sentiment_score": 8.8,
            "momentum": "STRONG UP",
            "support": 408.0,
            "resistance": 425.0,
            "next_target": 450.0,
            "risk": "Low",
            "volatility": "MEDIUM",
            "profile": "Excellent pour trend following",
            "timeframe": "2-4 months"
        },
        "GOOGL": {
            "ticker": "GOOGL",
            "current_price": 142.8,
            "target_price": 155.0,
            "recommendation": "HOLD",
            "confidence": "68%",
            "reason": "Mixed signals - revenue solid but AI competition rising, YouTube strong",
            "technical_score": 6.5,
            "sentiment_score": 6.9,
            "momentum": "MODERATE UP",
            "support": 138.0,
            "resistance": 148.0,
            "next_target": 160.0,
            "risk": "Low-Medium",
            "volatility": "MEDIUM",
            "profile": "Mouvements réguliers",
            "timeframe": "4-6 months"
        },
        "NVDA": {
            "ticker": "NVDA",
            "current_price": 878.5,
            "target_price": 950.0,
            "recommendation": "BUY",
            "confidence": "94%",
            "reason": "AI boom continues, GPU demand soaring, data center expansion accelerating",
            "technical_score": 9.2,
            "sentiment_score": 9.5,
            "momentum": "VERY STRONG UP",
            "support": 850.0,
            "resistance": 900.0,
            "next_target": 1000.0,
            "risk": "Medium",
            "volatility": "HIGH",
            "profile": "Volatile avec tendance IA forte",
            "timeframe": "2-3 months"
        },
        "TSLA": {
            "ticker": "TSLA",
            "current_price": 248.9,
            "target_price": 285.0,
            "recommendation": "BUY",
            "confidence": "75%",
            "reason": "Deliveries beat forecasts, Gigafactory expansion, EV demand growing",
            "technical_score": 7.8,
            "sentiment_score": 7.5,
            "momentum": "STRONG UP",
            "support": 230.0,
            "resistance": 265.0,
            "next_target": 300.0,
            "risk": "High",
            "volatility": "EXTREME",
            "profile": "Très volatile - gros mouvements",
            "timeframe": "2-3 weeks"
        },
        "AMD": {
            "ticker": "AMD",
            "current_price": 165.2,
            "target_price": 180.0,
            "recommendation": "BUY",
            "confidence": "82%",
            "reason": "Excellent pour swings techniques, strong technical setup",
            "technical_score": 8.7,
            "sentiment_score": 8.2,
            "momentum": "STRONG UP",
            "support": 160.0,
            "resistance": 170.0,
            "next_target": 190.0,
            "risk": "Medium-High",
            "volatility": "HIGH",
            "profile": "Bon pour swings techniques",
            "timeframe": "3-4 weeks"
        },
        "COIN": {
            "ticker": "COIN",
            "current_price": 125.8,
            "target_price": 150.0,
            "recommendation": "BUY",
            "confidence": "65%",
            "reason": "Dépend du marché crypto - très volatile mais tendance crypto positive",
            "technical_score": 7.2,
            "sentiment_score": 7.8,
            "momentum": "STRONG UP",
            "support": 115.0,
            "resistance": 135.0,
            "next_target": 160.0,
            "risk": "High",
            "volatility": "EXTREME",
            "profile": "Crypto-dependent - très volatile",
            "timeframe": "2-4 weeks"
        },
        "V": {
            "ticker": "V",
            "current_price": 285.6,
            "target_price": 310.0,
            "recommendation": "BUY",
            "confidence": "85%",
            "reason": "Stable avec peu de bruit, excellent trend following",
            "technical_score": 8.1,
            "sentiment_score": 8.4,
            "momentum": "MODERATE UP",
            "support": 275.0,
            "resistance": 295.0,
            "next_target": 320.0,
            "risk": "Low",
            "volatility": "LOW",
            "profile": "Stable avec peu de bruit",
            "timeframe": "4-6 months"
        },
        "KO": {
            "ticker": "KO",
            "current_price": 61.2,
            "target_price": 65.0,
            "recommendation": "HOLD",
            "confidence": "70%",
            "reason": "Défensive - très stable, faible volatilité",
            "technical_score": 6.5,
            "sentiment_score": 7.2,
            "momentum": "STEADY",
            "support": 59.0,
            "resistance": 62.5,
            "next_target": 66.0,
            "risk": "Very Low",
            "volatility": "LOW",
            "profile": "Défensive - très stable",
            "timeframe": "6-12 months"
        },
        "BRK.B": {
            "ticker": "BRK.B",
            "current_price": 410.5,
            "target_price": 440.0,
            "recommendation": "HOLD",
            "confidence": "78%",
            "reason": "Solide avec faible volatilité, bon hold long terme",
            "technical_score": 7.0,
            "sentiment_score": 7.6,
            "momentum": "STEADY",
            "support": 395.0,
            "resistance": 420.0,
            "next_target": 450.0,
            "risk": "Very Low",
            "volatility": "LOW",
            "profile": "Solide - faible volatilité",
            "timeframe": "6-12 months"
        }
    }
    return predictions

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>INSTITUTIONAL BOT</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { 
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
  min-height: 100vh;
  padding: 20px;
  color: #e0e0e0;
}
.container { max-width: 1200px; margin: 0 auto; }
header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.5); border: 1px solid #2d3561; }
h1 { color: #00d99f; font-size: 2em; margin-bottom: 10px; text-shadow: 0 0 10px rgba(0,217,159,0.3); }
.subtitle { color: #a0a0a0; font-size: 0.9em; }
nav { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
nav button { padding: 12px 24px; border: none; background: #2d3561; color: #b0b0b0; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; border: 1px solid #3d4571; }
nav button:hover { background: #3d4571; color: #00d99f; }
nav button.active { background: linear-gradient(135deg, #00d99f 0%, #00c986 100%); color: #0a0e27; }
.content { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 40px; border-radius: 15px; display: none; box-shadow: 0 5px 20px rgba(0,0,0,0.5); margin-bottom: 20px; border: 1px solid #2d3561; }
.content.active { display: block; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 20px 0; }
.card { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a3d 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #3d6b4f; }
.card .label { font-size: 0.85em; color: rgba(255,255,255,0.7); text-transform: uppercase; }
.card .value { font-size: 2em; font-weight: bold; margin-top: 10px; color: #00d99f; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
.item { background: #252d48; padding: 18px; border-radius: 10px; border-left: 4px solid #00d99f; }
.item .label { font-weight: 600; font-size: 0.85em; color: #a0a0a0; text-transform: uppercase; margin-bottom: 8px; }
.item .value { color: #00d99f; font-size: 1.2em; font-weight: bold; }
.news-card { background: #252d48; border-left: 4px solid #00d99f; padding: 20px; border-radius: 10px; margin-bottom: 15px; }
.news-title { font-weight: bold; color: #e0e0e0; margin-bottom: 8px; }
.news-source { font-size: 0.85em; color: #808080; margin-bottom: 5px; }
.news-time { font-size: 0.8em; color: #606060; }
.tweet-card { background: #252d48; border-left: 4px solid #ff6b6b; padding: 18px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.tweet-text { color: #e0e0e0; font-size: 0.95em; line-height: 1.5; margin-bottom: 10px; }
.tweet-author { font-weight: 600; color: #ff6b6b; font-size: 0.85em; margin-bottom: 5px; }
.tweet-engagement { display: flex; gap: 15px; font-size: 0.8em; color: #808080; margin-top: 10px; }
.tweet-engagement span { display: flex; align-items: center; gap: 4px; }
.holding-card { background: #252d48; border-left: 4px solid #00d99f; padding: 18px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.holding-ticker { font-weight: 700; color: #00d99f; font-size: 1.1em; margin-bottom: 8px; }
.holding-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 10px; }
.holding-stat { background: #1a2035; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #3d4571; }
.holding-label { font-size: 0.85em; color: #a0a0a0; text-transform: uppercase; }
.holding-value { font-weight: 600; color: #00d99f; font-size: 1.1em; margin-top: 5px; }
.news-item { background: #1a2035; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #00d99f; }
.news-item-title { font-weight: 600; color: #e0e0e0; margin-bottom: 4px; }
.news-item-meta { display: flex; gap: 10px; font-size: 0.85em; color: #808080; }
.positive { color: #00d99f; }
.negative { color: #ff6b6b; }
.neutral { color: #808080; }
.trend-card { background: #252d48; border-left: 5px solid #00d99f; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid #3d5f3d; }
.trend-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #3d4571; }
.trend-label { font-weight: 600; color: #e0e0e0; }
.trend-value { font-size: 1.1em; font-weight: 700; color: #00d99f; }
.trend-value.bearish { color: #ff6b6b; }
.status-card { background: #252d48; border-left: 5px solid #00d99f; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid #3d4571; }
.status-item { display: flex; justify-content: space-between; padding: 8px 0; }
.status-label { color: #a0a0a0; font-weight: 600; }
.status-value { font-weight: 700; color: #00d99f; }
.news-feed { margin-top: 15px; }
.news-headline { background: #252d48; border-left: 4px solid #ff9800; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.3); }
.news-headline.bullish { background: #1a3a2a; border-left-color: #00d99f; }
.news-headline.bearish { background: #3a1a1a; border-left-color: #ff6b6b; }
.headline-title { font-weight: 600; color: #e0e0e0; margin-bottom: 6px; font-size: 0.95em; }
.headline-meta { display: flex; gap: 12px; font-size: 0.8em; color: #808080; }
.headline-change { font-weight: 700; font-size: 1.1em; }
.bullish { color: #00d99f; }
.bearish { color: #ff6b6b; }
.predictions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-top: 20px; }
.prediction-card { background: #252d48; border-radius: 12px; border-left: 5px solid #00d99f; box-shadow: 0 4px 12px rgba(0,0,0,0.3); overflow: hidden; border: 1px solid #3d4571; }
.prediction-header { padding: 20px; background: linear-gradient(135deg, #1e3a5f 0%, #2d5a3d 100%); color: white; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3d5f3d; }
.prediction-ticker { font-size: 1.4em; font-weight: 700; color: #00d99f; }
.prediction-signal { font-size: 1.2em; padding: 6px 12px; border-radius: 20px; background: rgba(0,217,159,0.2); font-weight: 600; }
.prediction-signal.buy { background: rgba(0,217,159,0.3); color: #00d99f; }
.prediction-signal.hold { background: rgba(255,152,0,0.3); color: #ff9800; }
.prediction-signal.sell { background: rgba(255,107,107,0.3); color: #ff6b6b; }
.prediction-body { padding: 20px; }
.pred-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #3d4571; }
.pred-row:last-child { border-bottom: none; }
.pred-label { font-weight: 600; color: #a0a0a0; }
.pred-value { font-weight: 700; color: #00d99f; }
.pred-value.bullish { color: #00d99f; }
.pred-value.bearish { color: #ff6b6b; }
.pred-confidence { font-size: 1.3em; font-weight: 700; color: #00d99f; }
.pred-reason { background: #1a2035; padding: 12px; border-radius: 8px; margin: 12px 0; font-size: 0.9em; color: #c0c0c0; line-height: 1.5; border: 1px solid #3d4571; }
.pred-scores { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }
.score-box { background: #1a3a2a; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #3d5f3d; }
.score-label { font-size: 0.8em; color: #a0a0a0; font-weight: 600; }
.score-value { font-size: 1.3em; font-weight: 700; color: #00d99f; }
.pred-levels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 12px 0; }
.level-box { background: #1a2035; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #3d4571; }
.level-label { font-size: 0.75em; color: #808080; text-transform: uppercase; }
.level-value { font-weight: 700; color: #e0e0e0; }
.volatility-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85em; margin-left: 10px; }
.volatility-extreme { background: rgba(255,107,107,0.3); color: #ff6b6b; }
.volatility-high { background: rgba(255,152,0,0.3); color: #ff9800; }
.volatility-medium { background: rgba(33,150,243,0.3); color: #2196f3; }
.volatility-low { background: rgba(0,217,159,0.3); color: #00d99f; }
.profile-text { font-style: italic; color: #808080; font-size: 0.9em; margin-top: 5px; }
h2 { color: #00d99f; margin-bottom: 20px; font-size: 1.8em; text-shadow: 0 0 10px rgba(0,217,159,0.2); }
h3 { color: #00d99f; margin: 20px 0 15px 0; font-size: 1.2em; }
button { padding: 12px 24px; border: none; background: linear-gradient(135deg, #00d99f 0%, #00c986 100%); color: #0a0e27; border-radius: 8px; cursor: pointer; font-weight: 600; margin: 10px 0; transition: all 0.3s; }
button:hover { background: linear-gradient(135deg, #00c986 0%, #00b872 100%); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,217,159,0.3); }
input, select { width: 100%; padding: 10px; margin: 5px 0 15px 0; border: 2px solid #3d4571; border-radius: 8px; font-size: 0.95em; background: #252d48; color: #e0e0e0; }
input:focus, select:focus { outline: none; border-color: #00d99f; box-shadow: 0 0 0 3px rgba(0,217,159,0.2); }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
.form-group { }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #e0e0e0; }
.alert { padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid; }
.alert-success { background: rgba(0,217,159,0.2); border-left-color: #00d99f; color: #00d99f; }
.alert-error { background: rgba(255,107,107,0.2); border-left-color: #ff6b6b; color: #ff6b6b; }
.alert-info { background: rgba(33,150,243,0.2); border-left-color: #2196f3; color: #2196f3; }
.market-card { background: #252d48; padding: 18px; border-radius: 10px; border-left: 4px solid #00d99f; text-align: center; }
.market-symbol { font-weight: bold; color: #e0e0e0; font-size: 1.1em; margin-bottom: 8px; }
.market-price { font-size: 1.6em; font-weight: bold; color: #00d99f; }
.market-change { font-size: 0.9em; margin-top: 8px; padding: 8px; border-radius: 5px; }
.market-change.positive { background: rgba(0,217,159,0.2); color: #00d99f; }
.market-change.negative { background: rgba(255,107,107,0.2); color: #ff6b6b; }
footer { text-align: center; color: #808080; margin-top: 30px; font-size: 0.9em; }
ul { margin-left: 20px; line-height: 2; color: #e0e0e0; }
.loader { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(0,217,159,0.3); border-radius: 50%; border-top-color: #00d99f; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body style="background: #0f1419;">
<div style="display: flex; height: 100vh; overflow: hidden;">

<!-- Header Top -->
<div style="position: fixed; top: 0; left: 0; right: 0; height: 60px; background: linear-gradient(to right, #1a1a2e 0%, #16213e 100%); border-bottom: 1px solid #2d3561; z-index: 1000; padding: 0 30px; display: flex; align-items: center; justify-content: space-between;">
  <div style="display: flex; align-items: center; gap: 20px;">
    <h1 style="color: #00d99f; font-size: 1.4em; margin: 0; text-shadow: 0 0 10px rgba(0,217,159,0.3);">INSTITUTIONAL BOT</h1>
    <div style="display: flex; gap: 10px; font-size: 0.85em;">
      <span style="color: #00d99f; font-weight: 600;">🟢 SYSTEM: ACTIVE</span>
      <span style="color: #00d99f; font-weight: 600;">📊 SESSION: RTH</span>
      <span style="color: #ffb700; font-weight: 600;">📈 MACRO: NEUTRAL</span>
      <span style="color: #a0a0a0;">📅 CALENDAR: CLEAR</span>
    </div>
  </div>
  <div style="display: flex; gap: 15px; align-items: center;">
    <button style="background: #1e5f9e; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">NO 15M</button>
    <div style="display: flex; gap: 8px; color: #a0a0a0;">
      <span style="cursor: pointer; font-size: 1.2em;">⚙️</span>
      <span style="cursor: pointer; font-size: 1.2em;">🔔</span>
      <span style="cursor: pointer; font-size: 1.2em;">⚡</span>
    </div>
  </div>
</div>

<!-- Main Content -->
<div style="margin-top: 60px; width: 100%; padding: 20px; overflow-y: auto; background: linear-gradient(135deg, #0a0e27 0%, #0f1419 100%);">

<!-- Row 1: Market Structure -->
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">

<!-- Market Structure Card -->
<div style="background: #1a1a2e; border: 1px solid #2d3561; border-radius: 10px; padding: 20px;">
  <div style="color: #a0a0a0; font-size: 0.9em; text-transform: uppercase; margin-bottom: 10px; font-weight: 600;">📊 Market Structure</div>
  <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
    <span style="color: #00d99f; font-size: 0.85em; background: rgba(0,217,159,0.2); padding: 5px 10px; border-radius: 4px;">COMPRESSION</span>
    <div style="color: #00d99f; font-weight: 700; font-size: 1.2em;">YES</div>
  </div>
  <div style="height: 150px; background: #252d48; border-radius: 8px; display: flex; align-items: flex-end; justify-content: space-around; padding: 10px;">
    <div style="width: 25px; height: 40px; background: #00d99f; border-radius: 4px;"></div>
    <div style="width: 25px; height: 80px; background: #00d99f; border-radius: 4px;"></div>
    <div style="width: 25px; height: 60px; background: #00d99f; border-radius: 4px;"></div>
    <div style="width: 25px; height: 100px; background: #00d99f; border-radius: 4px;"></div>
    <div style="width: 25px; height: 45px; background: #00d99f; border-radius: 4px;"></div>
  </div>
  <div style="color: #606060; font-size: 0.8em; margin-top: 10px;">17190 • 17290 RANGE BOX</div>
</div>

<!-- Risk & Discipline Card -->
<div style="background: #1a1a2e; border: 1px solid #2d3561; border-radius: 10px; padding: 20px;">
  <div style="color: #a0a0a0; font-size: 0.9em; text-transform: uppercase; margin-bottom: 15px; font-weight: 600;">🛡️ Risk & Discipline</div>
  <div style="margin-bottom: 15px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
      <span style="color: #a0a0a0; font-size: 0.9em;">ACTIVE RISK</span>
      <span style="color: #00d99f; font-weight: 700;">0.75%</span>
    </div>
    <div style="height: 8px; background: #252d48; border-radius: 4px; overflow: hidden;">
      <div style="width: 25%; height: 100%; background: linear-gradient(90deg, #00d99f, #00c986);"></div>
    </div>
  </div>
  <div style="margin-bottom: 15px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
      <span style="color: #a0a0a0; font-size: 0.9em;">DAILY DRAWDOWN</span>
      <span style="color: #a0a0a0;">0.5% / 2.5% MAX</span>
    </div>
    <div style="height: 8px; background: #252d48; border-radius: 4px; overflow: hidden;">
      <div style="width: 20%; height: 100%; background: linear-gradient(90deg, #00d99f, #00c986);"></div>
    </div>
  </div>
  <div style="margin-bottom: 15px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
      <span style="color: #a0a0a0; font-size: 0.9em;">TRADE COUNT</span>
      <span style="color: #a0a0a0;">1 OF 2 ALLOWED</span>
    </div>
    <div style="height: 8px; background: #252d48; border-radius: 4px; overflow: hidden;">
      <div style="width: 50%; height: 100%; background: linear-gradient(90deg, #00d99f, #00c986);"></div>
    </div>
  </div>
  <div style="background: #252d48; padding: 10px; border-radius: 6px; margin-top: 15px;">
    <div style="color: #00d99f; font-weight: 600; display: flex; align-items: center; gap: 8px;">
      <span>🟢</span> DISCIPLINE STATUS
    </div>
    <div style="color: #a0a0a0; font-size: 0.85em; margin-top: 5px;">Operational parameters stable.</div>
  </div>
</div>

<!-- Execution State Card -->
<div style="background: #1a1a2e; border: 1px solid #2d3561; border-radius: 10px; padding: 20px;">
  <div style="color: #a0a0a0; font-size: 0.9em; text-transform: uppercase; margin-bottom: 15px; font-weight: 600;">▶️ Execution State</div>
  <div style="background: #252d48; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
    <div style="color: #a0a0a0; font-size: 0.85em; margin-bottom: 5px;">POSITION</div>
    <div style="color: #00d99f; font-weight: 700; font-size: 1.4em;">LONG</div>
  </div>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
    <div style="background: #252d48; padding: 12px; border-radius: 8px;">
      <div style="color: #a0a0a0; font-size: 0.8em; margin-bottom: 5px;">ENTRY PRICE</div>
      <div style="color: #e0e0e0; font-weight: 700;">17890.25</div>
    </div>
    <div style="background: #252d48; padding: 12px; border-radius: 8px;">
      <div style="color: #a0a0a0; font-size: 0.8em; margin-bottom: 5px;">STOPLOSS</div>
      <div style="color: #ff6b6b; font-weight: 700;">17875.00</div>
    </div>
  </div>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
    <div style="background: #252d48; padding: 12px; border-radius: 8px;">
      <div style="color: #a0a0a0; font-size: 0.8em; margin-bottom: 5px;">TAKEPROFIT</div>
      <div style="color: #00d99f; font-weight: 700;">17935.60</div>
    </div>
    <div style="background: #252d48; padding: 12px; border-radius: 8px;">
      <div style="color: #a0a0a0; font-size: 0.8em; margin-bottom: 5px;">RISK RATIO</div>
      <div style="color: #e0e0e0; font-weight: 700;">3R</div>
    </div>
  </div>
  <div style="margin-top: 10px; padding: 10px; background: #252d48; border-radius: 6px;">
    <div style="display: flex; justify-content: space-between;">
      <span style="color: #a0a0a0; font-size: 0.85em;">DURATION</span>
      <span style="color: #e0e0e0; font-weight: 600;">08:42:15</span>
    </div>
  </div>
</div>

</div>

<!-- Row 2: Performance Tracking -->
<div style="background: #1a1a2e; border: 1px solid #2d3561; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
  <div style="margin-bottom: 20px;">
    <div style="font-size: 1.2em; color: #a0a0a0; text-transform: uppercase; margin-bottom: 10px; font-weight: 600;">📈 Performance Tracking</div>
    <div style="display: flex; align-items: baseline; gap: 15px;">
      <div style="font-size: 2.5em; font-weight: 700; color: #e0e0e0;">$124,500.00</div>
      <div style="color: #00d99f; font-weight: 600; font-size: 1.1em;">+4.2% MTO PERFORMANCE</div>
    </div>
  </div>
  
  <!-- Chart Placeholder -->
  <div style="height: 300px; background: linear-gradient(to right, #252d48, #1a2535); border-radius: 8px; position: relative; overflow: hidden;">
    <svg style="width: 100%; height: 100%;" viewBox="0 0 800 300">
      <polyline points="0,200 50,180 100,150 150,160 200,140 250,120 300,100 350,110 400,90 450,70 500,80 550,60 600,50 650,40 700,30 750,20 800,10" 
                  fill="none" stroke="#00d99f" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <polyline points="0,200 50,180 100,150 150,160 200,140 250,120 300,100 350,110 400,90 450,70 500,80 550,60 600,50 650,40 700,30 750,20 800,10" 
                  fill="url(#gradient)" opacity="0.2"/>
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#00d99f;stop-opacity:0.3" />
          <stop offset="100%" style="stop-color:#00d99f;stop-opacity:0" />
        </linearGradient>
      </defs>
    </svg>
    <div style="position: absolute; bottom: 20px; left: 20px; right: 20px; display: flex; gap: 20px; justify-content: flex-end;">
      <button style="background: #1e5f9e; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; font-weight: 600;">1D</button>
      <button style="background: #1e5f9e; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; font-weight: 600;">1W</button>
      <button style="background: #1e5f9e; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; font-weight: 600;">1M</button>
      <button style="background: #1e5f9e; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; font-weight: 600;">ALL</button>
    </div>
  </div>
</div>

<!-- Bottom Status Bar -->
<div style="background: #1a1a2e; border-top: 1px solid #2d3561; padding: 15px 30px; font-size: 0.85em; color: #606060; display: flex; justify-content: space-between;">
  <div>⏱️ LATENCY: 4MS • ⬆️ UPTIME: 99.98% • 📦 VERSION: 4.2.0 STABLE</div>
  <div>🟢 HARDWARE ENCRYPTED TUNNEL ACTIVE</div>
</div>

</div>

</div>

<script>
window.addEventListener('load', function() {
  console.log('Dashboard loaded');
});
</script>

</body>
</html>'''

def require_rate_limit(f):
    def wrapper(*args, **kwargs):
        allowed, count = check_rate_limit()
        if not allowed:
            status = get_rate_limit_status()
            return jsonify({"error": "Rate limit exceeded", "message": f"Maximum {RATE_LIMIT_MAX} requests per day reached"}), 429
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/api/conf')
@require_rate_limit
def conf():
    return jsonify(load_editable_config())

@app.route('/api/save-config', methods=['POST'])
@require_rate_limit
def save_config():
    try:
        config_data = request.json
        if save_editable_config(config_data):
            return jsonify({"success": True, "message": "Configuration saved"})
        else:
            return jsonify({"success": False, "message": "Failed to save configuration"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/test')
@require_rate_limit
def test():
    try:
        init_bot()
        return jsonify({"success": True, "msg": "System Ready"})
    except Exception as e:
        return jsonify({"success": False, "err": str(e)})

@app.route('/api/evolve', methods=['POST'])
@require_rate_limit
def evolve():
    try:
        init_bot()
        d = request.json
        
        # Get evolution parameters from request
        instrument = d.get('inst', 'NQ')
        start_date = d.get('st', '2024-01-01')
        end_date = d.get('ed', '2024-06-30')
        generations = d.get('gens', 1000)
        population_size = d.get('pop', 50)
        mutation_rate = d.get('mut', 0.1)
        
        # Run evolutionary backtest
        result = bot.evolve_backtest(
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            generations=generations,
            population_size=population_size,
            mutation_rate=mutation_rate
        )
        
        return jsonify({"ok": True, "res": result})
    except Exception as e:
        return jsonify({"ok": False, "err": str(e)}), 500

@app.route('/api/news')
@require_rate_limit
def news():
    return jsonify({"news": get_sp500_news()})

@app.route('/api/sp500-news')
@require_rate_limit
def sp500_news():
    return jsonify({"news": get_sp500_news()})

@app.route('/api/market-overview')
@require_rate_limit
def market_overview():
    return jsonify({"overview": get_market_overview()})

@app.route('/api/x-news')
@require_rate_limit
def x_news():
    return jsonify({"tweets": get_x_news()})

@app.route('/api/holdings')
@require_rate_limit
def get_holdings_api():
    return jsonify({"holdings": load_holdings()})

@app.route('/api/holdings-news')
@require_rate_limit
def get_holdings_news_api():
    return jsonify({"news": get_holdings_news()})

@app.route('/backtest')
def backtest_ui():
    """Serve the backtesting UI"""
    return render_template('backtest.html')

@app.route('/api/backtest/run', methods=['POST'])
@require_rate_limit
def backtest_run():
    """Run a backtest with the specified parameters"""
    try:
        init_bot()
        d = request.json
        s = bot.backtest(d['inst'], d['st'], d['ed'])
        return jsonify({"ok": True, "res": {k: str(round(v, 2) if isinstance(v, float) else v) for k, v in s.items()}})
    except Exception as e:
        return jsonify({"ok": False, "err": str(e)})

@app.route('/api/holdings', methods=['POST'])
@require_rate_limit
def update_holdings():
    try:
        holdings = request.json
        if save_holdings(holdings):
            return jsonify({"success": True, "message": "Holdings saved"})
        else:
            return jsonify({"success": False, "message": "Failed to save holdings"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/market-trend')
@require_rate_limit
def market_trend():
    return jsonify(get_market_trend())

@app.route('/api/yahoo-news')
@require_rate_limit
def yahoo_news():
    return jsonify({"news": get_yahoo_finance_news()})

@app.route('/api/predictions')
@require_rate_limit
def predictions():
    return jsonify({"predictions": get_predictions()})

@app.route('/api/rate-limit')
def rate_limit_status():
    return jsonify(get_rate_limit_status())

@app.route('/api/evolve-params')
@require_rate_limit
def evolve_params():
    try:
        init_bot()
        # Return the evolution parameters that can be used for optimization
        params = {
            'rsi_period': [5, 10, 15, 20, 25, 30],
            'ema_fast': [5, 10, 15, 20, 25, 30],
            'ema_slow': [20, 30, 50, 70, 100, 150],
            'stop_loss_pct': [0.005, 0.01, 0.015, 0.02, 0.025, 0.03],
            'take_profit_pct': [1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
            'position_size': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
        }
        return jsonify({"ok": True, "params": params})
    except Exception as e:
        return jsonify({"ok": False, "err": str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """
    API endpoint for running backtests.
    
    Returns:
        JSON response with backtest results or error
    """
    try:
        # Check rate limit
        allowed, count = check_rate_limit()
        if not allowed:
            return jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded',
                'rate_limit': get_rate_limit_status()
            }), 429
        
        data = request.get_json()
        instrument = data.get('instrument', 'NQ')
        start_date = data.get('start_date', '2023-01-01')
        end_date = data.get('end_date', '2023-12-31')
        
        logger.info(f"API backtest requested for {instrument} from {start_date} to {end_date}")
        
        # Initialize bot if needed
        if not bot:
            init_bot()
            
        # Run backtest
        result = bot.run_backtest(instrument, start_date, end_date)
        
        # Return JSON response
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in API backtest: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Backtest failed due to an error',
            'error': str(e)
        }), 500

@app.route('/api/market-sentiment')
@require_rate_limit
def market_sentiment():
    try:
        init_bot()
        # Get current market sentiment from our enhanced analyzer
        sentiment = get_market_sentiment()
        return jsonify({"ok": True, "sentiment": sentiment})
    except Exception as e:
        return jsonify({"ok": False, "err": str(e)}), 500

if __name__ == '__main__':
    print("🤖 FTMO Bot Interface | http://127.0.0.1:5001")
    app.run(host='127.0.0.1', port=5001, debug=False)
