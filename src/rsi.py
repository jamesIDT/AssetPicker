"""RSI calculation functions for daily and weekly timeframes."""

from datetime import datetime


def calculate_rsi(closes: list[float], period: int = 14) -> float | None:
    """
    Calculate RSI using Wilder's smoothed RSI formula.

    Args:
        closes: List of closing prices (oldest to newest)
        period: RSI period (default: 14)

    Returns:
        RSI value (0-100) or None if insufficient data
    """
    # Need period + 1 prices minimum to calculate first RSI
    if len(closes) < period + 1:
        return None

    # Calculate price changes (deltas)
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

    # Separate gains and losses
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # First average: simple mean of first `period` values
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Smoothed averages for remaining values (Wilder's smoothing)
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    # Calculate RS and RSI
    if avg_loss == 0:
        return 100.0  # No losses = RSI is 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def extract_closes(market_chart: dict) -> list[float]:
    """
    Extract closing prices from CoinGecko market_chart response.

    Args:
        market_chart: Dict with 'prices' key containing [[timestamp_ms, price], ...]

    Returns:
        List of closing prices (oldest to newest)
    """
    prices = market_chart.get("prices", [])
    return [price for _, price in prices]


def get_daily_rsi(market_chart: dict, period: int = 14) -> float | None:
    """
    Calculate daily RSI from CoinGecko market_chart data.

    Args:
        market_chart: CoinGecko market_chart response (from get_coin_market_chart)
        period: RSI period (default: 14)

    Returns:
        RSI value (0-100) or None if insufficient data
    """
    closes = extract_closes(market_chart)
    return calculate_rsi(closes, period)


def get_weekly_rsi(market_chart: dict, period: int = 14) -> float | None:
    """
    Calculate weekly RSI from CoinGecko daily market_chart data.

    Aggregates daily data to weekly closes (last close of each ISO week),
    then calculates RSI on the weekly data.

    Args:
        market_chart: CoinGecko market_chart response with daily data
        period: RSI period (default: 14)

    Returns:
        RSI value (0-100) or None if insufficient weekly data (need period+1 weeks)
    """
    prices = market_chart.get("prices", [])
    if not prices:
        return None

    # Group by ISO week (year, week_number)
    weekly_closes: dict[tuple[int, int], float] = {}

    for timestamp_ms, price in prices:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        iso = dt.isocalendar()
        week_key = (iso.year, iso.week)
        # Keep the most recent price for each week (dict overwrites)
        weekly_closes[week_key] = price

    # Sort by week and extract closes
    sorted_weeks = sorted(weekly_closes.keys())
    closes = [weekly_closes[week] for week in sorted_weeks]

    # Need at least period + 1 weekly data points
    if len(closes) < period + 1:
        return None

    return calculate_rsi(closes, period)
