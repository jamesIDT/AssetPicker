"""Crypto RSI Screener - Main Streamlit application."""

import asyncio
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from src.charts import build_rsi_scatter
from src.coingecko import CoinGeckoClient
from src.rsi import get_daily_rsi, get_weekly_rsi

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Crypto RSI Screener", layout="wide")

# Custom CSS for chart container
st.markdown(
    """
    <style>
    /* Style the primary button */
    [data-testid="stButton"] button[kind="primary"] {
        background-color: #4CAF50;
        border-color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "coin_data" not in st.session_state:
    st.session_state.coin_data = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
if "failed_coins" not in st.session_state:
    st.session_state.failed_coins = 0


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


async def fetch_all_data(coin_ids: list[str]) -> tuple[list[dict], int]:
    """
    Fetch market data and calculate RSI for all coins.

    Args:
        coin_ids: List of CoinGecko coin IDs

    Returns:
        Tuple of (coin data list, failed count)
    """
    async with CoinGeckoClient() as client:
        # Fetch market data and history concurrently
        market_data = await client.get_coins_market_data(coin_ids)
        history = await client.get_coins_history(coin_ids, days=120)

    # Build lookup for market data
    market_lookup = {c["id"]: c for c in market_data}

    result = []
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

        result.append(
            {
                "symbol": market.get("symbol", "").upper(),
                "name": market.get("name", ""),
                "daily_rsi": daily_rsi,
                "weekly_rsi": weekly_rsi,
                "vol_mcap_ratio": vol_mcap_ratio,
                "price": market.get("current_price", 0),
                "volume": volume,
                "market_cap": mcap,
            }
        )

    return result, failed_count


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
            data, failed_count = asyncio.run(fetch_all_data(coin_ids))
            st.session_state.coin_data = data
            st.session_state.last_updated = datetime.now()
            st.session_state.failed_coins = failed_count
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")

# Display chart or message
if st.session_state.coin_data is not None:
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
        # Build and display chart - responsive square
        fig = build_rsi_scatter(st.session_state.coin_data)
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

        # Signal lists with star explanation
        st.markdown("---")
        st.caption("Coins at RSI extremes (below 30 or above 70). ⭐ = weekly RSI also at extreme.")

        # Gather data
        opportunities = [
            c for c in st.session_state.coin_data if c["daily_rsi"] < 30
        ]
        opportunities.sort(key=lambda c: c["daily_rsi"])

        caution = [
            c for c in st.session_state.coin_data if c["daily_rsi"] > 70
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
