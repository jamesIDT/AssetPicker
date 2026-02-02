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


def calculate_rsi_history(closes: list[float], period: int = 14) -> list[float]:
    """
    Calculate RSI history (all RSI values, not just the last one).

    Args:
        closes: List of closing prices (oldest to newest)
        period: RSI period (default: 14)

    Returns:
        List of RSI values from oldest to newest, or empty list if insufficient data
    """
    if len(closes) < period + 1:
        return []

    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # First average
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi_history = []

    # First RSI value
    if avg_loss == 0:
        rsi_history.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_history.append(100 - (100 / (1 + rs)))

    # Smoothed averages for remaining values
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi_history.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_history.append(100 - (100 / (1 + rs)))

    return rsi_history


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


def extract_volumes(market_chart: dict) -> list[float]:
    """
    Extract volume data from CoinGecko market_chart response.

    Args:
        market_chart: Dict with 'total_volumes' key containing [[timestamp_ms, volume], ...]

    Returns:
        List of volumes (oldest to newest)
    """
    volumes = market_chart.get("total_volumes", [])
    return [vol for _, vol in volumes]


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


def calculate_multi_tf_rsi(
    hourly_data: dict | None, daily_data: dict | None, period: int = 14
) -> dict[str, float]:
    """
    Calculate RSI for all 6 timeframes.

    Args:
        hourly_data: CoinGecko hourly data {"prices": [[ts_ms, price], ...]} or None
        daily_data: CoinGecko daily data {"prices": [[ts_ms, price], ...]} or None
        period: RSI period (default: 14)

    Returns:
        Dict with RSI values for available timeframes:
        {"1h": 45.2, "4h": 48.1, "12h": 52.3, "1d": 55.0, "3d": 58.2, "1w": 62.1}
        Omits timeframes with insufficient data.
    """
    result: dict[str, float] = {}

    # Hourly-based timeframes (1h, 4h, 12h)
    if hourly_data:
        hourly_prices = hourly_data.get("prices", [])

        if hourly_prices:
            # 1h RSI - direct from hourly closes
            hourly_closes = [price for _, price in hourly_prices]
            rsi_1h = calculate_rsi(hourly_closes, period)
            if rsi_1h is not None:
                result["1h"] = rsi_1h

            # 4h RSI - aggregated from hourly
            closes_4h = aggregate_to_4h_closes(hourly_prices)
            rsi_4h = calculate_rsi(closes_4h, period)
            if rsi_4h is not None:
                result["4h"] = rsi_4h

            # 12h RSI - aggregated from hourly
            closes_12h = aggregate_to_12h_closes(hourly_prices)
            rsi_12h = calculate_rsi(closes_12h, period)
            if rsi_12h is not None:
                result["12h"] = rsi_12h

    # Daily-based timeframes (1d, 3d, 1w)
    if daily_data:
        daily_prices = daily_data.get("prices", [])

        if daily_prices:
            # 1d RSI - direct from daily closes
            daily_closes = [price for _, price in daily_prices]
            rsi_1d = calculate_rsi(daily_closes, period)
            if rsi_1d is not None:
                result["1d"] = rsi_1d

            # 3d RSI - aggregated from daily
            closes_3d = aggregate_to_3d_closes(daily_prices)
            rsi_3d = calculate_rsi(closes_3d, period)
            if rsi_3d is not None:
                result["3d"] = rsi_3d

            # 1w RSI - use existing weekly aggregation pattern
            rsi_1w = get_weekly_rsi(daily_data, period)
            if rsi_1w is not None:
                result["1w"] = rsi_1w

    return result


def calculate_multi_tf_rsi_with_history(
    hourly_data: dict | None, daily_data: dict | None, period: int = 14
) -> dict[str, dict]:
    """
    Calculate RSI and RSI history for all 6 timeframes.

    Args:
        hourly_data: CoinGecko hourly data {"prices": [[ts_ms, price], ...]} or None
        daily_data: CoinGecko daily data {"prices": [[ts_ms, price], ...]} or None
        period: RSI period (default: 14)

    Returns:
        Dict with RSI value and history for available timeframes:
        {"1h": {"rsi": 45.2, "history": [...]}, "4h": {...}, ...}
        Omits timeframes with insufficient data.
    """
    result: dict[str, dict] = {}

    # Hourly-based timeframes (1h, 4h, 12h)
    if hourly_data:
        hourly_prices = hourly_data.get("prices", [])

        if hourly_prices:
            # 1h RSI
            hourly_closes = [price for _, price in hourly_prices]
            rsi_hist_1h = calculate_rsi_history(hourly_closes, period)
            if rsi_hist_1h:
                result["1h"] = {"rsi": rsi_hist_1h[-1], "history": rsi_hist_1h}

            # 4h RSI
            closes_4h = aggregate_to_4h_closes(hourly_prices)
            rsi_hist_4h = calculate_rsi_history(closes_4h, period)
            if rsi_hist_4h:
                result["4h"] = {"rsi": rsi_hist_4h[-1], "history": rsi_hist_4h}

            # 12h RSI
            closes_12h = aggregate_to_12h_closes(hourly_prices)
            rsi_hist_12h = calculate_rsi_history(closes_12h, period)
            if rsi_hist_12h:
                result["12h"] = {"rsi": rsi_hist_12h[-1], "history": rsi_hist_12h}

    # Daily-based timeframes (1d, 3d, 1w)
    if daily_data:
        daily_prices = daily_data.get("prices", [])

        if daily_prices:
            # 1d RSI
            daily_closes = [price for _, price in daily_prices]
            rsi_hist_1d = calculate_rsi_history(daily_closes, period)
            if rsi_hist_1d:
                result["1d"] = {"rsi": rsi_hist_1d[-1], "history": rsi_hist_1d}

            # 3d RSI
            closes_3d = aggregate_to_3d_closes(daily_prices)
            rsi_hist_3d = calculate_rsi_history(closes_3d, period)
            if rsi_hist_3d:
                result["3d"] = {"rsi": rsi_hist_3d[-1], "history": rsi_hist_3d}

            # 1w RSI - need to get weekly closes for history
            weekly_closes: dict[tuple[int, int], float] = {}
            for timestamp_ms, price in daily_prices:
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                iso = dt.isocalendar()
                week_key = (iso.year, iso.week)
                weekly_closes[week_key] = price
            sorted_weeks = sorted(weekly_closes.keys())
            closes_1w = [weekly_closes[week] for week in sorted_weeks]
            rsi_hist_1w = calculate_rsi_history(closes_1w, period)
            if rsi_hist_1w:
                result["1w"] = {"rsi": rsi_hist_1w[-1], "history": rsi_hist_1w}

    return result


def aggregate_to_4h_volumes(hourly_volumes: list) -> list[float]:
    """
    Aggregate hourly volume data to 4-hour totals.

    Args:
        hourly_volumes: List of [timestamp_ms, volume] pairs from CoinGecko

    Returns:
        List of total volumes for each 4-hour bucket (oldest to newest)
    """
    if not hourly_volumes:
        return []

    bucket_size_ms = 4 * 60 * 60 * 1000
    buckets: dict[int, float] = {}

    for timestamp_ms, volume in hourly_volumes:
        bucket_key = timestamp_ms // bucket_size_ms
        # Sum volumes within the bucket
        buckets[bucket_key] = buckets.get(bucket_key, 0) + volume

    sorted_buckets = sorted(buckets.keys())
    return [buckets[bucket] for bucket in sorted_buckets]


def aggregate_to_12h_volumes(hourly_volumes: list) -> list[float]:
    """
    Aggregate hourly volume data to 12-hour totals.

    Args:
        hourly_volumes: List of [timestamp_ms, volume] pairs from CoinGecko

    Returns:
        List of total volumes for each 12-hour bucket (oldest to newest)
    """
    if not hourly_volumes:
        return []

    bucket_size_ms = 12 * 60 * 60 * 1000
    buckets: dict[int, float] = {}

    for timestamp_ms, volume in hourly_volumes:
        bucket_key = timestamp_ms // bucket_size_ms
        buckets[bucket_key] = buckets.get(bucket_key, 0) + volume

    sorted_buckets = sorted(buckets.keys())
    return [buckets[bucket] for bucket in sorted_buckets]


def aggregate_to_3d_volumes(daily_volumes: list) -> list[float]:
    """
    Aggregate daily volume data to 3-day totals.

    Args:
        daily_volumes: List of [timestamp_ms, volume] pairs from CoinGecko

    Returns:
        List of total volumes for each 3-day bucket (oldest to newest)
    """
    if not daily_volumes:
        return []

    bucket_size_ms = 3 * 24 * 60 * 60 * 1000
    buckets: dict[int, float] = {}

    for timestamp_ms, volume in daily_volumes:
        bucket_key = timestamp_ms // bucket_size_ms
        buckets[bucket_key] = buckets.get(bucket_key, 0) + volume

    sorted_buckets = sorted(buckets.keys())
    return [buckets[bucket] for bucket in sorted_buckets]


def aggregate_to_weekly_volumes(daily_volumes: list) -> list[float]:
    """
    Aggregate daily volume data to weekly totals.

    Args:
        daily_volumes: List of [timestamp_ms, volume] pairs from CoinGecko

    Returns:
        List of total volumes for each week (oldest to newest)
    """
    if not daily_volumes:
        return []

    weekly_volumes: dict[tuple[int, int], float] = {}
    for timestamp_ms, volume in daily_volumes:
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        iso = dt.isocalendar()
        week_key = (iso.year, iso.week)
        weekly_volumes[week_key] = weekly_volumes.get(week_key, 0) + volume

    sorted_weeks = sorted(weekly_volumes.keys())
    return [weekly_volumes[week] for week in sorted_weeks]


def calculate_multi_tf_obv(
    hourly_data: dict | None, daily_data: dict | None
) -> dict[str, dict]:
    """
    Calculate OBV and OBV acceleration for all 6 timeframes.

    Args:
        hourly_data: CoinGecko hourly data {"prices": [...], "total_volumes": [...]} or None
        daily_data: CoinGecko daily data {"prices": [...], "total_volumes": [...]} or None

    Returns:
        Dict with OBV data for available timeframes:
        {"1h": {"obv": [...], "acceleration": {...}}, "4h": {...}, ...}
        Omits timeframes with insufficient data.
    """
    from src.indicators import calculate_obv, calculate_obv_acceleration

    result: dict[str, dict] = {}

    # Hourly-based timeframes (1h, 4h, 12h)
    if hourly_data:
        hourly_prices = hourly_data.get("prices", [])
        hourly_volumes = hourly_data.get("total_volumes", [])

        if hourly_prices and hourly_volumes:
            # 1h OBV
            closes_1h = [price for _, price in hourly_prices]
            volumes_1h = [vol for _, vol in hourly_volumes]
            if len(closes_1h) == len(volumes_1h) and len(closes_1h) >= 3:
                obv_1h = calculate_obv(closes_1h, volumes_1h)
                if len(obv_1h) >= 3:
                    accel_1h = calculate_obv_acceleration(obv_1h)
                    result["1h"] = {"obv": obv_1h[-30:], "acceleration": accel_1h}

            # 4h OBV
            closes_4h = aggregate_to_4h_closes(hourly_prices)
            volumes_4h = aggregate_to_4h_volumes(hourly_volumes)
            if len(closes_4h) == len(volumes_4h) and len(closes_4h) >= 3:
                obv_4h = calculate_obv(closes_4h, volumes_4h)
                if len(obv_4h) >= 3:
                    accel_4h = calculate_obv_acceleration(obv_4h)
                    result["4h"] = {"obv": obv_4h[-30:], "acceleration": accel_4h}

            # 12h OBV
            closes_12h = aggregate_to_12h_closes(hourly_prices)
            volumes_12h = aggregate_to_12h_volumes(hourly_volumes)
            if len(closes_12h) == len(volumes_12h) and len(closes_12h) >= 3:
                obv_12h = calculate_obv(closes_12h, volumes_12h)
                if len(obv_12h) >= 3:
                    accel_12h = calculate_obv_acceleration(obv_12h)
                    result["12h"] = {"obv": obv_12h[-30:], "acceleration": accel_12h}

    # Daily-based timeframes (1d, 3d, 1w)
    if daily_data:
        daily_prices = daily_data.get("prices", [])
        daily_volumes = daily_data.get("total_volumes", [])

        if daily_prices and daily_volumes:
            # 1d OBV
            closes_1d = [price for _, price in daily_prices]
            volumes_1d = [vol for _, vol in daily_volumes]
            if len(closes_1d) == len(volumes_1d) and len(closes_1d) >= 3:
                obv_1d = calculate_obv(closes_1d, volumes_1d)
                if len(obv_1d) >= 3:
                    accel_1d = calculate_obv_acceleration(obv_1d)
                    result["1d"] = {"obv": obv_1d[-30:], "acceleration": accel_1d}

            # 3d OBV
            closes_3d = aggregate_to_3d_closes(daily_prices)
            volumes_3d = aggregate_to_3d_volumes(daily_volumes)
            if len(closes_3d) == len(volumes_3d) and len(closes_3d) >= 3:
                obv_3d = calculate_obv(closes_3d, volumes_3d)
                if len(obv_3d) >= 3:
                    accel_3d = calculate_obv_acceleration(obv_3d)
                    result["3d"] = {"obv": obv_3d[-30:], "acceleration": accel_3d}

            # 1w OBV
            weekly_closes_data: dict[tuple[int, int], float] = {}
            for timestamp_ms, price in daily_prices:
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                iso = dt.isocalendar()
                week_key = (iso.year, iso.week)
                weekly_closes_data[week_key] = price

            weekly_volumes_data: dict[tuple[int, int], float] = {}
            for timestamp_ms, volume in daily_volumes:
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                iso = dt.isocalendar()
                week_key = (iso.year, iso.week)
                weekly_volumes_data[week_key] = weekly_volumes_data.get(week_key, 0) + volume

            sorted_weeks = sorted(weekly_closes_data.keys())
            closes_1w = [weekly_closes_data[week] for week in sorted_weeks]
            volumes_1w = [weekly_volumes_data.get(week, 0) for week in sorted_weeks]

            if len(closes_1w) == len(volumes_1w) and len(closes_1w) >= 3:
                obv_1w = calculate_obv(closes_1w, volumes_1w)
                if len(obv_1w) >= 3:
                    accel_1w = calculate_obv_acceleration(obv_1w)
                    result["1w"] = {"obv": obv_1w[-30:], "acceleration": accel_1w}

    return result
