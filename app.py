"""Crypto RSI Screener - Main Streamlit application."""

import asyncio
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from src.charts import build_acceleration_quadrant, build_rsi_scatter
from src.coingecko import CoinGeckoClient
from src.indicators import (
    calculate_beta_adjusted_rsi,
    calculate_divergence_score,
    calculate_opportunity_score,
    calculate_rsi_acceleration,
    calculate_zscore,
    classify_signal_lifecycle,
    detect_divergence,
    detect_regime,
    detect_volatility_regime,
)
from src.sectors import calculate_sector_momentum, calculate_sector_rsi, get_sector
from src.rsi import calculate_rsi, extract_closes, get_daily_rsi, get_weekly_rsi

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

    /* =================================================================
       CSS DESIGN TOKENS
       ================================================================= */
    :root {
        /* Background colors */
        --bg-0: #4A4A4A;           /* Primary background (dark gray) */
        --bg-1: #6D8196;           /* Slate blue for panels */
        --bg-2: #5A5A5A;           /* Slightly lighter gray for hover */

        /* Text colors */
        --text-0: #FFFFE3;         /* Cream primary text */
        --text-1: rgba(255, 255, 227, 0.72);  /* Secondary text */
        --text-2: rgba(255, 255, 227, 0.54);  /* Tertiary/muted text */

        /* Accent colors */
        --accent: #FFB020;         /* Yellow-orange hero color */
        --accent-2: #FFD38A;       /* Softer accent for hover */

        /* Panel/surface colors */
        --panel: rgba(109, 129, 150, 0.15);       /* Panel background */
        --panel-hover: rgba(109, 129, 150, 0.25); /* Panel hover */

        /* Borders and lines */
        --line: rgba(255, 255, 227, 0.12);        /* Subtle borders */
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

    /* Expander header/toggle */
    .streamlit-expanderHeader {
        color: var(--text-0) !important;
        font-weight: 500 !important;
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
       DATAFRAME / TABLE STYLING
       ================================================================= */
    [data-testid="stDataFrame"],
    .stDataFrame {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 2px !important;
    }

    /* Table headers */
    [data-testid="stDataFrame"] th,
    .stDataFrame th,
    [data-testid="stTable"] th {
        background-color: var(--bg-2) !important;
        color: var(--text-1) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        border-bottom: 1px solid var(--line) !important;
    }

    /* Table cells */
    [data-testid="stDataFrame"] td,
    .stDataFrame td,
    [data-testid="stTable"] td {
        color: var(--text-0) !important;
        border-bottom: 1px solid var(--line) !important;
    }

    /* Table row hover */
    [data-testid="stDataFrame"] tr:hover td,
    .stDataFrame tr:hover td,
    [data-testid="stTable"] tr:hover td {
        background-color: var(--panel-hover) !important;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "coin_data" not in st.session_state:
    st.session_state.coin_data = None
if "divergence_data" not in st.session_state:
    st.session_state.divergence_data = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
if "failed_coins" not in st.session_state:
    st.session_state.failed_coins = 0
if "btc_regime" not in st.session_state:
    st.session_state.btc_regime = None
if "btc_weekly_rsi" not in st.session_state:
    st.session_state.btc_weekly_rsi = None
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


async def fetch_all_data(coin_ids: list[str]) -> tuple[list[dict], list[dict], int, dict | None, float | None]:
    """
    Fetch market data and calculate RSI for all coins.

    Args:
        coin_ids: List of CoinGecko coin IDs

    Returns:
        Tuple of (coin data list, divergence data list, failed count, btc_regime, btc_weekly_rsi)
    """
    async with CoinGeckoClient() as client:
        # Fetch market data and history concurrently
        market_data = await client.get_coins_market_data(coin_ids)
        history = await client.get_coins_history(coin_ids, days=120)

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

        # Calculate beta-adjusted RSI
        beta_info = None
        prices = hist.get("prices", [])
        if len(prices) >= 2 and len(btc_returns) >= 30 and btc_daily_rsi is not None:
            coin_returns = []
            for i in range(1, len(prices)):
                prev_price = prices[i - 1][1]
                curr_price = prices[i][1]
                if prev_price > 0:
                    coin_returns.append((curr_price - prev_price) / prev_price)

            # Align lengths - use the shorter of the two
            min_len = min(len(coin_returns), len(btc_returns))
            if min_len >= 30:
                aligned_coin_returns = coin_returns[-min_len:]
                aligned_btc_returns = btc_returns[-min_len:]
                beta_info = calculate_beta_adjusted_rsi(
                    aligned_coin_returns, aligned_btc_returns, daily_rsi, btc_daily_rsi
                )

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
            "beta_info": beta_info,
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

    return result, divergence_result, failed_count, btc_regime, btc_weekly_rsi


# Main UI
st.title(f"Crypto RSI Screener")
st.caption("Data from CoinGecko Pro API")

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

# Refresh button - primary style
if st.button("Refresh Data", type="primary"):
    with st.spinner("Fetching data from CoinGecko..."):
        try:
            data, divergence_data, failed_count, btc_regime, btc_weekly_rsi = asyncio.run(fetch_all_data(coin_ids))
            st.session_state.coin_data = data
            st.session_state.divergence_data = divergence_data
            st.session_state.last_updated = datetime.now()
            st.session_state.failed_coins = failed_count
            st.session_state.btc_regime = btc_regime
            st.session_state.btc_weekly_rsi = btc_weekly_rsi
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

# Display chart or message
if st.session_state.coin_data is not None:
    # Display regime banner if available
    if st.session_state.btc_regime is not None:
        regime = st.session_state.btc_regime
        btc_rsi = st.session_state.btc_weekly_rsi
        combined = regime.get("combined", "transition")

        # Map regime to display properties (dark theme with colored accent borders)
        # Format: (emoji_label, momentum_label, bg_color, border_color)
        regime_display = {
            "bull_rising": ("🐂 Bull ↗", "Rising", "rgba(76, 175, 80, 0.15)", "#4CAF50"),
            "bull_falling": ("🐂 Bull ↘", "Cooling", "rgba(76, 175, 80, 0.10)", "#4CAF50"),
            "bull_neutral": ("🐂 Bull →", "Steady", "rgba(76, 175, 80, 0.10)", "#4CAF50"),
            "bear_rising": ("🐻 Bear ↗", "Recovering", "rgba(244, 67, 54, 0.10)", "#f44336"),
            "bear_falling": ("🐻 Bear ↘", "Falling", "rgba(244, 67, 54, 0.15)", "#f44336"),
            "bear_neutral": ("🐻 Bear →", "Steady", "rgba(244, 67, 54, 0.10)", "#f44336"),
            "transition": ("⚖️ Transition", "", "rgba(255, 176, 32, 0.12)", "#FFB020"),
        }

        emoji_label, momentum_label, bg_color, border_color = regime_display.get(
            combined, ("⚖️ Transition", "", "rgba(255, 176, 32, 0.12)", "#FFB020")
        )

        banner_text = emoji_label
        if momentum_label:
            banner_text += f" ({momentum_label})"
        if btc_rsi is not None:
            banner_text += f" | BTC Weekly RSI: {btc_rsi:.1f}"

        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                border-left: 3px solid {border_color};
                padding: 8px 16px;
                border-radius: 2px;
                margin-bottom: 12px;
                text-align: center;
                font-size: 1.1em;
                font-weight: 500;
                color: #FFFFE3;
            ">
                {banner_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Collapsible "How to Read This Dashboard" panel
    with st.expander("📖 How to Read This Dashboard", expanded=False):
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

    # Show timestamp with relative time and failed count
    if st.session_state.last_updated:
        relative = format_relative_time(st.session_state.last_updated)
        full_time = st.session_state.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        status_text = f"Updated {relative}"
        if st.session_state.failed_coins > 0:
            status_text += f" | {st.session_state.failed_coins} coin(s) unavailable"
        st.caption(f"{status_text} ({full_time})")

    # Handle empty data gracefully
    if not st.session_state.coin_data:
        st.warning("No valid coin data available. Check your watchlist configuration.")
    else:
        # Build sector options for filter dropdown
        sector_counts = {}
        for coin in st.session_state.coin_data:
            sector = coin.get("sector", "Other")
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        sector_options = ["All Sectors"] + [
            f"{sector} ({count})" for sector, count in sorted(sector_counts.items())
        ]

        # Sector filter dropdown
        col_filter, col_count = st.columns([3, 1])
        with col_filter:
            selected = st.selectbox(
                "Filter by Sector",
                sector_options,
                index=0,
                key="sector_filter",
            )
            # Extract sector name (remove count suffix)
            if selected == "All Sectors":
                st.session_state.selected_sector = "All Sectors"
            else:
                st.session_state.selected_sector = selected.split(" (")[0]

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

        with col_count:
            st.metric("Coins", len(filtered_coin_data))

        # Color mode toggle
        color_mode = st.radio(
            "Color Mode",
            ["Weekly RSI", "Beta Residual"],
            horizontal=True,
            help="Weekly RSI: Green=oversold, Red=overbought. Beta Residual: Green=outperforming BTC, Red=underperforming.",
        )

        # Z-score labels toggle
        show_zscore = st.checkbox(
            "Show Z-Score Labels",
            value=False,
            help="Display statistical z-score next to coin symbols for extreme readings (|z| > 1.5)",
        )

        # Extract beta residuals for beta mode
        beta_residuals = None
        if color_mode == "Beta Residual":
            beta_residuals = []
            for c in filtered_coin_data:
                beta_info = c.get("beta_info")
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

        # Hero Charts Row - RSI Scatter (65%) | Acceleration Quadrant (35%)
        chart_col1, chart_col2 = st.columns([0.65, 0.35])

        with chart_col1:
            # Build and display RSI Scatter chart
            fig = build_rsi_scatter(
                filtered_coin_data,
                filtered_divergence_data,
                beta_data=beta_residuals,
                color_mode="beta_residual" if color_mode == "Beta Residual" else "weekly_rsi",
                sector_data=sector_data,
                zscore_data=zscore_data,
                show_zscore=show_zscore,
            )
            st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

        with chart_col2:
            # Acceleration Quadrant
            st.markdown("### Acceleration Quadrant")
            # Filter coins with both acceleration and volatility data
            accel_coins = [
                c for c in st.session_state.coin_data
                if c.get("acceleration") is not None and c.get("volatility") is not None
            ]

            if accel_coins:
                accel_fig = build_acceleration_quadrant(accel_coins)
                st.plotly_chart(accel_fig, use_container_width=True)
                st.caption(
                    "**Bottom-right** (Accel + Compressed) = highest conviction."
                )
            else:
                st.info("Acceleration data requires price history. Refresh to load.")

        # Signal lists with star explanation
        st.markdown("---")
        st.caption("Coins at RSI extremes (below 30 or above 70). ⭐ = weekly RSI also at extreme.")

        # Gather data
        opportunities = [
            c for c in filtered_coin_data if c["daily_rsi"] < 30
        ]
        opportunities.sort(key=lambda c: c["daily_rsi"])

        caution = [
            c for c in filtered_coin_data if c["daily_rsi"] > 70
        ]
        caution.sort(key=lambda c: c["daily_rsi"], reverse=True)

        # Display in balanced columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Potential Opportunities ({len(opportunities)})")
            if opportunities:
                for coin in opportunities:
                    star = " ⭐" if coin["weekly_rsi"] < 30 else ""
                    st.write(
                        f"**{coin['symbol']}** - Daily: {coin['daily_rsi']:.1f} | "
                        f"Weekly: {coin['weekly_rsi']:.1f}{star}"
                    )
            else:
                st.markdown("_No oversold coins currently_")

        with col2:
            st.subheader(f"Exercise Caution ({len(caution)})")
            if caution:
                for coin in caution:
                    star = " ⭐" if coin["weekly_rsi"] > 70 else ""
                    st.write(
                        f"**{coin['symbol']}** - Daily: {coin['daily_rsi']:.1f} | "
                        f"Weekly: {coin['weekly_rsi']:.1f}{star}"
                    )
            else:
                st.markdown("_No overbought coins currently_")

        # Market Analysis Section - Visible panels (not expanders)
        st.markdown("---")
        st.subheader("Market Analysis")

        panel_col1, panel_col2 = st.columns(2)

        # Opportunity Leaderboard (left panel)
        with panel_col1:
            import pandas as pd

            st.markdown("### Opportunity Leaderboard")

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

        # Sector Momentum (right panel)
        with panel_col2:
            import plotly.graph_objects as go
            import pandas as pd

            st.markdown("### Sector Momentum")

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
                    textfont=dict(size=14, color="#FFFFE3"),
                    hovertemplate="<b>%{y}</b><br>RSI: %{x:.1f}<extra></extra>",
                ))

                # Add vertical line at x=50 (neutral)
                sector_fig.add_vline(x=50, line_dash="dash", line_color="rgba(255, 255, 227, 0.3)", opacity=1)

                sector_fig.update_layout(
                    xaxis_title="RSI",
                    yaxis_title="",
                    xaxis=dict(
                        range=[0, 100],
                        title_font=dict(color="#FFFFE3"),
                        tickfont=dict(color="#FFFFE3"),
                        gridcolor="rgba(255, 255, 227, 0.08)",
                    ),
                    yaxis=dict(
                        tickfont=dict(color="#FFFFE3"),
                    ),
                    paper_bgcolor="#4A4A4A",
                    plot_bgcolor="rgba(90, 90, 90, 0.3)",
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

        # Signal Lifecycle Analysis section (collapsed expander at bottom)
        st.markdown("---")
        with st.expander("Signal Lifecycle Analysis", expanded=False):
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
