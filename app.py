"""Crypto RSI Screener - Main Streamlit application."""

import asyncio
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from src.charts import build_rsi_scatter
from src.coingecko import CoinGeckoClient
from src.indicators import (
    calculate_beta_adjusted_rsi,
    calculate_divergence_score,
    calculate_zscore,
    classify_signal_lifecycle,
    detect_divergence,
    detect_regime,
    detect_volatility_regime,
)
from src.sectors import calculate_sector_rsi, get_sector
from src.rsi import calculate_rsi, extract_closes, get_daily_rsi, get_weekly_rsi

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
                "beta_info": beta_info,
                "lifecycle_oversold": lifecycle_oversold,
                "lifecycle_overbought": lifecycle_overbought,
                "volatility": volatility,
                "price_change_pct": price_change_pct,
            }
        )

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

    # Now add sector info, sector_rank, and zscore_info to each result coin
    # Build a lookup from symbol to result index for efficient update
    coin_id_to_result_idx = {}
    for i, coin_id in enumerate(coin_ids):
        if coin_id in market_lookup:
            symbol = market_lookup[coin_id].get("symbol", "").upper()
            # Find the result entry with this symbol
            for j, r in enumerate(result):
                if r["symbol"] == symbol:
                    coin_id_to_result_idx[coin_id] = j
                    break

    for coin_id, result_idx in coin_id_to_result_idx.items():
        sector = get_sector(coin_id)
        result[result_idx]["sector"] = sector
        result[result_idx]["id"] = coin_id

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

        # Calculate z-score using daily RSI history
        zscore_info = None
        if coin_id in history:
            hist = history[coin_id]
            daily_closes = extract_closes(hist)
            daily_rsi_history = get_rsi_history(daily_closes)
            if len(daily_rsi_history) >= 10:
                zscore_info = calculate_zscore(daily_rsi_history, lookback=90)

        result[result_idx]["zscore_info"] = zscore_info

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

        # Map regime to display properties
        regime_display = {
            "bull_rising": ("🐂 Bull ↗", "Rising", "#e8f5e9"),
            "bull_falling": ("🐂 Bull ↘", "Cooling", "#f1f8e9"),
            "bull_neutral": ("🐂 Bull →", "Steady", "#f1f8e9"),
            "bear_rising": ("🐻 Bear ↗", "Recovering", "#fff3e0"),
            "bear_falling": ("🐻 Bear ↘", "Falling", "#ffebee"),
            "bear_neutral": ("🐻 Bear →", "Steady", "#ffebee"),
            "transition": ("⚖️ Transition", "", "#fffde7"),
        }

        emoji_label, momentum_label, bg_color = regime_display.get(
            combined, ("⚖️ Transition", "", "#fffde7")
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
                padding: 8px 16px;
                border-radius: 4px;
                margin-bottom: 12px;
                text-align: center;
                font-size: 1.1em;
                font-weight: 500;
            ">
                {banner_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

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
            for c in st.session_state.coin_data:
                beta_info = c.get("beta_info")
                if beta_info is not None:
                    beta_residuals.append(beta_info.get("residual", 0))
                else:
                    beta_residuals.append(0)

        # Extract sector data for tooltips
        sector_data = []
        for c in st.session_state.coin_data:
            sector_data.append({
                "sector": c.get("sector", "Other"),
                "sector_rank": c.get("sector_rank"),
            })

        # Extract zscore data for labels and tooltips
        zscore_data = []
        for c in st.session_state.coin_data:
            zscore_data.append(c.get("zscore_info"))

        # Build and display chart - responsive square
        fig = build_rsi_scatter(
            st.session_state.coin_data,
            st.session_state.divergence_data,
            beta_data=beta_residuals,
            color_mode="beta_residual" if color_mode == "Beta Residual" else "weekly_rsi",
            sector_data=sector_data,
            zscore_data=zscore_data,
            show_zscore=show_zscore,
        )
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

        # Signal Lifecycle Analysis section
        with st.expander("📊 Signal Lifecycle Analysis", expanded=False):
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
                        conviction = "★★★"
                        conviction_sort = 3
                    elif (is_confirmed and is_compressed) or (is_fresh and vol_regime == "normal"):
                        conviction = "★★"
                        conviction_sort = 2
                    else:
                        conviction = "★"
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
                        conviction = "★★★"
                        conviction_sort = 3
                    elif (is_confirmed and is_compressed) or (is_fresh and vol_regime == "normal"):
                        conviction = "★★"
                        conviction_sort = 2
                    else:
                        conviction = "★"
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
                    # Color price change based on signal direction
                    # For oversold: positive price change is good (bouncing)
                    # For overbought: negative price change is good (correcting)
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
                "**Conviction:** ★★★ Fresh + Compressed = Highest conviction | ★★ Confirmed or Fresh + Normal | ★ Other"
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
