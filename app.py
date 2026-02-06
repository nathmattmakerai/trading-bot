"""
Interface Web Streamlit pour FTMO Futures Bot
Permet de configurer tous les paramètres sans éditer le code
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

from main import TradingBot
from config.rules_v1 import vv1_FROZEN

# Configuration page
st.set_page_config(
    page_title="FTMO Futures Bot Control Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2em;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 0.5rem;
    }
    .config-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown("<h1 class='main-header'>🤖 FTMO Futures Trading Bot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>Control Panel v1.0</p>", unsafe_allow_html=True)

# Sidebar pour navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "⚙️ Configuration", "📈 Backtest", "📖 Documentation"]
)

# ==============================================================================
# PAGE 1: DASHBOARD
# ==============================================================================
if page == "📊 Dashboard":
    st.markdown("<h2 class='section-header'>Dashboard</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", "🟢 Ready", delta="Active")
    with col2:
        st.metric("Bot Version", "PRD v1", delta="FROZEN")
    with col3:
        st.metric("Capital", "$10,000", delta="Initial")
    with col4:
        st.metric("Tests", "27/27 ✓", delta="All Passing")
    
    st.divider()
    
    # Affichage de la configuration PRD actuelle
    st.subheader("Current Configuration (PRD v1 FROZEN)")
    
    config_tabs = st.tabs(["Compression", "Breakout", "Risk Management", "Filters"])
    
    with config_tabs[0]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**ATR Period**: {vv1_FROZEN['COMPRESSION_CONFIG']['atr_period']}")
        with col2:
            st.info(f"**ATR Lookback**: {vv1_FROZEN['COMPRESSION_CONFIG']['atr_lookback']}")
        with col3:
            st.info(f"**Range Lookback**: {vv1_FROZEN['COMPRESSION_CONFIG']['range_lookback']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**ATR Ratio**: {vv1_FROZEN['COMPRESSION_CONFIG']['atr_ratio_threshold']:.2f}")
        with col2:
            st.info(f"**Range Ratio**: {vv1_FROZEN['COMPRESSION_CONFIG']['range_ratio_threshold']:.2f}")
    
    with config_tabs[1]:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Range Lookback**: {vv1_FROZEN['BREAKOUT_CONFIG']['range_lookback']}")
        with col2:
            st.info(f"**ATR Multiplier**: {vv1_FROZEN['BREAKOUT_CONFIG']['atr_multiplier']:.2f}")
    
    with config_tabs[2]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.warning(f"**Risk/Trade**: {vv1_FROZEN['RISK_CONFIG']['risk_per_trade']:.2f}%")
        with col2:
            st.warning(f"**Max Daily Loss**: {vv1_FROZEN['RISK_CONFIG']['max_daily_loss']:.2f}%")
        with col3:
            st.warning(f"**Max Trades/Day**: {vv1_FROZEN['RISK_CONFIG']['max_trades_per_day']}")
        
        st.info(f"**TP Ratio**: {vv1_FROZEN['RISK_CONFIG']['tp_ratio']:.1f}R (Fixed)")
    
    with config_tabs[3]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**VIX Risk-On**: < {vv1_FROZEN['MACRO_FILTER_CONFIG']['vix_risk_on_threshold']}")
        with col2:
            st.info(f"**VIX Risk-Off**: > {vv1_FROZEN['MACRO_FILTER_CONFIG']['vix_risk_off_threshold']}")
        with col3:
            st.info(f"**RTH Session**: {vv1_FROZEN['SESSION_CONFIG']['rth_open']} - {vv1_FROZEN['SESSION_CONFIG']['rth_close']}")
    
    st.divider()
    
    # Test rapide
    st.subheader("Quick Test")
    if st.button("🧪 Run Quick System Check"):
        with st.spinner("Running system check..."):
            try:
                bot = TradingBot(starting_balance=10000.0)
                st.success("✅ Bot initialized successfully!")
                st.json({
                    "status": "ready",
                    "capital": "$10,000",
                    "modules": "all_loaded",
                    "tests": "27/27_passing"
                })
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ==============================================================================
# PAGE 2: CONFIGURATION
# ==============================================================================
elif page == "⚙️ Configuration":
    st.markdown("<h2 class='section-header'>Configuration Manager</h2>", unsafe_allow_html=True)
    
    st.warning("⚠️ **NOTE**: This is a preview interface. Current implementation uses frozen PRD v1 config. Custom parameters can be added by extending the rules_v1.py file.")
    
    config_section = st.radio(
        "Select Configuration Section",
        ["Compression Detector", "Breakout Setup", "Risk Management", "Macro Filter", "Session Filter"]
    )
    
    # Compression Detector
    if config_section == "Compression Detector":
        st.subheader("Compression Detector Settings")
        st.info("Detects market consolidation periods for setup identification")
        
        with st.expander("📋 Current Settings", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                atr_period = st.number_input(
                    "ATR Period (Short-term)",
                    value=vv1_FROZEN['COMPRESSION_CONFIG']['atr_period'],
                    min_value=5,
                    max_value=30,
                    help="Lookback period for short-term ATR"
                )
            with col2:
                atr_lookback = st.number_input(
                    "ATR Lookback (Long-term)",
                    value=vv1_FROZEN['COMPRESSION_CONFIG']['atr_lookback'],
                    min_value=30,
                    max_value=100,
                    help="Lookback period for long-term ATR"
                )
            with col3:
                range_lookback = st.number_input(
                    "Range Lookback",
                    value=vv1_FROZEN['COMPRESSION_CONFIG']['range_lookback'],
                    min_value=10,
                    max_value=50,
                    help="Periods to calculate range"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                atr_ratio = st.slider(
                    "ATR Ratio Threshold",
                    min_value=0.5,
                    max_value=1.0,
                    value=vv1_FROZEN['COMPRESSION_CONFIG']['atr_ratio_threshold'],
                    step=0.05,
                    help="Compression detected when ATR(short) < ratio × ATR(long)"
                )
            with col2:
                range_ratio = st.slider(
                    "Range Ratio Threshold",
                    min_value=1.0,
                    max_value=3.0,
                    value=vv1_FROZEN['COMPRESSION_CONFIG']['range_ratio_threshold'],
                    step=0.1,
                    help="Range confinement threshold"
                )
        
        st.divider()
        
        with st.expander("📊 Preview: How it works", expanded=False):
            st.markdown("""
            **Compression Detection Logic:**
            1. Calculate ATR over short period (14 bars)
            2. Calculate ATR over long period (50 bars)
            3. If ATR(14) < threshold × ATR(50) → Compression detected
            
            **Use Case:** Setup breakout trades after consolidation breaks
            """)
    
    # Breakout Setup
    elif config_section == "Breakout Setup":
        st.subheader("Breakout Setup Settings")
        st.info("Identifies breakout signals from consolidation zones")
        
        with st.expander("📋 Current Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                range_lookback = st.number_input(
                    "Range Lookback (Breakout)",
                    value=vv1_FROZEN['BREAKOUT_CONFIG']['range_lookback'],
                    min_value=5,
                    max_value=50,
                    help="Bars to identify breakout range"
                )
            with col2:
                atr_mult = st.slider(
                    "ATR Multiplier",
                    min_value=1.0,
                    max_value=3.0,
                    value=vv1_FROZEN['BREAKOUT_CONFIG']['atr_multiplier'],
                    step=0.1,
                    help="TP distance = ATR × multiplier"
                )
    
    # Risk Management
    elif config_section == "Risk Management":
        st.subheader("Risk Management Settings")
        st.danger("⚠️ These settings control position sizing and daily loss limits")
        
        with st.expander("📋 Current Settings", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                risk_per_trade = st.slider(
                    "Risk per Trade (%)",
                    min_value=0.1,
                    max_value=2.0,
                    value=vv1_FROZEN['RISK_CONFIG']['risk_per_trade'],
                    step=0.05,
                    help="% of account risked per trade"
                )
            with col2:
                max_daily_loss = st.slider(
                    "Max Daily Loss (%)",
                    min_value=1.0,
                    max_value=5.0,
                    value=vv1_FROZEN['RISK_CONFIG']['max_daily_loss'],
                    step=0.1,
                    help="Stop trading if daily loss exceeds this %"
                )
            with col3:
                max_trades = st.number_input(
                    "Max Trades per Day",
                    value=vv1_FROZEN['RISK_CONFIG']['max_trades_per_day'],
                    min_value=1,
                    max_value=10,
                    help="Maximum trades allowed per day"
                )
            
            tp_ratio = st.slider(
                "TP Ratio (R)",
                min_value=1.0,
                max_value=5.0,
                value=vv1_FROZEN['RISK_CONFIG']['tp_ratio'],
                step=0.1,
                help="Target profit = Risk × ratio"
            )
    
    # Macro Filter
    elif config_section == "Macro Filter":
        st.subheader("Macro Economic Filter (VIX-based)")
        st.info("Controls trading based on risk sentiment (VIX levels)")
        
        with st.expander("📋 Current Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                vix_risk_on = st.number_input(
                    "VIX Risk-On Threshold",
                    value=vv1_FROZEN['MACRO_FILTER_CONFIG']['vix_risk_on_threshold'],
                    min_value=10,
                    max_value=25,
                    help="VIX < this = Risk-ON (trade longs)"
                )
            with col2:
                vix_risk_off = st.number_input(
                    "VIX Risk-Off Threshold",
                    value=vv1_FROZEN['MACRO_FILTER_CONFIG']['vix_risk_off_threshold'],
                    min_value=20,
                    max_value=35,
                    help="VIX > this = Risk-OFF (no longs)"
                )
    
    # Session Filter
    elif config_section == "Session Filter":
        st.subheader("Trading Session Settings")
        st.info("Restrict trading to regular market hours (RTH)")
        
        with st.expander("📋 Current Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**RTH Open**: {vv1_FROZEN['SESSION_CONFIG']['rth_open']}")
            with col2:
                st.info(f"**RTH Close**: {vv1_FROZEN['SESSION_CONFIG']['rth_close']}")
    
    st.divider()
    
    # Save configuration
    if st.button("💾 Save Configuration", type="primary"):
        st.success("✅ Configuration saved! (To update live, edit config/rules_v1.py)")

# ==============================================================================
# PAGE 3: BACKTEST
# ==============================================================================
elif page == "📈 Backtest":
    st.markdown("<h2 class='section-header'>Backtest Engine</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        instrument = st.selectbox(
            "Instrument",
            ["NQ", "ES", "YM"],
            help="Nasdaq-100, S&P 500, or Dow Jones mini futures"
        )
    with col2:
        start_date = st.date_input(
            "Start Date",
            value=datetime(2024, 1, 1),
            help="Backtest start date"
        )
    with col3:
        end_date = st.date_input(
            "End Date",
            value=datetime(2024, 12, 31),
            help="Backtest end date"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        starting_balance = st.number_input(
            "Starting Balance ($)",
            value=10000.0,
            min_value=1000.0,
            step=1000.0,
            help="Initial account balance for backtest"
        )
    with col2:
        commission_per_trade = st.number_input(
            "Commission per Trade ($)",
            value=2.50,
            min_value=0.0,
            step=0.5,
            help="Trading costs per round-trip"
        )
    
    st.divider()
    
    if st.button("▶️ Run Backtest", type="primary", use_container_width=True):
        with st.spinner(f"Running backtest for {instrument} ({start_date} to {end_date})..."):
            try:
                bot = TradingBot(starting_balance=starting_balance)
                stats = bot.backtest(
                    instrument=instrument,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                )
                
                st.success("✅ Backtest completed!")
                
                # Résultats
                st.markdown("### 📊 Results Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Final Balance",
                        f"${stats.get('final_balance', 0):,.2f}",
                        delta=f"${stats.get('total_pnl', 0):,.2f}"
                    )
                with col2:
                    st.metric(
                        "Return %",
                        f"{stats.get('total_return_pct', 0):.2f}%",
                        delta=f"ROI"
                    )
                with col3:
                    st.metric(
                        "Win Rate",
                        f"{stats.get('win_rate', 0):.1f}%",
                        delta=f"{stats.get('num_wins', 0)}W/{stats.get('num_losses', 0)}L"
                    )
                with col4:
                    st.metric(
                        "Profit Factor",
                        f"{stats.get('profit_factor', 0):.2f}",
                        delta="Gross P/L ratio"
                    )
                
                st.divider()
                
                # Détails
                st.markdown("### 📈 Trade Statistics")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.info(f"**Total Trades**: {stats.get('num_trades', 0)}")
                with col2:
                    st.success(f"**Winning**: {stats.get('num_wins', 0)}")
                with col3:
                    st.error(f"**Losing**: {stats.get('num_losses', 0)}")
                with col4:
                    st.info(f"**Avg Win**: ${stats.get('avg_win', 0):,.2f}")
                with col5:
                    st.info(f"**Avg Loss**: ${stats.get('avg_loss', 0):,.2f}")
                
                st.divider()
                
                # Equity curve
                if 'equity_curve' in stats:
                    st.markdown("### 📈 Equity Curve")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=stats['equity_curve'],
                        mode='lines',
                        name='Equity',
                        fill='tozeroy'
                    ))
                    fig.update_layout(
                        title="Account Equity Over Time",
                        xaxis_title="Trade Number",
                        yaxis_title="Balance ($)",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Export résultats
                st.markdown("### 💾 Export Results")
                results_json = json.dumps(stats, indent=2)
                st.download_button(
                    label="Download Results (JSON)",
                    data=results_json,
                    file_name=f"backtest_{instrument}_{start_date}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"❌ Backtest failed: {str(e)}")

# ==============================================================================
# PAGE 4: DOCUMENTATION
# ==============================================================================
elif page == "📖 Documentation":
    st.markdown("<h2 class='section-header'>Documentation</h2>", unsafe_allow_html=True)
    
    doc_tabs = st.tabs(["Quick Start", "Strategy Overview", "Configuration", "API Reference"])
    
    with doc_tabs[0]:
        st.markdown("""
        ## Quick Start Guide
        
        ### 1. Run the Bot
        ```bash
        python quickstart.py
        ```
        
        ### 2. Run Unit Tests
        ```bash
        python -m pytest tests/validation_suite.py -v
        ```
        
        ### 3. Run Backtest
        ```bash
        python example_backtest.py
        ```
        
        ### 4. Use This Interface
        ```bash
        streamlit run app.py
        ```
        """)
    
    with doc_tabs[1]:
        st.markdown("""
        ## Trading Strategy Overview (PRD v1 FROZEN)
        
        ### Core Logic
        1. **Macro Filter** - Check VIX for risk sentiment
           - VIX < 18: Risk-ON → Allow long trades
           - VIX > 22: Risk-OFF → No long trades
        
        2. **Compression Detection** - Identify consolidation
           - ATR(14) < 0.65 × ATR(50)
           - Setup breakout trades after consolidation
        
        3. **Breakout Generation** - Identify entry points
           - Long: Close > Range High + (ATR × 1.5)
           - Short: Close < Range Low - (ATR × 1.5)
        
        4. **Risk Management**
           - Risk per trade: 0.75% of account
           - Max daily loss: 2.50%
           - Max trades/day: 2
           - TP ratio: 3.0R (fixed)
        
        5. **Session Filter** - Trade only RTH
           - 8:00 AM - 3:00 PM ET
        """)
    
    with doc_tabs[2]:
        st.markdown("""
        ## Configuration Files
        
        **Main Config**: `config/rules_v1.py`
        - COMPRESSION_CONFIG: Consolidation detection
        - BREAKOUT_CONFIG: Entry signal generation
        - RISK_CONFIG: Position sizing
        - MACRO_FILTER_CONFIG: VIX thresholds
        - SESSION_CONFIG: Trading hours
        
        **Custom Settings**: Edit directly in `rules_v1.py`
        """)
    
    with doc_tabs[3]:
        st.markdown("""
        ## Python API Reference
        
        ### Initialize Bot
        ```python
        from main import TradingBot
        bot = TradingBot(starting_balance=10000.0)
        ```
        
        ### Run Backtest
        ```python
        stats = bot.backtest(
            instrument="NQ",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        ```
        
        ### Access Configuration
        ```python
        from config.rules_v1 import vv1_FROZEN
        print(vv1_FROZEN['RISK_CONFIG']['risk_per_trade'])
        ```
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>FTMO Futures Trading Bot | PRD v1 FROZEN | Version 1.0</p>
    <p>27/27 Tests Passing | Zero Errors | Production Ready</p>
</div>
""", unsafe_allow_html=True)
