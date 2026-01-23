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

# Initialize session state
if "coin_data" not in st.session_state:
    st.session_state.coin_data = None
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None


def load_watchlist() -> list[dict]:
    """Load watchlist from JSON file."""
    with open("watchlist.json") as f:
        data = json.load(f)
    return data.get("coins", [])


async def fetch_all_data(coin_ids: list[str]) -> list[dict]:
    """
    Fetch market data and calculate RSI for all coins.

    Args:
        coin_ids: List of CoinGecko coin IDs

    Returns:
        List of coin data dicts ready for charting
    """
    async with CoinGeckoClient() as client:
        # Fetch market data and history concurrently
        market_data = await client.get_coins_market_data(coin_ids)
        history = await client.get_coins_history(coin_ids, days=90)

    # Build lookup for market data
    market_lookup = {c["id"]: c for c in market_data}

    result = []
    for coin_id in coin_ids:
        if coin_id not in market_lookup or coin_id not in history:
            continue

        market = market_lookup[coin_id]
        hist = history[coin_id]

        # Calculate RSI values
        daily_rsi = get_daily_rsi(hist)
        weekly_rsi = get_weekly_rsi(hist)

        # Skip if RSI couldn't be calculated
        if daily_rsi is None or weekly_rsi is None:
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

    return result


# Main UI
st.title("Crypto RSI Screener")

# Load watchlist
watchlist = load_watchlist()
coin_ids = [c["id"] for c in watchlist]

# Refresh button
if st.button("Refresh Data"):
    try:
        data = asyncio.run(fetch_all_data(coin_ids))
        st.session_state.coin_data = data
        st.session_state.last_updated = datetime.now()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")

# Display chart or message
if st.session_state.coin_data is not None:
    fig = build_rsi_scatter(st.session_state.coin_data)
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.last_updated:
        st.text(f"Last updated: {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.info("Click Refresh to load data")
