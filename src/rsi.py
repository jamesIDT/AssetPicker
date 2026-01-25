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


def aggregate_to_4h_closes(hourly_prices: list) -> list[float]:
    """
    Aggregate hourly price data to 4-hour closes.

    Args:
        hourly_prices: List of [timestamp_ms, price] pairs from CoinGecko

    Returns:
        List of closing prices for each 4-hour bucket (oldest to newest)
    """
    if not hourly_prices:
        return []

    # 4 hours in milliseconds
    bucket_size_ms = 4 * 60 * 60 * 1000

    # Group by 4-hour buckets using integer division
    buckets: dict[int, float] = {}
    for timestamp_ms, price in hourly_prices:
        bucket_key = timestamp_ms // bucket_size_ms
        # Keep overwriting - last price in bucket is the close
        buckets[bucket_key] = price

    # Sort by bucket and extract closes
    sorted_buckets = sorted(buckets.keys())
    return [buckets[bucket] for bucket in sorted_buckets]


def aggregate_to_12h_closes(hourly_prices: list) -> list[float]:
    """
    Aggregate hourly price data to 12-hour closes.

    Args:
        hourly_prices: List of [timestamp_ms, price] pairs from CoinGecko

    Returns:
        List of closing prices for each 12-hour bucket (oldest to newest)
    """
    if not hourly_prices:
        return []

    # 12 hours in milliseconds
    bucket_size_ms = 12 * 60 * 60 * 1000

    # Group by 12-hour buckets using integer division
    buckets: dict[int, float] = {}
    for timestamp_ms, price in hourly_prices:
        bucket_key = timestamp_ms // bucket_size_ms
        # Keep overwriting - last price in bucket is the close
        buckets[bucket_key] = price

    # Sort by bucket and extract closes
    sorted_buckets = sorted(buckets.keys())
    return [buckets[bucket] for bucket in sorted_buckets]


def aggregate_to_3d_closes(daily_prices: list) -> list[float]:
    """
    Aggregate daily price data to 3-day closes.

    Args:
        daily_prices: List of [timestamp_ms, price] pairs from CoinGecko

    Returns:
        List of closing prices for each 3-day bucket (oldest to newest)
    """
    if not daily_prices:
        return []

    # 3 days in milliseconds
    bucket_size_ms = 3 * 24 * 60 * 60 * 1000

    # Group by 3-day buckets using integer division
    buckets: dict[int, float] = {}
    for timestamp_ms, price in daily_prices:
        bucket_key = timestamp_ms // bucket_size_ms
        # Keep overwriting - last price in bucket is the close
        buckets[bucket_key] = price

    # Sort by bucket and extract closes
    sorted_buckets = sorted(buckets.keys())
    return [buckets[bucket] for bucket in sorted_buckets]


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
