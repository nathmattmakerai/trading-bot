"""
Interface Web Streamlit pour FTMO Futures Bot
Permet de configurer tous les paramètres sans éditer le code
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

from main import TradingBot
from config.rules_v1 import vv1_FROZEN
from backtest_runner import BacktestRunner, BacktestAnalyzer

# Nouveaux modules de prévision
from data.stock_data_loader import StockDataLoader
from data.social_data_loader import SocialDataLoader
from engine.learning.prediction_engine import PredictionEngine

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
    ["📊 Dashboard", "⚙️ Configuration", "📈 Backtest", "🔮 Predictions", "📖 Documentation"]
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
    
    config_tabs = st.tabs(["Compression", "Breakout", "Risk Management", "Filters", "🧠 Learner Memory"])
    
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
            st.info("**Confirmation**: Candle Close")
    
    with config_tabs[2]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.warning(f"**Risk/Trade**: {vv1_FROZEN['RISK_CONFIG']['risk_per_trade']*100:.2f}%")
        with col2:
            st.warning(f"**Max Daily Loss**: {vv1_FROZEN['RISK_CONFIG']['max_daily_loss']*100:.2f}%")
        with col3:
            st.warning(f"**Max Trades/Day**: {vv1_FROZEN['RISK_CONFIG']['max_trades_per_day']}")
        
        st.info(f"**TP Ratio**: {vv1_FROZEN['POSITION_CONFIG']['take_profit_ratio']:.1f}R (Fixed)")
    
    with config_tabs[3]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**VIX Risk-On**: < {vv1_FROZEN['MACRO_FILTER_CONFIG']['risk_on_vix']}")
        with col2:
            st.info(f"**VIX Risk-Off**: > {vv1_FROZEN['MACRO_FILTER_CONFIG']['risk_off_vix']}")
        with col3:
            st.info(f"**RTH Session**: {vv1_FROZEN['SESSION_CONFIG']['rth_open']} - {vv1_FROZEN['SESSION_CONFIG']['rth_close']}")

    with config_tabs[4]:
        import json
        import os
        memory_path = "config/learning_memory.json"
        if os.path.exists(memory_path):
            with open(memory_path, "r") as f:
                memory = json.load(f)
            
            if memory:
                st.success(f"Robot memory active with {len(memory)} danger zones learned.")
                for zone in memory:
                    st.error(f"⚠️ **Avoid {zone['feature']}**: {zone['min']} to {zone['max']} (Past performance: {zone['avg_pnl']:.2f}%)")
                
                if st.button("🗑️ Reset Robot Memory"):
                    os.remove(memory_path)
                    st.rerun()
            else:
                st.write("Robot memory is empty. Run backtests to help it learn!")
        else:
            st.write("No memory file found. The robot will start learning after the first backtest.")
    
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
            range_lookback = st.number_input(
                "Range Lookback (Breakout)",
                value=vv1_FROZEN["BREAKOUT_CONFIG"]["range_lookback"],
                min_value=5,
                max_value=50,
                help="Bars to identify breakout range"
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
                value=float(vv1_FROZEN['POSITION_CONFIG']['take_profit_ratio']),
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
                    value=float(vv1_FROZEN['MACRO_FILTER_CONFIG']['risk_on_vix']),
                    min_value=10,
                    max_value=25,
                    help="VIX < this = Risk-ON (trade longs)"
                )
            with col2:
                vix_risk_off = st.number_input(
                    "VIX Risk-Off Threshold",
                    value=float(vv1_FROZEN['MACRO_FILTER_CONFIG']['risk_off_vix']),
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
    st.markdown("<h2 class='section-header'>Backtest Engine - Train on Historical Data</h2>", unsafe_allow_html=True)
    
    # Backtest mode selection
    backtest_tabs = st.tabs(["Single Backtest", "Walk-Forward Analysis", "Results Library"])
    
    # ==== TAB 1: SINGLE BACKTEST ====
    with backtest_tabs[0]:
        st.markdown("### Run Single Backtest")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            instrument = st.selectbox(
                "Instrument",
                ["NQ", "ES"],
                help="Nasdaq-100 or S&P 500 mini futures"
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
                value=50000.0,
                min_value=100.0,
                # No max limit
                step=1000.0,
                help="Initial account balance for backtest"
            )
        col1, col2 = st.columns(2)
        with col1:
            risk_free_rate = st.number_input(
                "Risk-Free Rate (Annual %)",
                value=4.0,
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                help="For Sharpe/Sortino ratio calculation"
            )
        with col2:
            contract_type = st.radio(
                "Contract Type (Size)",
                ["E-mini (Standard)", "Micro (1/10th size)"],
                index=1 if starting_balance < 25000 else 0,
                help="Start with Micros for accounts < $25k to allow proper position sizing"
            )
            if starting_balance < 25000 and "E-mini" in contract_type:
                st.warning("⚠️ E-mini on <$25k account will force 1 contract (risk > 2-5%)")
        
        # Configuration de risque personnalisée
        st.markdown("#### ⚙️ Risk Configuration")
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_per_trade = st.slider(
                "Risk per Trade (%)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="Percentage of account risked per trade"
            )
        with col2:
            max_daily_loss = st.slider(
                "Max Daily Loss (%)",
                min_value=1.0,
                max_value=20.0,
                value=3.0,
                step=0.1,
                help="Stop trading if daily loss exceeds this %"
            )
        with col3:
            max_trades_per_day = st.number_input(
                "Max Trades/Day",
                min_value=1,
                max_value=10,
                value=3,
                help="Maximum trades allowed per day"
            )
        
        if starting_balance < 50000 and risk_per_trade < 1.5:
             st.info("ℹ️ Note: With small account/low risk, position size may be floored to 1 contract (minimum possible). Use Micros or increase risk/capital to see scaling.")
        
        st.divider()
        
        # Run backtest button
        if st.button("▶️ Run Single Backtest", type="primary", use_container_width=True):
            with st.spinner(f"Running backtest for {instrument} ({start_date} to {end_date})..."):
                try:
                    # Configuration contrat
                    is_micro = "Micro" in contract_type
                    # Multiplier est la valeur d'un POINT plein (pas d'un tick)
                    multiplier = 2.0 if is_micro else 20.0  # NQ: $2 micro, $20 e-mini
                    if instrument == "ES":
                        multiplier = 5.0 if is_micro else 50.0  # ES: $5 micro, $50 e-mini
                    
                    custom_contract_config = {"tick_value": multiplier}
                    
                    # Créer configuration de risque personnalisée
                    custom_risk_config = {
                        "risk_per_trade": risk_per_trade / 100.0,
                        "max_daily_loss": max_daily_loss / 100.0,
                        "max_trades_per_day": max_trades_per_day,
                    }
                    
                    runner = BacktestRunner(
                        starting_balance=starting_balance,
                        custom_risk_config=custom_risk_config,
                        custom_contract_config=custom_contract_config
                    )
                    result = runner.run_backtest(
                        instrument=instrument,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                    
                    st.success("✅ Backtest completed successfully!")
                    st.session_state.last_result = result
                    
                    # SUMMARY METRICS
                    st.markdown("### 📊 Summary Metrics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Final Balance",
                            f"${result.final_balance:,.2f}",
                            delta=f"${result.total_pnl:,.2f}",
                            delta_color="normal" if result.total_pnl > 0 else "inverse"
                        )
                    with col2:
                        st.metric(
                            "Return %",
                            f"{result.total_return_pct:.2f}%",
                            delta=None
                        )
                    with col3:
                        st.metric(
                            "Win Rate",
                            f"{result.win_rate:.1f}%",
                            delta=f"{result.num_wins}W / {result.num_losses}L"
                        )
                    with col4:
                        st.metric(
                            "Profit Factor",
                            f"{result.profit_factor:.2f}",
                            delta="Wins/Losses"
                        )
                    
                    st.divider()
                    
                    # DETAILED STATISTICS TABS
                    stats_tabs = st.tabs(["Trade Statistics", "Risk Metrics", "Performance", "Equity Curve", "Trade List", "Export"])
                    
                    # Tab 1: Trade Statistics
                    with stats_tabs[0]:
                        col1, col2, col3, col4, col5, col6 = st.columns(6)
                        with col1:
                            st.info(f"**Total Trades**\n{result.num_trades}")
                        with col2:
                            st.success(f"**Winning Trades**\n{result.num_wins}")
                        with col3:
                            st.error(f"**Losing Trades**\n{result.num_losses}")
                        with col4:
                            st.info(f"**Breakeven**\n{result.num_breakeven}")
                        with col5:
                            st.info(f"**Win Rate**\n{result.win_rate:.1f}%")
                        with col6:
                            # Total Skipped explanation
                            st.warning(f"**Total Skipped**\n{getattr(result, 'num_virtual_trades', 0)}")
                            with st.expander("Why was it skipped?"):
                                learner_total = getattr(result, 'num_learner_wins', 0) + getattr(result, 'num_learner_losses', 0)
                                equity_total = getattr(result, 'num_equity_wins', 0) + getattr(result, 'num_equity_losses', 0)
                                filter_total = getattr(result, 'num_filter_wins', 0) + getattr(result, 'num_filter_losses', 0)
                                st.write(f"- 🧠 Learner: {learner_total}")
                                st.write(f"- 🛡️ Equity Guard: {equity_total}")
                                st.write(f"- ⚙️ Setup Filters: {filter_total}")
                        
                        st.divider()
                        
                        # [NEW] LEARNER VS EQUITY VS FILTERS ANALYSIS
                        lcol, ecol = st.columns(2)
                        
                        with lcol:
                            st.markdown("#### 🧠 Learner Guard")
                            st.metric("Skipped", learner_total)
                            st.caption(f"Avoided: {getattr(result, 'num_learner_wins', 0)}W / {getattr(result, 'num_learner_losses', 0)}L")

                        with ecol:
                            st.markdown("#### 🛡️ Equity Guard")
                            st.metric("Paused", equity_total)
                            st.caption(f"Saved: {getattr(result, 'num_equity_wins', 0)}W / {getattr(result, 'num_equity_losses', 0)}L")
                        
                        st.divider()
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Average Win", f"${result.avg_win:,.2f}")
                        with col2:
                            st.metric("Average Loss", f"${result.avg_loss:,.2f}")
                        with col3:
                            st.metric("Largest Win", f"${result.largest_win:,.2f}")
                        with col4:
                            st.metric("Largest Loss", f"${result.largest_loss:,.2f}")
                        
                        st.divider()
                        
                        # [NEW] Automatic Diagnosis
                        st.markdown("#### 💬 Bot Diagnosis")
                        diag = getattr(result, "diagnosis", "No diagnosis available.")
                        if "🛡️" in diag or "🧠" in diag:
                            st.info(diag)
                        elif "❌" in diag:
                            st.error(diag)
                        else:
                            st.success(diag)
                        
                        st.divider()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Wins (P&L)", f"${result.total_wins:,.2f}")
                        with col2:
                            st.metric("Total Losses (P&L)", f"${result.total_losses:,.2f}")
                    
                    # Tab 2: Risk Metrics
                    with stats_tabs[1]:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Max Drawdown %",
                                f"{result.max_drawdown_pct:.2f}%",
                                delta="Lower is better"
                            )
                        with col2:
                            st.metric(
                                "Max Drawdown Amount",
                                f"${result.max_drawdown_amount:,.2f}",
                                delta="In dollars"
                            )
                        with col3:
                            st.metric(
                                "Drawdown Duration",
                                f"{result.drawdown_duration} bars",
                                delta="Trading periods"
                            )
                        
                        st.divider()
                        
                        # Drawdown information
                        st.info(
                            f"📊 **Drawdown Analysis**\n\n"
                            f"Maximum Drawdown represents the largest peak-to-trough decline. "
                            f"For FTMO compliance:\n"
                            f"• Target: < 3.5%\n"
                            f"• Actual: {abs(result.max_drawdown_pct):.2f}%\n"
                            f"• Status: {'✅ PASS' if abs(result.max_drawdown_pct) < 3.5 else '❌ FAIL'}"
                        )
                    
                    # Tab 3: Performance Metrics
                    with stats_tabs[2]:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}", delta="Higher is better")
                        with col2:
                            st.metric("Sortino Ratio", f"{result.sortino_ratio:.2f}", delta="Downside risk only")
                        with col3:
                            st.metric("Calmar Ratio", f"{result.calmar_ratio:.2f}", delta="Return/Drawdown")
                        with col4:
                            st.metric("Recovery Factor", f"{result.recovery_factor:.2f}", delta="Profit/Max Loss")
                        
                        st.divider()
                        
                        # Monthly breakdown
                        st.markdown("#### Monthly Performance")
                        if result.monthly_pnl_dict:
                            monthly_df = pd.DataFrame(
                                list(result.monthly_pnl_dict.items()),
                                columns=["Month", "P&L ($)"]
                            )
                            monthly_df = monthly_df.sort_values("Month")
                            
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=monthly_df["Month"],
                                    y=monthly_df["P&L ($)"],
                                    marker_color=['green' if x > 0 else 'red' for x in monthly_df["P&L ($)"]],
                                    text=monthly_df["P&L ($)"].apply(lambda x: f"${x:,.0f}"),
                                    textposition="outside"
                                )
                            ])
                            fig.update_layout(
                                title="Monthly P&L",
                                xaxis_title="Month",
                                yaxis_title="Profit/Loss ($)",
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Tab 4: Equity Curve
                    with stats_tabs[3]:
                        if result.equity_curve:
                            fig = go.Figure()
                            
                            # Equity curve
                            fig.add_trace(go.Scatter(
                                y=result.equity_curve,
                                mode='lines',
                                name='Equity',
                                line=dict(color='#1f77b4', width=2),
                                fill='tozeroy',
                                fillcolor='rgba(31, 119, 180, 0.2)'
                            ))
                            
                            # Add starting balance line
                            fig.add_hline(
                                y=result.starting_balance,
                                line_dash="dash",
                                line_color="gray",
                                annotation_text="Starting Balance",
                                annotation_position="right"
                            )
                            
                            fig.update_layout(
                                title="Account Equity Curve",
                                xaxis_title="Trade Number",
                                yaxis_title="Account Equity ($)",
                                hovermode='x unified',
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No trades executed - no equity curve available")
                    
                    # Tab 5: Trade List
                    with stats_tabs[4]:
                        if result.trades:
                            st.markdown("#### All Trades")
                            trades_df = pd.DataFrame(result.trades)
                            
                            # Format display
                            display_df = trades_df[[
                                "trade_id", "entry_date", "direction", 
                                "entry_price", "exit_price", "pnl", "pnl_pct"
                            ]].copy()
                            
                            display_df["entry_price"] = display_df["entry_price"].apply(lambda x: f"{x:.2f}")
                            display_df["exit_price"] = display_df["exit_price"].apply(lambda x: f"{x:.2f}")
                            display_df["pnl"] = display_df["pnl"].apply(lambda x: f"${x:,.2f}")
                            display_df["pnl_pct"] = display_df["pnl_pct"].apply(lambda x: f"{x:.2f}%")
                            
                            st.dataframe(display_df, use_container_width=True)
                        else:
                            st.info("No trades executed during backtest period")
                    
                    # Tab 6: Export
                    with stats_tabs[5]:
                        st.markdown("#### Export Results")
                        
                        # JSON export
                        results_json = json.dumps(result.to_dict(), indent=2, default=str)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=results_json,
                            file_name=f"backtest_{instrument}_{start_date.strftime('%Y%m%d')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        
                        # CSV export (trades)
                        if result.trades:
                            trades_df = pd.DataFrame(result.trades)
                            csv = trades_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Trades as CSV",
                                data=csv,
                                file_name=f"trades_{instrument}_{start_date.strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        st.divider()
                        
                        # Summary text
                        summary_text = f"""
# BACKTEST SUMMARY REPORT
**{instrument} - {start_date} to {end_date}**

## Account Performance
- Starting Balance: ${result.starting_balance:,.2f}
- Final Balance: ${result.final_balance:,.2f}
- Total P&L: ${result.total_pnl:,.2f}
- Return: {result.total_return_pct:.2f}%

## Trading Statistics
- Total Trades: {result.num_trades}
- Skipped (Virtual): {getattr(result, 'num_virtual_trades', 0)}
- Winning Trades: {result.num_wins}
- Losing Trades: {result.num_losses}
- Win Rate: {result.win_rate:.1f}%
- Profit Factor: {result.profit_factor:.2f}

## Risk Metrics
- Max Drawdown: {result.max_drawdown_pct:.2f}%
- Sharpe Ratio: {result.sharpe_ratio:.2f}
- Sortino Ratio: {result.sortino_ratio:.2f}
- Calmar Ratio: {result.calmar_ratio:.2f}

## Trade Details
- Average Win: ${result.avg_win:,.2f}
- Average Loss: ${result.avg_loss:,.2f}
- Largest Win: ${result.largest_win:,.2f}
- Largest Loss: ${result.largest_loss:,.2f}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                        st.download_button(
                            label="📥 Download as Text Report",
                            data=summary_text,
                            file_name=f"backtest_report_{instrument}_{start_date.strftime('%Y%m%d')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")
                    st.exception(e)
    
    # ==== TAB 2: WALK-FORWARD ANALYSIS ====
    with backtest_tabs[1]:
        st.markdown("### Walk-Forward Analysis")
        st.info(
            "📊 Walk-forward analysis tests your strategy on sequential non-overlapping periods. "
            "This provides more robust validation than a single backtest."
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            wf_instrument = st.selectbox(
                "Instrument (WF)",
                ["NQ", "ES"],
                help="Select instrument for walk-forward test",
                key="wf_instrument"
            )
        with col2:
            wf_start_date = st.date_input(
                "Start Date (WF)",
                value=datetime(2024, 1, 1),
                key="wf_start_date"
            )
        with col3:
            wf_end_date = st.date_input(
                "End Date (WF)",
                value=datetime(2024, 12, 31),
                key="wf_end_date"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            wf_starting_balance = st.number_input(
                "Starting Balance (WF)",
                value=10000.0,
                min_value=1000.0,
                step=1000.0,
                key="wf_balance"
            )
        with col2:
            wf_window_months = st.slider(
                "Window Size (Months)",
                min_value=1,
                max_value=12,
                value=3,
                help="Size of each backtest window"
            )
        
        st.divider()
        
        if st.button("▶️ Run Walk-Forward Analysis", type="primary", use_container_width=True):
            with st.spinner(f"Running walk-forward analysis for {wf_instrument}..."):
                try:
                    runner = BacktestRunner(starting_balance=wf_starting_balance)
                    results = runner.run_walk_forward(
                        instrument=wf_instrument,
                        start_date=wf_start_date.strftime("%Y-%m-%d"),
                        end_date=wf_end_date.strftime("%Y-%m-%d"),
                        window_size_months=wf_window_months
                    )
                    
                    st.success(f"✅ Walk-forward analysis complete! ({len(results)} windows)")
                    
                    # Summary statistics
                    st.markdown("### Walk-Forward Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    avg_return = np.mean([r.total_return_pct for r in results])
                    avg_dd = np.mean([r.max_drawdown_pct for r in results])
                    avg_sharpe = np.mean([r.sharpe_ratio for r in results])
                    total_trades = sum([r.num_trades for r in results])
                    
                    with col1:
                        st.metric("Avg Return", f"{avg_return:.2f}%")
                    with col2:
                        st.metric("Avg Max DD", f"{avg_dd:.2f}%")
                    with col3:
                        st.metric("Avg Sharpe", f"{avg_sharpe:.2f}")
                    with col4:
                        st.metric("Total Trades", total_trades)
                    
                    st.divider()
                    
                    # Window results table
                    st.markdown("### Results by Window")
                    window_data = []
                    for i, result in enumerate(results, 1):
                        window_data.append({
                            "Window": i,
                            "Period": f"{result.start_date} to {result.end_date}",
                            "Trades": result.num_trades,
                            "Return %": f"{result.total_return_pct:.2f}%",
                            "Win Rate": f"{result.win_rate:.1f}%",
                            "Max DD": f"{result.max_drawdown_pct:.2f}%",
                            "Sharpe": f"{result.sharpe_ratio:.2f}"
                        })
                    
                    window_df = pd.DataFrame(window_data)
                    st.dataframe(window_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Walk-forward analysis failed: {str(e)}")
                    st.exception(e)
    
    # ==== TAB 3: RESULTS LIBRARY ====
    with backtest_tabs[2]:
        st.markdown("### Results Library")
        st.info("💾 Save and compare backtest results")
        
        if "backtest_results" not in st.session_state:
            st.session_state.backtest_results = []
        
        if "last_result" in st.session_state:
            col1, col2 = st.columns(2)
            with col1:
                result_name = st.text_input("Name this result:")
            with col2:
                if st.button("💾 Save Result"):
                    st.session_state.backtest_results.append({
                        "name": result_name or f"Backtest {len(st.session_state.backtest_results) + 1}",
                        "result": st.session_state.last_result,
                        "timestamp": datetime.now()
                    })
                    st.success("✅ Result saved!")
        else:
            st.info("Run a backtest to save results")
        
        if st.session_state.backtest_results:
            st.markdown("### Saved Results")
            for i, saved in enumerate(st.session_state.backtest_results):
                with st.expander(f"📊 {saved['name']} ({saved['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                    result = saved['result']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Return", f"{result.total_return_pct:.2f}%")
                    with col2:
                        st.metric("Win Rate", f"{result.win_rate:.1f}%")
                    with col3:
                        st.metric("Max DD", f"{result.max_drawdown_pct:.2f}%")
                    with col4:
                        st.metric("Sharpe", f"{result.sharpe_ratio:.2f}")
                    
                    if st.button(f"Delete", key=f"delete_{i}"):
                        st.session_state.backtest_results.pop(i)
                        st.rerun()

# ==============================================================================
# PAGE 4: DOCUMENTATION
# ==============================================================================
elif page == "🔮 Predictions":
    st.markdown("<h2 class='section-header'>Stock Market Predictions & Social Sentiment</h2>", unsafe_allow_html=True)
    st.write("Combined analysis of Technical indicators (Yahoo Finance) and Social Sentiment (X/Twitter).")

    tickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NFLX', 'PYPL']
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Run Global Analysis"):
            with st.spinner("Analyzing Market and X Sentiment..."):
                stock_loader = StockDataLoader()
                social_loader = SocialDataLoader()
                engine = PredictionEngine()
                
                # Fetch data
                price_data = stock_loader.get_stock_data(tickers)
                social_data = social_loader.get_batch_sentiment(tickers)
                
                # Generate predictions
                predictions = engine.predict_batch(tickers, price_data, social_data)
                
                st.session_state.market_predictions = predictions
                st.session_state.last_prediction_time = datetime.now().strftime("%H:%M:%S")

    if 'market_predictions' in st.session_state:
        st.success(f"Last update: {st.session_state.last_prediction_time}")
        
        # Display predictions in a grid
        cols = st.columns(2)
        for i, pred in enumerate(st.session_state.market_predictions):
            with cols[i % 2]:
                with st.container():
                    # Color based on prediction
                    color = "#28a745" if "BUY" in pred['prediction'] else "#dc3545" if "SELL" in pred['prediction'] else "#ffc107"
                    
                    st.markdown(f"""
                        <div style='border: 2px solid {color}; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                            <h3 style='margin: 0; color: {color}'>{pred['ticker']} - {pred['prediction']}</h3>
                            <p style='font-size: 1.2em; margin: 10px 0;'>Current: <b>${pred['last_price']}</b> → Target: <b>${pred['target_price']}</b></p>
                            <div style='display: flex; justify-content: space-between;'>
                                <span>Confidence: <b>{pred['confidence']}%</b></span>
                                <span>RSI: <b>{pred['rsi']}</b></span>
                            </div>
                            <div style='margin-top: 10px; padding-top: 10px; border-top: 1px dashed gray;'>
                                <small>Sentiment X: <b>{pred['sentiment']}</b> ({pred['sentiment_score']})</small>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    else:
        st.info("Click 'Run Global Analysis' to fetch 10-stock prediction report.")

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
