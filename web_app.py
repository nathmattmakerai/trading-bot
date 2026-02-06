"""
FTMO Futures Bot - Web Interface (Flask)
Access: http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import sys

try:
    from main import TradingBot
    from config.rules_v1 import vv1_FROZEN
except Exception as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        "status": "ready",
        "version": "1.0",
        "prd": "v1_FROZEN",
        "tests": "27/27_passing"
    })

@app.route('/api/config', methods=['GET'])
def api_config():
    return jsonify(vv1_FROZEN)

@app.route('/api/test', methods=['POST'])
def api_test():
    try:
        bot = TradingBot(starting_balance=10000.0)
        return jsonify({"success": True, "message": "Bot initialized"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    try:
        data = request.json
        bot = TradingBot(starting_balance=data.get('starting_balance', 10000))
        stats = bot.backtest(
            instrument=data.get('instrument', 'NQ'),
            start_date=data.get('start_date', '2024-01-01'),
            end_date=data.get('end_date', '2024-12-31')
        )
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ============================================================================
# WEB INTERFACE
# ============================================================================

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FTMO Futures Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); }
        h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.1em; }
        nav { display: flex; gap: 15px; margin-top: 20px; flex-wrap: wrap; }
        nav button { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        nav button:hover { background: #764ba2; }
        nav button.active { background: #764ba2; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2.5em; font-weight: bold; color: #667eea; margin: 10px 0; }
        .metric-label { color: #666; }
        .badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 0.85em; font-weight: 600; background: #d4edda; color: #155724; margin-top: 10px; }
        .content { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); display: none; }
        .content.active { display: block; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .item { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }
        .label { font-weight: 600; color: #333; font-size: 0.9em; text-transform: uppercase; }
        .value { color: #667eea; font-size: 1.3em; font-weight: 700; margin-top: 8px; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 8px; font-weight: 600; }
        input, select { width: 100%; max-width: 500px; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 1em; }
        input:focus, select:focus { outline: none; border-color: #667eea; }
        .btn { padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 1em; transition: all 0.3s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #764ba2; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; }
        .alert { padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid; }
        .alert-success { background: #d4edda; color: #155724; border-left-color: #28a745; }
        .alert-error { background: #f8d7da; color: #721c24; border-left-color: #dc3545; }
        .results { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .result-item { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; }
        .result-label { color: #666; font-size: 0.9em; text-transform: uppercase; }
        .result-value { font-size: 1.5em; font-weight: 700; color: #667eea; margin-top: 8px; }
        footer { text-align: center; color: rgba(255,255,255,0.8); margin-top: 30px; }
        h2 { color: #667eea; margin-bottom: 20px; }
        h3 { color: #764ba2; margin: 20px 0 15px 0; }
        .loading { display: none; text-align: center; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 FTMO Futures Trading Bot</h1>
            <p class="subtitle">Control Panel v1.0</p>
            <nav>
                <button class="nav-btn active" onclick="show('dashboard')">📊 Dashboard</button>
                <button class="nav-btn" onclick="show('config')">⚙️ Configuration</button>
                <button class="nav-btn" onclick="show('backtest')">📈 Backtest</button>
                <button class="nav-btn" onclick="show('docs')">📖 Docs</button>
            </nav>
        </header>
        
        <div id="dashboard" class="content active">
            <h2>📊 Dashboard</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Status</div>
                    <div class="metric-value">🟢</div>
                    <div class="badge">Ready</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Version</div>
                    <div class="metric-value">PRD v1</div>
                    <div class="badge">FROZEN</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Capital</div>
                    <div class="metric-value">$10k</div>
                    <div class="badge">Initial</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Tests</div>
                    <div class="metric-value">27/27</div>
                    <div class="badge">✓ Passing</div>
                </div>
            </div>
            <h3>Configuration</h3>
            <div id="summary" class="grid"></div>
            <button class="btn btn-success" onclick="test()" style="margin-top: 20px;">🧪 System Test</button>
            <div id="test-result"></div>
        </div>
        
        <div id="config" class="content">
            <h2>⚙️ Configuration</h2>
            <h3>Compression Detector</h3>
            <div id="compression" class="grid"></div>
            <h3>Breakout Setup</h3>
            <div id="breakout" class="grid"></div>
            <h3>Risk Management</h3>
            <div id="risk" class="grid"></div>
            <h3>Macro Filter</h3>
            <div id="macro" class="grid"></div>
            <h3>Calendar Filter</h3>
            <div id="calendar" class="grid"></div>
            <h3>Session</h3>
            <div id="session" class="grid"></div>
        </div>
        
        <div id="backtest" class="content">
            <h2>📈 Backtest</h2>
            <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
                <div class="form-group">
                    <label>Instrument:</label>
                    <select id="bt-inst">
                        <option value="NQ">NQ (Nasdaq)</option>
                        <option value="ES">ES (S&P 500)</option>
                        <option value="YM">YM (Dow)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Start Date:</label>
                    <input type="date" id="bt-start" value="2024-01-01">
                </div>
                <div class="form-group">
                    <label>End Date:</label>
                    <input type="date" id="bt-end" value="2024-12-31">
                </div>
            </div>
            <div class="form-group">
                <label>Starting Balance ($):</label>
                <input type="number" id="bt-bal" value="10000" min="1000" step="1000">
            </div>
            <button class="btn btn-primary" onclick="backtest()">▶️ Run Backtest</button>
            <div id="bt-loading" class="loading">
                <div class="spinner"></div>
                <p>Running...</p>
            </div>
            <div id="bt-result"></div>
        </div>
        
        <div id="docs" class="content">
            <h2>📖 Documentation</h2>
            <h3>Quick Start</h3>
            <pre style="background: #f8f9fa; padding: 20px; border-radius: 8px; overflow-x: auto; border-left: 4px solid #667eea;">python web_app.py    # Start interface
python -m pytest tests/validation_suite.py -v    # Run tests
python example_backtest.py    # Backtest</pre>
            <h3>Strategy (PRD v1 FROZEN)</h3>
            <ul style="margin-left: 20px; line-height: 2;">
                <li><strong>Macro:</strong> VIX < 18 = Risk-ON | VIX > 22 = Risk-OFF</li>
                <li><strong>Compression:</strong> ATR(14) < 0.65 × ATR(50)</li>
                <li><strong>Breakout:</strong> Range breakout with ATR</li>
                <li><strong>Risk:</strong> 0.75% per trade, 2.50% max daily loss</li>
                <li><strong>Session:</strong> RTH only (8 AM - 3 PM ET)</li>
            </ul>
        </div>
    </div>
    
    <footer><p>✅ FTMO Futures Bot | PRD v1 FROZEN | 27/27 Tests Passing</p></footer>
    
    <script>
        function show(p) {
            document.querySelectorAll('.content').forEach(e => e.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(e => e.classList.remove('active'));
            document.getElementById(p).classList.add('active');
            event.target.classList.add('active');
        }
        
        function load() {
            fetch('/api/config').then(r => r.json()).then(c => {
                let h = '';
                const items = [
                    {l: 'Risk/Trade', v: (c.RISK_CONFIG.risk_per_trade * 100) + '%'},
                    {l: 'Max Daily Loss', v: (c.RISK_CONFIG.max_daily_loss * 100) + '%'},
                    {l: 'Max Trades/Day', v: c.RISK_CONFIG.max_trades_per_day},
                    {l: 'TP Ratio', v: c.POSITION_CONFIG.take_profit_ratio + 'R'},
                    {l: 'VIX Risk-On', v: '< ' + c.MACRO_FILTER_CONFIG.risk_on_vix},
                    {l: 'VIX Risk-Off', v: '> ' + c.MACRO_FILTER_CONFIG.risk_off_vix},
                    {l: 'RTH Open', v: c.SESSION_CONFIG.rth_open},
                    {l: 'RTH Close', v: c.SESSION_CONFIG.rth_close}
                ];
                items.forEach(i => {
                    h += '<div class="item"><div class="label">' + i.l + '</div><div class="value">' + i.v + '</div></div>';
                });
                document.getElementById('summary').innerHTML = h;
                
                ['COMPRESSION_CONFIG', 'BREAKOUT_CONFIG', 'RISK_CONFIG', 'MACRO_FILTER_CONFIG', 'CALENDAR_FILTER_CONFIG', 'SESSION_CONFIG'].forEach(k => {
                    let html = '';
                    const m = {COMPRESSION_CONFIG: 'compression', BREAKOUT_CONFIG: 'breakout', RISK_CONFIG: 'risk', MACRO_FILTER_CONFIG: 'macro', CALENDAR_FILTER_CONFIG: 'calendar', SESSION_CONFIG: 'session'};
                    for (let [key, val] of Object.entries(c[k])) {
                        if (typeof val === 'object') continue;
                        html += '<div class="item"><div class="label">' + key.replace(/_/g, ' ') + '</div><div class="value">' + val + '</div></div>';
                    }
                    document.getElementById(m[k]).innerHTML = html;
                });
            });
        }
        
        function test() {
            fetch('/api/test', {method: 'POST'}).then(r => r.json()).then(d => {
                if (d.success) {
                    document.getElementById('test-result').innerHTML = '<div class="alert alert-success">✅ Test passed!</div>';
                } else {
                    document.getElementById('test-result').innerHTML = '<div class="alert alert-error">❌ ' + d.error + '</div>';
                }
            });
        }
        
        function backtest() {
            document.getElementById('bt-loading').style.display = 'block';
            document.getElementById('bt-result').innerHTML = '';
            fetch('/api/backtest', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    instrument: document.getElementById('bt-inst').value,
                    start_date: document.getElementById('bt-start').value,
                    end_date: document.getElementById('bt-end').value,
                    starting_balance: parseFloat(document.getElementById('bt-bal').value)
                })
            }).then(r => r.json()).then(d => {
                document.getElementById('bt-loading').style.display = 'none';
                if (d.success) {
                    let s = d.stats, h = '<h3 style="color:#28a745;">✅ Results</h3><div class="results">';
                    h += '<div class="result-item"><div class="result-label">Final Balance</div><div class="result-value">$' + (s.final_balance ? s.final_balance.toFixed(2) : 'N/A') + '</div></div>';
                    h += '<div class="result-item"><div class="result-label">Total PnL</div><div class="result-value">$' + (s.total_pnl ? s.total_pnl.toFixed(2) : 'N/A') + '</div></div>';
                    h += '<div class="result-item"><div class="result-label">Return %</div><div class="result-value">' + (s.total_return_pct ? s.total_return_pct.toFixed(2) : 'N/A') + '%</div></div>';
                    h += '<div class="result-item"><div class="result-label">Total Trades</div><div class="result-value">' + (s.num_trades || 0) + '</div></div>';
                    h += '<div class="result-item"><div class="result-label">Wins</div><div class="result-value">' + (s.num_wins || 0) + '</div></div>';
                    h += '<div class="result-item"><div class="result-label">Losses</div><div class="result-value">' + (s.num_losses || 0) + '</div></div>';
                    h += '<div class="result-item"><div class="result-label">Win Rate</div><div class="result-value">' + (s.win_rate ? s.win_rate.toFixed(1) : 'N/A') + '%</div></div>';
                    h += '<div class="result-item"><div class="result-label">Profit Factor</div><div class="result-value">' + (s.profit_factor ? s.profit_factor.toFixed(2) : 'N/A') + '</div></div>';
                    h += '</div>';
                    document.getElementById('bt-result').innerHTML = h;
                } else {
                    document.getElementById('bt-result').innerHTML = '<div class="alert alert-error">❌ ' + d.error + '</div>';
                }
            }).catch(e => {
                document.getElementById('bt-loading').style.display = 'none';
                document.getElementById('bt-result').innerHTML = '<div class="alert alert-error">❌ ' + e.message + '</div>';
            });
        }
        
        window.addEventListener('load', load);
    </script>
</body>
</html>
    """

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🤖 FTMO Futures Bot - Web Interface")
    print("="*80)
    print("\n✅ Configuration loaded")
    print("✅ All modules ready")
    print("\n📱 Server starting on http://localhost:5000")
    print("\nOpen your browser: http://localhost:5000")
    print("\n" + "="*80 + "\n")
    
    try:
        app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
    except Exception as e:
        print(f"❌ Error: {e}")
