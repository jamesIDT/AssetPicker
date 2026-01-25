"""Crypto RSI Screener - Main Streamlit application."""

import asyncio
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from src.charts import build_acceleration_quadrant, build_rsi_scatter
from src.coingecko import CoinGeckoClient
from src.data_store import (
    load_data,
    save_data,
    load_hourly_data,
    save_hourly_data,
    is_hourly_cache_valid,
)
from src.indicators import (
    calculate_beta_adjusted_rsi,
    calculate_divergence_score,
    calculate_multi_tf_divergence,
    calculate_opportunity_score,
    calculate_rsi_acceleration,
    calculate_zscore,
    classify_signal_lifecycle,
    detect_divergence,
    detect_regime,
    detect_volatility_regime,
)
from src.sectors import calculate_sector_momentum, calculate_sector_rsi, get_sector
from src.rsi import calculate_multi_tf_rsi, calculate_rsi, extract_closes, get_daily_rsi, get_weekly_rsi

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Crypto RSI Screener",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Design System CSS - Dark Theme with Yellow-Orange Accent
st.markdown(
    """
    <style>
    /* =================================================================
       GOOGLE FONTS IMPORT
       ================================================================= */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    /* =================================================================
       CSS DESIGN TOKENS
       ================================================================= */
    :root {
        /* Background colors */
        --bg-0: #3E4253;           /* Primary background (dark slate) */
        --bg-1: #4A4F5E;           /* Slightly lighter for panels */
        --bg-2: #565B6B;           /* Hover states */

        /* Text colors */
        --text-0: #F6F8F7;         /* Off-white primary text */
        --text-1: rgba(246, 248, 247, 0.72);  /* Secondary text */
        --text-2: rgba(246, 248, 247, 0.54);  /* Tertiary/muted text */

        /* Accent colors */
        --accent: #B69A5A;         /* Gold/mustard hero color */
        --accent-2: #D4BA7A;       /* Lighter gold for hover */
        --copper: #A77C65;         /* Secondary accent (copper) */
        --mauve: #7C6065;          /* Tertiary accent (dusty rose) */

        /* Panel/surface colors */
        --panel: rgba(246, 248, 247, 0.04);       /* Panel background */
        --panel-hover: rgba(246, 248, 247, 0.08); /* Panel hover */

        /* Borders and lines */
        --line: rgba(246, 248, 247, 0.12);        /* Subtle borders */
    }

    /* =================================================================
       GLOBAL STREAMLIT OVERRIDES
       ================================================================= */

    /* Main app background */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .main .block-container {
        background-color: var(--bg-0) !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div {
        background-color: var(--bg-0) !important;
        border-right: 1px solid var(--line) !important;
    }

    /* All text defaults to cream */
    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp div {
        color: var(--text-0) !important;
    }

    /* Headings */
    .stApp h1,
    .stApp h2,
    .stApp h3 {
        color: var(--text-0) !important;
        letter-spacing: 0.02em;
    }

    /* Captions and small text */
    .stApp small,
    .stApp .stCaption,
    [data-testid="stCaption"] {
        color: var(--text-2) !important;
    }

    /* =================================================================
       PRIMARY BUTTON STYLING
       ================================================================= */
    [data-testid="stButton"] button[kind="primary"],
    .stButton > button[kind="primary"] {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: var(--bg-0) !important;
        border-radius: 2px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stButton"] button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: var(--accent-2) !important;
        border-color: var(--accent-2) !important;
        color: var(--bg-0) !important;
    }

    /* Secondary buttons */
    [data-testid="stButton"] button:not([kind="primary"]),
    .stButton > button:not([kind="primary"]) {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        color: var(--text-0) !important;
        border-radius: 2px !important;
    }

    [data-testid="stButton"] button:not([kind="primary"]):hover,
    .stButton > button:not([kind="primary"]):hover {
        background-color: var(--panel-hover) !important;
        border-color: var(--accent) !important;
    }

    /* =================================================================
       PANEL / EXPANDER STYLING
       ================================================================= */
    [data-testid="stExpander"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 2px !important;
    }

    [data-testid="stExpander"]:hover {
        background-color: var(--panel-hover) !important;
    }

    [data-testid="stExpander"] summary {
        color: var(--text-0) !important;
    }

    /* Expander header/toggle - fix arrow overlap */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-0) !important;
        font-weight: 500 !important;
    }

    /* Fix expander icon - hide Material Icons text and use CSS triangle */
    [data-testid="stExpander"] details > summary {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }

    /* Hide the broken Material Icons text completely */
    [data-testid="stIconMaterial"] {
        font-size: 0 !important;
        width: 16px !important;
        height: 16px !important;
        display: inline-block !important;
        position: relative !important;
    }

    /* Replace with CSS arrow */
    [data-testid="stIconMaterial"]::before {
        content: "▸" !important;
        font-size: 1rem !important;
        color: var(--text-1) !important;
        position: absolute !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        transition: transform 0.2s ease !important;
    }

    [data-testid="stExpander"] details[open] [data-testid="stIconMaterial"]::before {
        content: "▾" !important;
    }

    /* =================================================================
       INPUT / SELECT STYLING
       ================================================================= */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    [data-testid="stSelectbox"] > div > div,
    [data-baseweb="select"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        color: var(--text-0) !important;
        border-radius: 2px !important;
    }

    /* Input focus state */
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    [data-baseweb="select"]:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    /* Dropdown menus */
    [data-baseweb="menu"],
    [data-baseweb="popover"] > div {
        background-color: var(--bg-2) !important;
        border: 1px solid var(--line) !important;
    }

    [data-baseweb="menu"] li,
    [data-baseweb="menu"] [role="option"] {
        color: var(--text-0) !important;
    }

    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [role="option"]:hover {
        background-color: var(--panel-hover) !important;
    }

    /* =================================================================
       METRIC STYLING
       ================================================================= */
    [data-testid="stMetric"] {
        background-color: var(--panel) !important;
        padding: 1rem !important;
        border-radius: 2px !important;
        border: 1px solid var(--line) !important;
    }

    [data-testid="stMetric"] label,
    [data-testid="stMetricLabel"] {
        color: var(--text-2) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] {
        color: var(--text-0) !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: var(--text-1) !important;
    }

    /* =================================================================
       TAB STYLING
       ================================================================= */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        border-bottom: 1px solid var(--line) !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-2) !important;
        background-color: transparent !important;
        border-radius: 2px 2px 0 0 !important;
        padding: 0.5rem 1rem !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-0) !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Tab panel content */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem !important;
    }

    /* =================================================================
       SCROLLBAR STYLING (WEBKIT)
       ================================================================= */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-0);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--line);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--bg-1);
    }

    /* =================================================================
       LOADING / SPINNER STYLING
       ================================================================= */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* =================================================================
       ALERT STYLING (error, warning, info, success)
       ================================================================= */
    /* Error alerts - dark red background */
    [data-testid="stAlert"][data-baseweb="notification"][kind="error"],
    .stAlert div[data-testid="stNotificationContentError"] {
        background-color: rgba(244, 67, 54, 0.15) !important;
        border-left: 3px solid #f44336 !important;
    }

    /* Warning alerts - dark orange/yellow background */
    [data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
    .stAlert div[data-testid="stNotificationContentWarning"] {
        background-color: rgba(255, 152, 0, 0.15) !important;
        border-left: 3px solid #FF9800 !important;
    }

    /* Info alerts - dark blue background */
    [data-testid="stAlert"][data-baseweb="notification"][kind="info"],
    .stAlert div[data-testid="stNotificationContentInfo"] {
        background-color: rgba(33, 150, 243, 0.15) !important;
        border-left: 3px solid #2196F3 !important;
    }

    /* Success alerts - dark green background */
    [data-testid="stAlert"][data-baseweb="notification"][kind="success"],
    .stAlert div[data-testid="stNotificationContentSuccess"] {
        background-color: rgba(76, 175, 80, 0.15) !important;
        border-left: 3px solid #4CAF50 !important;
    }

    /* Alert text color - cream for all */
    .stAlert p,
    .stAlert span,
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: var(--text-0) !important;
    }

    /* =================================================================
       SPACING / LAYOUT POLISH
       ================================================================= */
    /* Reduce excessive gaps between major sections */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }

    /* Tighten spacing around subheaders */
    .stSubheader,
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Consistent chart container margins */
    [data-testid="stPlotlyChart"] {
        margin-bottom: 0 !important;
    }

    /* =================================================================
       DATAFRAME / TABLE STYLING - Dark theme
       ================================================================= */
    [data-testid="stDataFrame"],
    .stDataFrame {
        background-color: var(--bg-1) !important;
        border: 1px solid var(--line) !important;
        border-radius: 2px !important;
    }

    /* Table headers */
    [data-testid="stDataFrame"] th,
    .stDataFrame th,
    [data-testid="stTable"] th {
        background-color: var(--bg-0) !important;
        color: var(--text-1) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* Table cells */
    [data-testid="stDataFrame"] td,
    .stDataFrame td,
    [data-testid="stTable"] td {
        background-color: var(--bg-1) !important;
        color: var(--text-0) !important;
        border-bottom: 1px solid var(--line) !important;
    }

    /* Table row hover */
    [data-testid="stDataFrame"] tr:hover td,
    .stDataFrame tr:hover td,
    [data-testid="stTable"] tr:hover td {
        background-color: var(--bg-2) !important;
    }

    /* =================================================================
       DIVIDER / SEPARATOR
       ================================================================= */
    hr,
    [data-testid="stSeparator"] {
        border-color: var(--line) !important;
    }

    /* =================================================================
       LINK STYLING
       ================================================================= */
    a {
        color: var(--accent) !important;
    }

    a:hover {
        color: var(--accent-2) !important;
    }

    /* =================================================================
       TYPOGRAPHY - GLOBAL FONT FAMILY
       ================================================================= */
    * {
        font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace !important;
    }

    /* =================================================================
       TYPOGRAPHY UTILITY CLASSES
       ================================================================= */
    .tracking-caps {
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-weight: 500 !important;
    }

    .text-accent {
        color: var(--accent) !important;
    }

    .text-muted {
        color: var(--text-2) !important;
    }

    /* =================================================================
       SECTION HEADERS - Stage-style with accent
       ================================================================= */
    .section-header {
        color: var(--accent) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-bottom: 0.75rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid var(--line) !important;
    }

    /* =================================================================
       BORDERED PANEL SYSTEM
       ================================================================= */
    .bordered-panel {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 2px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }

    .bordered-panel:hover {
        background: var(--panel-hover) !important;
    }

    .panel-title {
        color: var(--text-0) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 0.75rem !important;
    }

    /* =================================================================
       CHART PANEL TITLE BUTTONS (tertiary buttons as clickable headers)
       ================================================================= */
    /* Style tertiary buttons as panel title bars */
    [data-testid="stButton"] button[kind="tertiary"] {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 2px !important;
        color: var(--text-0) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        padding: 0.75rem 1rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stButton"] button[kind="tertiary"]:hover {
        background: var(--panel-hover) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* =================================================================
       FULLSCREEN DIALOG/MODAL STYLING
       ================================================================= */
    /* Target overlay backdrop */
    .stDialog,
    [data-baseweb="modal"] {
        background-color: var(--bg-0) !important;
        padding: 0 !important;
    }

    /* Target all modal containers and wrappers */
    .stDialog > div,
    [data-baseweb="modal"] > div,
    .st-emotion-cache-1gulkj5,
    .st-emotion-cache-z5fcl4 {
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw !important;
        max-height: 100vh !important;
        min-width: 100vw !important;
        min-height: 100vh !important;
        align-items: stretch !important;
        justify-content: stretch !important;
        padding: 0 !important;
        margin: 0 !important;
        inset: 0 !important;
        position: fixed !important;
    }

    /* Target the dialog box itself - multiple selectors for specificity */
    div[role="dialog"],
    [data-baseweb="modal"] div[role="dialog"],
    .stDialog div[role="dialog"] {
        background-color: var(--bg-0) !important;
        border: none !important;
        border-radius: 0 !important;
        width: 100vw !important;
        max-width: 100vw !important;
        min-width: 100vw !important;
        height: 100vh !important;
        max-height: 100vh !important;
        min-height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        inset: 0 !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        position: fixed !important;
        transform: none !important;
    }

    /* Dialog header styling */
    div[role="dialog"] > div:first-child {
        background-color: var(--bg-1) !important;
        border-bottom: 1px solid var(--line) !important;
        padding: 0.75rem 1rem !important;
    }

    /* Dialog title text */
    div[role="dialog"] > div:first-child span {
        color: var(--text-0) !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* Dialog close button */
    div[role="dialog"] button {
        color: var(--text-2) !important;
    }

    div[role="dialog"] button:hover {
        color: var(--accent) !important;
    }

    /* Dialog content area - fill remaining space */
    div[role="dialog"] > div:last-child {
        padding: 1rem !important;
        height: calc(100vh - 50px) !important;
        max-height: calc(100vh - 50px) !important;
        overflow: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state - load from persistent storage if available
if "coin_data" not in st.session_state:
    # Try to load from persistent storage first
    cached_data = load_data()
    if cached_data:
        st.session_state.coin_data = cached_data["coin_data"]
        st.session_state.divergence_data = cached_data["divergence_data"]
        st.session_state.last_updated = cached_data["last_updated"]
        st.session_state.failed_coins = cached_data["failed_coins"]
        st.session_state.btc_regime = cached_data["btc_regime"]
        st.session_state.btc_weekly_rsi = cached_data["btc_weekly_rsi"]
        # Load hourly data separately (different cache)
        hourly_cached = load_hourly_data()
        st.session_state.hourly_history = hourly_cached.get("hourly_history") if hourly_cached else None
        # Multi-timeframe data (calculated on demand)
        st.session_state.multi_tf_rsi = {}
        st.session_state.multi_tf_divergence = {}
    else:
        st.session_state.coin_data = None
        st.session_state.divergence_data = None
        st.session_state.last_updated = None
        st.session_state.failed_coins = 0
        st.session_state.btc_regime = None
        st.session_state.btc_weekly_rsi = None
        st.session_state.hourly_history = None
        st.session_state.multi_tf_rsi = {}
        st.session_state.multi_tf_divergence = {}
if "selected_sector" not in st.session_state:
    st.session_state.selected_sector = "All Sectors"


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '5 min ago')."""
    now = datetime.now()
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} min ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    else:
        days = seconds // 86400
        return f"{days}d ago"


def load_watchlist() -> list[dict]:
    """Load watchlist from JSON file."""
    with open("watchlist.json") as f:
        data = json.load(f)
    return data.get("coins", [])


def get_rsi_history(closes: list[float], period: int = 14) -> list[float]:
    """
    Calculate RSI history (rolling RSI values) for divergence detection.

    Args:
        closes: List of closing prices (oldest to newest)
        period: RSI period (default: 14)

    Returns:
        List of RSI values starting from when there's enough data
    """
    if len(closes) < period + 1:
        return []

    rsi_history = []

    # Calculate deltas
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # First average
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Calculate first RSI
    if avg_loss == 0:
        rsi_history.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_history.append(100 - (100 / (1 + rs)))

    # Calculate remaining RSI values with smoothing
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi_history.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_history.append(100 - (100 / (1 + rs)))

    return rsi_history


def aggregate_to_weekly(prices: list[tuple[int, float]]) -> list[float]:
    """
    Aggregate daily price data to weekly closes.

    Args:
        prices: List of (timestamp_ms, price) tuples

    Returns:
        List of weekly closing prices (oldest to newest)
    """
    if not prices:
        return []

    weekly_closes: dict[tuple[int, int], float] = {}

    for timestamp_ms, price in prices:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        iso = dt.isocalendar()
        week_key = (iso.year, iso.week)
        weekly_closes[week_key] = price

    sorted_weeks = sorted(weekly_closes.keys())
    return [weekly_closes[week] for week in sorted_weeks]


async def fetch_all_data(coin_ids: list[str]) -> tuple[list[dict], list[dict], int, dict | None, float | None, dict | None, dict, dict]:
    """
    Fetch market data and calculate RSI for all coins.

    Args:
        coin_ids: List of CoinGecko coin IDs

    Returns:
        Tuple of (coin data list, divergence data list, failed count, btc_regime, btc_weekly_rsi, hourly_history, multi_tf_rsi, multi_tf_divergence)
    """
    async with CoinGeckoClient() as client:
        # Fetch market data and history concurrently
        market_data = await client.get_coins_market_data(coin_ids)
        history = await client.get_coins_history(coin_ids, days=120)

        # Fetch hourly data (with caching)
        hourly_history = None
        if is_hourly_cache_valid():
            hourly_cached = load_hourly_data()
            if hourly_cached:
                hourly_history = hourly_cached.get("hourly_history")
        else:
            # Fetch fresh hourly data
            hourly_history = await client.get_coins_hourly_history(coin_ids, days=90)
            # Save to cache
            save_hourly_data(hourly_history, datetime.now())

    # Build lookup for market data
    market_lookup = {c["id"]: c for c in market_data}

    # Calculate BTC regime and beta reference data if BTC data is available
    btc_regime = None
    btc_weekly_rsi = None
    btc_returns: list[float] = []
    btc_daily_rsi: float | None = None

    if "bitcoin" in history:
        btc_hist = history["bitcoin"]
        btc_prices = btc_hist.get("prices", [])
        btc_weekly_closes = aggregate_to_weekly(btc_prices)
        btc_weekly_rsi_history = get_rsi_history(btc_weekly_closes)
        if btc_weekly_rsi_history:
            btc_weekly_rsi = btc_weekly_rsi_history[-1]
            btc_regime = detect_regime(btc_weekly_rsi_history)

        # Calculate BTC daily returns for beta calculation
        if len(btc_prices) >= 2:
            for i in range(1, len(btc_prices)):
                prev_price = btc_prices[i - 1][1]
                curr_price = btc_prices[i][1]
                if prev_price > 0:
                    btc_returns.append((curr_price - prev_price) / prev_price)

        # Get BTC daily RSI for expected RSI calculation
        btc_daily_rsi = get_daily_rsi(btc_hist)

    # Calculate ETH returns and RSI for ETH benchmark
    eth_returns: list[float] = []
    eth_daily_rsi: float | None = None

    if "ethereum" in history:
        eth_hist = history["ethereum"]
        eth_prices = eth_hist.get("prices", [])

        # Calculate ETH daily returns
        if len(eth_prices) >= 2:
            for i in range(1, len(eth_prices)):
                prev_price = eth_prices[i - 1][1]
                curr_price = eth_prices[i][1]
                if prev_price > 0:
                    eth_returns.append((curr_price - prev_price) / prev_price)

        # Get ETH daily RSI
        eth_daily_rsi = get_daily_rsi(eth_hist)

    # Calculate Total3 (synthetic altcoin index) returns
    # Total3 = Total market cap minus BTC, ETH, and stablecoins
    # We approximate this by creating a market-cap weighted index of altcoins
    stablecoin_ids = {"tether", "usd-coin", "dai", "binance-usd", "true-usd", "frax", "paxos-standard"}
    excluded_ids = {"bitcoin", "ethereum"} | stablecoin_ids

    # Collect altcoin returns with market caps for weighting
    altcoin_data: list[tuple[str, list[float], float]] = []  # (coin_id, returns, market_cap)
    for coin_id in coin_ids:
        if coin_id in excluded_ids:
            continue
        if coin_id not in history or coin_id not in market_lookup:
            continue

        hist = history[coin_id]
        prices = hist.get("prices", [])
        mcap = market_lookup[coin_id].get("market_cap", 0)

        if len(prices) >= 2 and mcap > 0:
            coin_returns_list = []
            for i in range(1, len(prices)):
                prev_price = prices[i - 1][1]
                curr_price = prices[i][1]
                if prev_price > 0:
                    coin_returns_list.append((curr_price - prev_price) / prev_price)
            if coin_returns_list:
                altcoin_data.append((coin_id, coin_returns_list, mcap))

    # Calculate market-cap weighted Total3 returns
    total3_returns: list[float] = []
    total3_daily_rsi: float | None = None

    if altcoin_data:
        # Find minimum return length across all altcoins
        min_len = min(len(r) for _, r, _ in altcoin_data)
        if min_len >= 30:
            total_mcap = sum(mcap for _, _, mcap in altcoin_data)

            # Calculate weighted average return for each day
            for day_idx in range(min_len):
                weighted_return = 0.0
                for _, returns, mcap in altcoin_data:
                    # Use returns from the end (most recent)
                    idx = len(returns) - min_len + day_idx
                    weight = mcap / total_mcap
                    weighted_return += returns[idx] * weight
                total3_returns.append(weighted_return)

            # Calculate synthetic Total3 price series and RSI
            # Start with price of 100 and apply returns
            total3_prices = [100.0]
            for ret in total3_returns:
                total3_prices.append(total3_prices[-1] * (1 + ret))

            # Calculate Total3 RSI
            if len(total3_prices) >= 15:
                total3_rsi_history = get_rsi_history(total3_prices)
                if total3_rsi_history:
                    total3_daily_rsi = total3_rsi_history[-1]

    # Pre-calculate coins_for_sector and sector momentum (needed for opportunity score)
    coins_for_sector_pre = []
    for coin_id in coin_ids:
        if coin_id in market_lookup and coin_id in history:
            market = market_lookup[coin_id]
            hist = history[coin_id]
            daily_rsi_val = get_daily_rsi(hist)
            if daily_rsi_val is not None:
                daily_closes = extract_closes(hist)
                daily_rsi_history = get_rsi_history(daily_closes)
                coins_for_sector_pre.append({
                    "id": coin_id,
                    "daily_rsi": daily_rsi_val,
                    "market_cap": market.get("market_cap", 0),
                    "rsi_history": daily_rsi_history[-30:] if len(daily_rsi_history) >= 30 else daily_rsi_history,
                })

    # Calculate sector momentum before main loop for opportunity scoring
    sector_momentum = calculate_sector_momentum(coins_for_sector_pre)

    result = []
    divergence_result = []
    failed_count = 0

    for coin_id in coin_ids:
        if coin_id not in market_lookup or coin_id not in history:
            failed_count += 1
            continue

        market = market_lookup[coin_id]
        hist = history[coin_id]

        # Calculate RSI values
        daily_rsi = get_daily_rsi(hist)
        weekly_rsi = get_weekly_rsi(hist)

        # Skip if RSI couldn't be calculated
        if daily_rsi is None or weekly_rsi is None:
            failed_count += 1
            continue

        # Calculate vol/mcap ratio
        volume = market.get("total_volume", 0)
        mcap = market.get("market_cap", 0)
        vol_mcap_ratio = volume / mcap if mcap > 0 else 0

        # Calculate beta-adjusted RSI for all three benchmarks
        beta_info_btc = None
        beta_info_eth = None
        beta_info_total3 = None
        prices = hist.get("prices", [])

        if len(prices) >= 2:
            coin_returns = []
            for i in range(1, len(prices)):
                prev_price = prices[i - 1][1]
                curr_price = prices[i][1]
                if prev_price > 0:
                    coin_returns.append((curr_price - prev_price) / prev_price)

            # Beta vs BTC
            if len(btc_returns) >= 30 and btc_daily_rsi is not None:
                min_len = min(len(coin_returns), len(btc_returns))
                if min_len >= 30:
                    aligned_coin_returns = coin_returns[-min_len:]
                    aligned_btc_returns = btc_returns[-min_len:]
                    beta_info_btc = calculate_beta_adjusted_rsi(
                        aligned_coin_returns, aligned_btc_returns, daily_rsi, btc_daily_rsi
                    )

            # Beta vs ETH
            if len(eth_returns) >= 30 and eth_daily_rsi is not None:
                min_len = min(len(coin_returns), len(eth_returns))
                if min_len >= 30:
                    aligned_coin_returns = coin_returns[-min_len:]
                    aligned_eth_returns = eth_returns[-min_len:]
                    beta_info_eth = calculate_beta_adjusted_rsi(
                        aligned_coin_returns, aligned_eth_returns, daily_rsi, eth_daily_rsi
                    )

            # Beta vs Total3
            if len(total3_returns) >= 30 and total3_daily_rsi is not None:
                min_len = min(len(coin_returns), len(total3_returns))
                if min_len >= 30:
                    aligned_coin_returns = coin_returns[-min_len:]
                    aligned_total3_returns = total3_returns[-min_len:]
                    beta_info_total3 = calculate_beta_adjusted_rsi(
                        aligned_coin_returns, aligned_total3_returns, daily_rsi, total3_daily_rsi
                    )

        # Keep beta_info as the default (BTC) for backward compatibility
        beta_info = beta_info_btc

        # Calculate signal lifecycle for oversold and overbought
        prices = hist.get("prices", [])
        daily_closes = extract_closes(hist)
        daily_rsi_history = get_rsi_history(daily_closes)

        lifecycle_oversold = None
        lifecycle_overbought = None
        if len(daily_rsi_history) >= 5:
            lifecycle_oversold = classify_signal_lifecycle(
                daily_rsi_history, extreme_threshold=30.0, is_oversold=True
            )
            lifecycle_overbought = classify_signal_lifecycle(
                daily_rsi_history, extreme_threshold=70.0, is_oversold=False
            )

        # Calculate volatility regime
        volatility = None
        if len(daily_closes) >= 57:  # 4 * 14 + 1
            volatility = detect_volatility_regime(daily_closes, period=14)

        # Calculate RSI acceleration
        acceleration = None
        if len(daily_rsi_history) >= 3:
            acceleration = calculate_rsi_acceleration(daily_rsi_history)

        # Calculate price change since signal started
        price_change_pct = None
        current_price = market.get("current_price", 0)
        if lifecycle_oversold and lifecycle_oversold.get("state") != "none":
            days_in = lifecycle_oversold.get("days_in_zone", 0)
            if days_in > 0 and days_in <= len(daily_closes) and current_price > 0:
                entry_price = daily_closes[-(days_in + 1)] if days_in + 1 <= len(daily_closes) else daily_closes[0]
                price_change_pct = ((current_price - entry_price) / entry_price) * 100
        elif lifecycle_overbought and lifecycle_overbought.get("state") != "none":
            days_in = lifecycle_overbought.get("days_in_zone", 0)
            if days_in > 0 and days_in <= len(daily_closes) and current_price > 0:
                entry_price = daily_closes[-(days_in + 1)] if days_in + 1 <= len(daily_closes) else daily_closes[0]
                price_change_pct = ((current_price - entry_price) / entry_price) * 100

        # Build coin data dict (will add opportunity_score after divergence calculation)
        coin_data = {
            "id": coin_id,
            "symbol": market.get("symbol", "").upper(),
            "name": market.get("name", ""),
            "daily_rsi": daily_rsi,
            "weekly_rsi": weekly_rsi,
            "vol_mcap_ratio": vol_mcap_ratio,
            "price": market.get("current_price", 0),
            "volume": volume,
            "market_cap": mcap,
            "beta_info": beta_info,  # Default (BTC) for backward compatibility
            "beta_info_btc": beta_info_btc,
            "beta_info_eth": beta_info_eth,
            "beta_info_total3": beta_info_total3,
            "lifecycle_oversold": lifecycle_oversold,
            "lifecycle_overbought": lifecycle_overbought,
            "volatility": volatility,
            "acceleration": acceleration,
            "price_change_pct": price_change_pct,
            "rsi_history": daily_rsi_history[-30:] if len(daily_rsi_history) >= 30 else daily_rsi_history,
        }

        # Calculate divergence data (reuse prices, daily_closes, daily_rsi_history from above)

        # Weekly data for weekly divergence
        weekly_closes = aggregate_to_weekly(prices)
        weekly_rsi_history = get_rsi_history(weekly_closes)

        # Detect daily divergence (use last 14 periods)
        daily_div = None
        if len(daily_closes) >= 14 and len(daily_rsi_history) >= 14:
            daily_div = detect_divergence(
                daily_closes[-14:], daily_rsi_history[-14:], lookback=14
            )

        # Detect weekly divergence
        weekly_div = None
        if len(weekly_closes) >= 14 and len(weekly_rsi_history) >= 14:
            weekly_div = detect_divergence(
                weekly_closes[-14:], weekly_rsi_history[-14:], lookback=14
            )

        # Calculate combined score
        score = calculate_divergence_score(daily_div, weekly_div)

        # Determine dominant divergence type
        # Priority: daily divergence, then weekly
        div_type = "none"
        if daily_div and daily_div.get("type") != "none":
            div_type = daily_div["type"]
        elif weekly_div and weekly_div.get("type") != "none":
            div_type = weekly_div["type"]

        divergence_result.append({"type": div_type, "score": score})

        # Calculate opportunity score
        # Get sector for this coin
        sector = get_sector(coin_id)
        coin_data["sector"] = sector

        # Determine signal direction
        signal_direction = "long" if daily_rsi < 50 else "short"
        coin_data["signal_direction"] = signal_direction

        # Get days in zone from lifecycle
        days_in_zone = 0
        if signal_direction == "long" and lifecycle_oversold:
            days_in_zone = lifecycle_oversold.get("days_in_zone", 0)
        elif signal_direction == "short" and lifecycle_overbought:
            days_in_zone = lifecycle_overbought.get("days_in_zone", 0)

        # Calculate zscore for this coin
        zscore_val = 0
        if len(daily_rsi_history) >= 10:
            zscore_info = calculate_zscore(daily_rsi_history, lookback=90)
            if zscore_info:
                zscore_val = zscore_info.get("zscore", 0)
                coin_data["zscore_info"] = zscore_info

        # Check weekly extreme
        weekly_extreme = weekly_rsi < 30 or weekly_rsi > 70

        # Check volatility compressed
        volatility_compressed = volatility is not None and volatility.get("regime") == "compressed"

        # Check sector turning (from pre-calculated sector_momentum)
        sector_turning = False
        if sector in sector_momentum:
            sector_turning = sector_momentum[sector].get("is_rotation_signal", False)

        # Check decorrelation positive (based on beta interpretation and signal direction)
        decorrelation_positive = False
        if beta_info:
            interp = beta_info.get("interpretation", "")
            # For long (oversold): outperforming is positive decorrelation (holding up better than expected)
            # For short (overbought): underperforming is positive decorrelation (falling faster than expected)
            if signal_direction == "long" and interp == "outperforming":
                decorrelation_positive = True
            elif signal_direction == "short" and interp == "underperforming":
                decorrelation_positive = True

        # Build factors dict
        opportunity_factors = {
            "zscore": zscore_val,
            "days_in_zone": days_in_zone,
            "weekly_extreme": weekly_extreme,
            "divergence_score": score,
            "volatility_compressed": volatility_compressed,
            "sector_turning": sector_turning,
            "funding_aligned": False,  # Not implemented yet (no funding data)
            "decorrelation_positive": decorrelation_positive,
        }

        # Calculate opportunity score
        opportunity_score = calculate_opportunity_score(opportunity_factors)
        coin_data["opportunity_score"] = opportunity_score

        result.append(coin_data)

    # Calculate sector RSI and rankings
    # Build list for sector calculation (need id, daily_rsi)
    coins_for_sector = []
    for i, coin_id in enumerate(coin_ids):
        if coin_id in market_lookup and coin_id in history:
            market = market_lookup[coin_id]
            hist = history[coin_id]
            daily_rsi_val = get_daily_rsi(hist)
            if daily_rsi_val is not None:
                coins_for_sector.append({
                    "id": coin_id,
                    "daily_rsi": daily_rsi_val,
                    "market_cap": market.get("market_cap", 0),
                })

    sector_rsi = calculate_sector_rsi(coins_for_sector)

    # Add sector_rank to each result coin (sector, id, zscore_info already added in main loop)
    # Build a lookup from coin_id to result index for efficient update
    coin_id_to_result_idx = {r["id"]: i for i, r in enumerate(result)}

    for coin_id, result_idx in coin_id_to_result_idx.items():
        sector = result[result_idx].get("sector", "Other")

        # Determine sector ranking
        sector_rank = None
        if sector in sector_rsi:
            sector_info = sector_rsi[sector]
            sector_coins = sector_info.get("coins", [])
            if len(sector_coins) >= 2:
                # Get RSI values for all coins in this sector
                sector_coin_rsi = []
                for c in coins_for_sector:
                    if c["id"] in sector_coins:
                        sector_coin_rsi.append((c["id"], c["daily_rsi"]))

                if len(sector_coin_rsi) >= 2:
                    # Sort by daily_rsi (lowest = most oversold = best opportunity)
                    sector_coin_rsi.sort(key=lambda x: x[1])
                    if sector_coin_rsi[0][0] == coin_id:
                        sector_rank = "best"
                    elif sector_coin_rsi[-1][0] == coin_id:
                        sector_rank = "worst"

        result[result_idx]["sector_rank"] = sector_rank

    # Calculate multi-timeframe RSI and divergence for all coins
    multi_tf_rsi_all: dict = {}
    multi_tf_divergence_all: dict = {}

    for coin_id in coin_ids:
        hourly = hourly_history.get(coin_id, {}) if hourly_history else {}
        daily = history.get(coin_id, {})

        # Calculate multi-TF RSI
        multi_rsi = calculate_multi_tf_rsi(hourly, daily)
        if multi_rsi:
            multi_tf_rsi_all[coin_id] = multi_rsi

        # Calculate multi-TF divergence
        multi_div = calculate_multi_tf_divergence(hourly, daily, multi_rsi)
        if multi_div:
            multi_tf_divergence_all[coin_id] = multi_div

    return result, divergence_result, failed_count, btc_regime, btc_weekly_rsi, hourly_history, multi_tf_rsi_all, multi_tf_divergence_all


# Load watchlist with error handling
try:
    watchlist = load_watchlist()
except FileNotFoundError:
    st.error("watchlist.json not found. Create it with a 'coins' array.")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"Invalid JSON in watchlist.json: {e}")
    st.stop()

coin_ids = [c["id"] for c in watchlist]

# === HEADER ROW: Title + Refresh Button ===
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.title("Crypto RSI Screener")
    # Sub-header: Data source + timestamp
    subheader_parts = ["Data from CoinGecko Pro API"]
    if st.session_state.last_updated:
        relative = format_relative_time(st.session_state.last_updated)
        full_time = st.session_state.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        subheader_parts.append(f"Updated {relative} ({full_time})")
        if st.session_state.failed_coins > 0:
            subheader_parts.append(f"{st.session_state.failed_coins} coin(s) unavailable")
    st.caption(" · ".join(subheader_parts))
with header_col2:
    st.write("")  # Spacer for vertical alignment
    if st.button("Refresh Data", type="primary", use_container_width=True):
        with st.spinner("Fetching data from CoinGecko..."):
            try:
                data, divergence_data, failed_count, btc_regime, btc_weekly_rsi, hourly_history, multi_tf_rsi, multi_tf_divergence = asyncio.run(fetch_all_data(coin_ids))
                st.session_state.coin_data = data
                st.session_state.divergence_data = divergence_data
                st.session_state.last_updated = datetime.now()
                st.session_state.failed_coins = failed_count
                st.session_state.btc_regime = btc_regime
                st.session_state.btc_weekly_rsi = btc_weekly_rsi
                st.session_state.hourly_history = hourly_history
                st.session_state.multi_tf_rsi = multi_tf_rsi
                st.session_state.multi_tf_divergence = multi_tf_divergence
                # Save to persistent storage
                save_data(
                    coin_data=data,
                    divergence_data=divergence_data,
                    last_updated=st.session_state.last_updated,
                    failed_coins=failed_count,
                    btc_regime=btc_regime,
                    btc_weekly_rsi=btc_weekly_rsi,
                )
                st.rerun()
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")

# Display chart or message
if st.session_state.coin_data is not None:
    # Collapsible "How to Read This Dashboard" panel - centered
    with st.expander("Read This Dashboard", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### RSI Scatter Chart (Left)
            **Position = Daily RSI × Liquidity**
            - X-axis: Daily RSI (0-100)
            - Y-axis: Volume/Market Cap ratio (log scale)

            **Quadrants:**
            - 🟢 **Capitulation** (top-left): Oversold + High Activity
            - 🔴 **Peak Momentum** (top-right): Overbought + High Activity
            - ⬜ **Forgotten** (bottom-left): Oversold + Low Activity
            - 🟠 **Quiet Pump** (bottom-right): Overbought + Low Activity

            **Color = Weekly RSI alignment**
            - Green: Weekly oversold (<30) - timeframes aligned
            - Red: Weekly overbought (>70) - timeframes aligned
            - Yellow: Neutral weekly RSI

            **Marker Shapes:**
            - ● Circle: No divergence detected
            - + Cross: Bullish divergence (price lower, RSI higher)
            - ◆ Diamond: Bearish divergence (price higher, RSI lower)

            **Divergence Rings:**
            - Thin ring: Score 2 (single strong signal)
            - Bold ring: Score 4 (multi-timeframe confirmation)
            """)

        with col2:
            st.markdown("""
            ### Acceleration Quadrant (Right)
            **Position = RSI Acceleration × Volatility**
            - X-axis: RSI velocity change (positive = accelerating up)
            - Y-axis: Volatility ratio vs 20-day average

            **Quadrants:**
            - 🎯 **Coiled Spring** (bottom-right): Accelerating + Compressed → Best entry
            - 💥 **Explosive Move** (top-right): Accelerating + High Vol → Move in progress
            - ⚠️ **Exhausting** (top-left): Decelerating + High Vol → Move fading
            - 💤 **Dormant** (bottom-left): Decelerating + Compressed → Waiting

            ### Opportunity Leaderboard
            **Score (0-5)**: Multi-factor ranking combining:
            - RSI extremity and divergence
            - Signal freshness (newer = higher)
            - Volatility compression bonus
            - Funding rate confluence

            ### Signal Lifecycle
            - **Fresh** ★★★: New signal, highest conviction
            - **Confirmed** ★★: Sustained for 2-3 days
            - **Extended** ★: 4+ days, may be exhausting
            - **Resolving**: Moving back toward neutral
            """)

    # Handle empty data gracefully
    if not st.session_state.coin_data:
        st.warning("No valid coin data available. Check your watchlist configuration.")
    else:
        # Build sector counts for display
        sector_counts = {}
        for coin in st.session_state.coin_data:
            sector = coin.get("sector", "Other")
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        sector_options = ["All Sectors"] + [
            f"{sector} ({count})" for sector, count in sorted(sector_counts.items())
        ]

        # Prepare regime display data
        regime_html = ""
        if st.session_state.btc_regime is not None:
            regime = st.session_state.btc_regime
            btc_rsi = st.session_state.btc_weekly_rsi
            combined = regime.get("combined", "transition")

            # Map regime to display properties
            regime_display = {
                "bull_rising": ("🐂", "Bull", "Rising", "#4CAF50"),
                "bull_falling": ("🐂", "Bull", "Cooling", "#4CAF50"),
                "bull_neutral": ("🐂", "Bull", "Steady", "#4CAF50"),
                "bear_rising": ("🐻", "Bear", "Recovering", "#f44336"),
                "bear_falling": ("🐻", "Bear", "Falling", "#f44336"),
                "bear_neutral": ("🐻", "Bear", "Steady", "#f44336"),
                "transition": ("⚖️", "Transition", "", "#FFB020"),
            }

            emoji, regime_label, momentum_label, color = regime_display.get(
                combined, ("⚖️", "Transition", "", "#FFB020")
            )

            momentum_text = f" · {momentum_label}" if momentum_label else ""
            rsi_text = f"BTC Weekly RSI: {btc_rsi:.1f}" if btc_rsi is not None else ""

            regime_html = f"""
            <div style="
                background: rgba(30, 30, 35, 0.6);
                border: 1px solid {color}40;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: center;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 4px;">{emoji}</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: {color};">{regime_label}</div>
                <div style="font-size: 0.8rem; color: #888;">{momentum_text.strip(' · ')}</div>
                <div style="font-size: 0.85rem; color: #aaa; margin-top: 8px; padding-top: 8px; border-top: 1px solid #333;">{rsi_text}</div>
            </div>
            """

        # Build sector breakdown HTML
        sector_order = ["Majors", "DeFi", "AI", "DeSci"]
        sector_items = []
        for s in sector_order:
            if s in sector_counts:
                sector_items.append(f'<span style="color: #888;">{s}</span> <span style="color: #ccc;">{sector_counts[s]}</span>')
        sector_breakdown_html = " · ".join(sector_items)

        # === THREE-COLUMN CONTROL STRIP ===
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])

        # Column 1: Filters
        with ctrl_col1:
            st.markdown('<div style="font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Filters</div>', unsafe_allow_html=True)
            selected = st.selectbox(
                "Sector",
                sector_options,
                index=0,
                key="sector_filter",
                label_visibility="collapsed",
            )
            # Extract sector name (remove count suffix)
            if selected == "All Sectors":
                st.session_state.selected_sector = "All Sectors"
            else:
                st.session_state.selected_sector = selected.split(" (")[0]

            color_mode = st.radio(
                "Color by",
                ["Weekly RSI", "Beta Residual"],
                horizontal=False,
                label_visibility="visible",
                key="color_mode_radio",
            )

            # Show benchmark selector when Beta Residual mode is selected
            beta_benchmark = "BTC"
            if color_mode == "Beta Residual":
                beta_benchmark = st.radio(
                    "Beta Benchmark",
                    ["BTC", "ETH", "Total3"],
                    horizontal=True,
                    label_visibility="visible",
                    key="beta_benchmark_radio",
                    help="BTC: vs Bitcoin | ETH: vs Ethereum | Total3: vs Altcoin Index (excl. BTC, ETH, stables)",
                )

            show_zscore = st.checkbox(
                "Show Z-Score Labels",
                value=False,
            )

            # Timeframe highlight selector
            tf_highlight = st.radio(
                "Highlight Timeframe",
                ["All", "1w", "3d", "1d", "12h", "4h", "1h"],
                horizontal=False,
                label_visibility="visible",
                key="tf_highlight_radio",
            )

            # Convert "All" to None for the chart parameter
            highlight_tf = None if tf_highlight == "All" else tf_highlight

            # Store in session state for consistency
            if "highlight_tf" not in st.session_state:
                st.session_state.highlight_tf = None
            st.session_state.highlight_tf = highlight_tf

        # Filter coin data if sector selected
        if st.session_state.selected_sector != "All Sectors":
            filtered_coin_data = [
                c for c in st.session_state.coin_data
                if c.get("sector") == st.session_state.selected_sector
            ]
            filtered_divergence_data = [
                st.session_state.divergence_data[i]
                for i, c in enumerate(st.session_state.coin_data)
                if c.get("sector") == st.session_state.selected_sector
            ]
        else:
            filtered_coin_data = st.session_state.coin_data
            filtered_divergence_data = st.session_state.divergence_data

        # Column 2: Coverage stats
        with ctrl_col2:
            total_coins = len(st.session_state.coin_data)
            filtered_count = len(filtered_coin_data)
            display_count = filtered_count if st.session_state.selected_sector != "All Sectors" else total_coins

            st.markdown(f"""
            <div style="text-align: center; padding: 8px 0;">
                <div style="font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Coverage</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #F6F8F7; line-height: 1;">{display_count}</div>
                <div style="font-size: 0.9rem; color: #888; margin-top: 4px;">coins</div>
                <div style="font-size: 0.8rem; color: #666; margin-top: 12px; line-height: 1.6;">
                    {sector_breakdown_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Column 3: Market Regime
        with ctrl_col3:
            st.markdown('<div style="font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Market Regime</div>', unsafe_allow_html=True)
            if regime_html:
                st.markdown(regime_html, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #666; text-align: center; padding: 20px;">No regime data</div>', unsafe_allow_html=True)

        # Extract beta residuals for beta mode based on selected benchmark
        beta_residuals = None
        if color_mode == "Beta Residual":
            # Map benchmark selection to data key
            beta_key_map = {
                "BTC": "beta_info_btc",
                "ETH": "beta_info_eth",
                "Total3": "beta_info_total3",
            }
            beta_key = beta_key_map.get(beta_benchmark, "beta_info_btc")

            beta_residuals = []
            for c in filtered_coin_data:
                beta_info = c.get(beta_key) or c.get("beta_info")  # Fallback to default
                if beta_info is not None:
                    beta_residuals.append(beta_info.get("residual", 0))
                else:
                    beta_residuals.append(0)

        # Extract sector data for tooltips
        sector_data = []
        for c in filtered_coin_data:
            sector_data.append({
                "sector": c.get("sector", "Other"),
                "sector_rank": c.get("sector_rank"),
            })

        # Extract zscore data for labels and tooltips
        zscore_data = []
        for c in filtered_coin_data:
            zscore_data.append(c.get("zscore_info"))

        # Visual divider before charts
        st.markdown('<hr style="border: none; border-top: 1px solid #333; margin: 24px 0 16px 0;">', unsafe_allow_html=True)

        # Section Header: Charts
        st.markdown(
            '<div class="section-header">CHARTS — MARKET OVERVIEW</div>',
            unsafe_allow_html=True,
        )

        # Modal dialogs for fullscreen chart views
        @st.dialog("RSI Scatter", width="large")
        def show_rsi_scatter_modal():
            """Show RSI Scatter chart in fullscreen modal."""
            fig = build_rsi_scatter(
                filtered_coin_data,
                filtered_divergence_data,
                beta_data=beta_residuals,
                color_mode="beta_residual" if color_mode == "Beta Residual" else "weekly_rsi",
                sector_data=sector_data,
                zscore_data=zscore_data,
                show_zscore=show_zscore,
                height=900,
                beta_benchmark=beta_benchmark,
                multi_tf_divergence=st.session_state.get("multi_tf_divergence"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

        @st.dialog("Acceleration Quadrant", width="large")
        def show_accel_quadrant_modal():
            """Show Acceleration Quadrant chart in fullscreen modal."""
            accel_coins = [
                c for c in st.session_state.coin_data
                if c.get("acceleration") is not None and c.get("volatility") is not None
            ]
            if accel_coins:
                accel_fig = build_acceleration_quadrant(accel_coins, height=900)
                st.plotly_chart(accel_fig, use_container_width=True)
            else:
                st.info("Acceleration data requires price history. Refresh to load.")

        # Pre-build the charts for inline display (taller charts)
        rsi_scatter_fig = build_rsi_scatter(
            filtered_coin_data,
            filtered_divergence_data,
            beta_data=beta_residuals,
            color_mode="beta_residual" if color_mode == "Beta Residual" else "weekly_rsi",
            sector_data=sector_data,
            zscore_data=zscore_data,
            show_zscore=show_zscore,
            height=550,
            beta_benchmark=beta_benchmark,
            multi_tf_divergence=st.session_state.get("multi_tf_divergence"),
        )

        accel_coins = [
            c for c in st.session_state.coin_data
            if c.get("acceleration") is not None and c.get("volatility") is not None
        ]
        accel_fig = build_acceleration_quadrant(accel_coins, height=550) if accel_coins else None

        # Hero Charts Row - Equal width columns
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # RSI Scatter panel - button opens modal, chart below
            if st.button(
                "RSI SCATTER — Click to expand",
                key="btn_rsi_panel",
                use_container_width=True,
                type="tertiary",
            ):
                show_rsi_scatter_modal()
            st.plotly_chart(
                rsi_scatter_fig,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

        with chart_col2:
            # Acceleration Quadrant panel - button opens modal, chart below
            if st.button(
                "ACCELERATION QUADRANT — Click to expand",
                key="btn_accel_panel",
                use_container_width=True,
                type="tertiary",
            ):
                show_accel_quadrant_modal()
            if accel_fig:
                st.plotly_chart(
                    accel_fig,
                    use_container_width=True,
                    config={"responsive": True, "displayModeBar": False},
                )
            else:
                st.info("Acceleration data requires price history. Refresh to load.")

        # Section Header: Analysis
        st.markdown(
            '<div class="section-header">ANALYSIS — OPPORTUNITIES</div>',
            unsafe_allow_html=True,
        )

        panel_col1, panel_col2 = st.columns(2)

        # Opportunity Leaderboard (left panel)
        with panel_col1:
            import pandas as pd

            st.markdown(
                '<div class="bordered-panel"><div class="panel-title">Opportunity Leaderboard</div>',
                unsafe_allow_html=True,
            )

            # Filter coins with opportunity scores
            scored_coins = [
                c for c in st.session_state.coin_data
                if c.get("opportunity_score") is not None
            ]

            if scored_coins:
                # Shared filters ABOVE tabs (persist when switching between Long/Short)
                all_sectors = list(set(c.get("sector", "Other") for c in scored_coins))
                all_sectors.sort()

                filter_col1, filter_col2, filter_col3 = st.columns(3)

                with filter_col1:
                    sector_filter = st.selectbox(
                        "Sector",
                        ["All"] + all_sectors,
                        key="opp_sector_shared",
                    )

                with filter_col2:
                    min_score = st.slider(
                        "Min Score",
                        min_value=0.0,
                        max_value=5.0,
                        value=0.0,
                        step=0.5,
                        key="opp_min_score_shared",
                    )

                with filter_col3:
                    max_age = st.slider(
                        "Max Age (days)",
                        min_value=1,
                        max_value=14,
                        value=14,
                        step=1,
                        key="opp_max_age_shared",
                    )

                # Signal direction tabs
                long_tab, short_tab = st.tabs(["Long (Oversold)", "Short (Overbought)"])

                for tab, direction, tab_name in [
                    (long_tab, "long", "Long"),
                    (short_tab, "short", "Short"),
                ]:
                    with tab:
                        # Filter by signal direction
                        direction_coins = [
                            c for c in scored_coins
                            if c.get("signal_direction") == direction
                        ]

                        if not direction_coins:
                            st.info(f"No {tab_name.lower()} signals currently.")
                            continue

                        # Apply filters
                        filtered_coins = direction_coins
                        if sector_filter != "All":
                            filtered_coins = [c for c in filtered_coins if c.get("sector") == sector_filter]

                        filtered_coins = [
                            c for c in filtered_coins
                            if c.get("opportunity_score", {}).get("final_score", 0) >= min_score
                        ]

                        # Filter by age (days_in_zone)
                        def get_days_in_zone(coin):
                            if direction == "long":
                                lc = coin.get("lifecycle_oversold")
                            else:
                                lc = coin.get("lifecycle_overbought")
                            return lc.get("days_in_zone", 0) if lc else 0

                        filtered_coins = [
                            c for c in filtered_coins
                            if get_days_in_zone(c) <= max_age or get_days_in_zone(c) == 0
                        ]

                        # Sort by final_score descending
                        filtered_coins.sort(
                            key=lambda c: c.get("opportunity_score", {}).get("final_score", 0),
                            reverse=True,
                        )

                        # Show all toggle
                        show_all = st.checkbox("Show all", value=False, key=f"opp_show_all_{direction}")
                        display_coins = filtered_coins if show_all else filtered_coins[:10]

                        if not display_coins:
                            st.info("No signals match the filters.")
                            continue

                        # Build table data
                        table_data = []
                        for rank, coin in enumerate(display_coins, 1):
                            opp = coin.get("opportunity_score", {})
                            factors = opp.get("factors", {})

                            # Build factor icons
                            factor_icons = []
                            if factors.get("weekly_extreme"):
                                factor_icons.append("📅")  # Weekly
                            if factors.get("divergence"):
                                factor_icons.append("📉")  # Divergence
                            if factors.get("volatility_compressed"):
                                factor_icons.append("⚡")  # Compressed
                            if factors.get("sector_turning"):
                                factor_icons.append("🔄")  # Sector
                            if factors.get("funding_aligned"):
                                factor_icons.append("💰")  # Funding
                            if factors.get("decorrelation_positive"):
                                factor_icons.append("🎯")  # Decorrelation

                            factors_str = " ".join(factor_icons) if factor_icons else "—"

                            table_data.append({
                                "Rank": rank,
                                "Symbol": coin.get("symbol", ""),
                                "Score": opp.get('final_score', 0),  # Numeric for ProgressColumn
                                "Factors": factors_str,
                            })

                        df = pd.DataFrame(table_data)
                        st.dataframe(
                            df,
                            column_config={
                                "Score": st.column_config.ProgressColumn(
                                    "Score",
                                    format="%.2f",
                                    min_value=0,
                                    max_value=5,
                                ),
                            },
                            hide_index=True,
                            use_container_width=True,
                        )

                        st.caption(f"Showing {len(display_coins)} of {len(filtered_coins)} signals")
            else:
                st.info("No opportunity scores available. Refresh to load data.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Sector Momentum (right panel)
        with panel_col2:
            import plotly.graph_objects as go
            import pandas as pd

            st.markdown(
                '<div class="bordered-panel"><div class="panel-title">Sector Momentum</div>',
                unsafe_allow_html=True,
            )

            # Build coin data for sector momentum calculation
            coins_for_momentum = []
            for coin in st.session_state.coin_data:
                if coin.get("daily_rsi") is not None and coin.get("id"):
                    coins_for_momentum.append({
                        "id": coin["id"],
                        "daily_rsi": coin["daily_rsi"],
                        "market_cap": coin.get("market_cap", 0),
                        "rsi_history": coin.get("rsi_history", []),
                    })

            sector_momentum = calculate_sector_momentum(coins_for_momentum)

            if sector_momentum:
                # Sort sectors by RSI (most oversold at top)
                sorted_sectors = sorted(
                    sector_momentum.items(),
                    key=lambda x: x[1]["current_rsi"]
                )

                # Build bar chart data
                sector_names = [s[0] for s in sorted_sectors]
                rsi_values = [s[1]["current_rsi"] for s in sorted_sectors]
                momentum_arrows = [s[1]["momentum_arrow"] for s in sorted_sectors]

                # Color based on RSI zone
                colors = []
                for rsi in rsi_values:
                    if rsi < 35:
                        colors.append("#4CAF50")  # Green - oversold
                    elif rsi > 65:
                        colors.append("#f44336")  # Red - overbought
                    else:
                        colors.append("#FFC107")  # Yellow - neutral

                # Create horizontal bar chart
                sector_fig = go.Figure()

                sector_fig.add_trace(go.Bar(
                    y=sector_names,
                    x=rsi_values,
                    orientation="h",
                    marker_color=colors,
                    text=[f"{arrow}" for arrow in momentum_arrows],
                    textposition="outside",
                    textfont=dict(size=14, color="#F6F8F7"),
                    hovertemplate="<b>%{y}</b><br>RSI: %{x:.1f}<extra></extra>",
                ))

                # Add vertical line at x=50 (neutral)
                sector_fig.add_vline(x=50, line_dash="dash", line_color="rgba(246, 248, 247, 0.3)", opacity=1)

                sector_fig.update_layout(
                    xaxis_title="RSI",
                    yaxis_title="",
                    xaxis=dict(
                        range=[0, 100],
                        title_font=dict(color="#F6F8F7"),
                        tickfont=dict(color="#F6F8F7"),
                        gridcolor="rgba(246, 248, 247, 0.08)",
                    ),
                    yaxis=dict(
                        tickfont=dict(color="#F6F8F7"),
                    ),
                    paper_bgcolor="#3E4253",
                    plot_bgcolor="rgba(74, 79, 94, 0.3)",
                    height=max(250, len(sector_names) * 35),
                    margin=dict(l=20, r=80, t=20, b=40),
                    showlegend=False,
                )

                st.plotly_chart(sector_fig, use_container_width=True)

                # Check for rotation signals
                rotation_sectors = [
                    name for name, data in sorted_sectors
                    if data.get("is_rotation_signal")
                ]
                if rotation_sectors:
                    st.info(f"🔄 **Rotation signals:** {', '.join(rotation_sectors)}")

                # Data table
                table_data = []
                for name, data in sorted_sectors:
                    change_str = f"{data['change_7d']:+.1f}" if data["change_7d"] is not None else "—"
                    table_data.append({
                        "Sector": name,
                        "RSI": f"{data['current_rsi']:.1f}",
                        "7D Δ": change_str,
                        "Mom": data["momentum_arrow"],
                    })

                df = pd.DataFrame(table_data)
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("No sector data available.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Section Header: Signals
        st.markdown(
            '<div class="section-header">SIGNALS — LIFECYCLE ANALYSIS</div>',
            unsafe_allow_html=True,
        )

        # Signal Lifecycle panel (always visible, no expander)
        st.markdown(
            '<div class="bordered-panel">',
            unsafe_allow_html=True,
        )

        # Filter coins with active lifecycle signals
        lifecycle_coins = []
        for coin in st.session_state.coin_data:
            lc_over = coin.get("lifecycle_oversold")
            lc_overbought = coin.get("lifecycle_overbought")
            vol = coin.get("volatility")
            price_chg = coin.get("price_change_pct")

            # Check if oversold signal is active
            if lc_over and lc_over.get("state") not in ("none", None):
                # Determine volatility emoji
                vol_regime = vol.get("regime") if vol else "normal"
                vol_emoji = "⚡" if vol_regime == "compressed" else ("🌊" if vol_regime == "expanded" else "➖")

                # Calculate conviction
                state = lc_over.get("state", "")
                is_fresh = state == "fresh"
                is_confirmed = state == "confirmed"
                is_compressed = vol_regime == "compressed"

                if is_fresh and is_compressed:
                    conviction = "⭐⭐⭐"  # Gold stars for highest conviction
                    conviction_sort = 3
                elif (is_confirmed and is_compressed) or (is_fresh and vol_regime == "normal"):
                    conviction = "⭐⭐☆"  # Two gold, one hollow
                    conviction_sort = 2
                else:
                    conviction = "⭐☆☆"  # One gold, two hollow
                    conviction_sort = 1

                lifecycle_coins.append({
                    "symbol": coin["symbol"],
                    "signal_type": "🟢 Oversold",
                    "stage": f"{lc_over.get('emoji', '')} {state.capitalize()}",
                    "days": lc_over.get("days_in_zone", 0),
                    "price_change": price_chg,
                    "volatility": vol_emoji,
                    "conviction": conviction,
                    "conviction_sort": conviction_sort,
                    "is_oversold": True,
                })

            # Check if overbought signal is active
            if lc_overbought and lc_overbought.get("state") not in ("none", None):
                vol_regime = vol.get("regime") if vol else "normal"
                vol_emoji = "⚡" if vol_regime == "compressed" else ("🌊" if vol_regime == "expanded" else "➖")

                state = lc_overbought.get("state", "")
                is_fresh = state == "fresh"
                is_confirmed = state == "confirmed"
                is_compressed = vol_regime == "compressed"

                if is_fresh and is_compressed:
                    conviction = "⭐⭐⭐"  # Gold stars for highest conviction
                    conviction_sort = 3
                elif (is_confirmed and is_compressed) or (is_fresh and vol_regime == "normal"):
                    conviction = "⭐⭐☆"  # Two gold, one hollow
                    conviction_sort = 2
                else:
                    conviction = "⭐☆☆"  # One gold, two hollow
                    conviction_sort = 1

                lifecycle_coins.append({
                    "symbol": coin["symbol"],
                    "signal_type": "🔴 Overbought",
                    "stage": f"{lc_overbought.get('emoji', '')} {state.capitalize()}",
                    "days": lc_overbought.get("days_in_zone", 0),
                    "price_change": price_chg,
                    "volatility": vol_emoji,
                    "conviction": conviction,
                    "conviction_sort": conviction_sort,
                    "is_oversold": False,
                })

        if lifecycle_coins:
            # Sort by conviction (highest first), then by days (ascending for fresh)
            lifecycle_coins.sort(key=lambda x: (-x["conviction_sort"], x["days"]))

            # Build display table
            import pandas as pd
            df_data = []
            for lc in lifecycle_coins:
                price_chg_str = f"{lc['price_change']:+.1f}%" if lc["price_change"] is not None else "—"
                df_data.append({
                    "Symbol": lc["symbol"],
                    "Signal": lc["signal_type"],
                    "Stage": lc["stage"],
                    "Days": lc["days"],
                    "Price Δ": price_chg_str,
                    "Vol": lc["volatility"],
                    "Conviction": lc["conviction"],
                })

            df = pd.DataFrame(df_data)
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No extreme RSI signals currently active.")

        # Legend explaining badges
        st.caption(
            "**Signal Stages:** 🆕 Fresh (1-2 days) | ✓ Confirmed (3-5 days) | ⏳ Extended (6+ days) | ↗↘ Resolving (exiting zone)  \n"
            "**Volatility:** ⚡ Compressed (coiled spring) | ➖ Normal | 🌊 Expanded (volatile)  \n"
            "**Conviction:** ⭐⭐⭐ Fresh + Compressed = Highest | ⭐⭐☆ Confirmed or Fresh + Normal | ⭐☆☆ Other"
        )

        # Close the lifecycle panel
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty state with context
    st.markdown("---")
    st.markdown(
        """
        ### How to use this screener

        This tool visualizes RSI (Relative Strength Index) signals across your crypto watchlist:

        - **X-axis:** Daily RSI (0-100) - below 30 is oversold, above 70 is overbought
        - **Y-axis:** Liquidity ratio (Volume / Market Cap) - higher means more active trading
        - **Color:** Weekly RSI - green is oversold, red is overbought

        The chart is divided into four quadrants to help you quickly identify market conditions.

        **Click "Refresh Data" above to load your watchlist.**
        """
    )
    st.caption(f"Tracking {len(coin_ids)} coins from watchlist.json")
