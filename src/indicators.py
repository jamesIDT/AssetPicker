"""Market indicator calculations for regime detection, acceleration, and volatility."""


def detect_regime(btc_weekly_rsi_history: list[float]) -> dict | None:
    """
    Detect market regime based on BTC weekly RSI trend and momentum.

    Args:
        btc_weekly_rsi_history: List of BTC weekly RSI values (oldest to newest, at least 4 values)

    Returns:
        Dict with keys:
        - state: "bull" | "bear" | "transition"
        - momentum: "rising" | "falling" | "neutral"
        - combined: "bull_rising" | "bull_falling" | "bear_rising" | "bear_falling" | "transition"
        Returns None if insufficient data (< 4 values).
    """
    if len(btc_weekly_rsi_history) < 4:
        return None

    current = btc_weekly_rsi_history[-1]
    prev_3 = btc_weekly_rsi_history[-4]

    # Check for transition (RSI crossed 50 within last 3 periods)
    recent_4 = btc_weekly_rsi_history[-4:]
    crossed_50 = False
    for i in range(1, len(recent_4)):
        if (recent_4[i - 1] <= 50 < recent_4[i]) or (recent_4[i - 1] > 50 >= recent_4[i]):
            crossed_50 = True
            break

    # Determine state
    if crossed_50:
        state = "transition"
    elif current > 50:
        state = "bull"
    else:
        state = "bear"

    # Determine momentum
    diff = current - prev_3
    if diff > 3:
        momentum = "rising"
    elif diff < -3:
        momentum = "falling"
    else:
        momentum = "neutral"

    # Combined state
    if state == "transition":
        combined = "transition"
    else:
        combined = f"{state}_{momentum}"

    return {
        "state": state,
        "momentum": momentum,
        "combined": combined,
    }


def calculate_rsi_acceleration(rsi_history: list[float]) -> dict | None:
    """
    Calculate RSI velocity and acceleration (second derivative).

    Args:
        rsi_history: List of RSI values over time (oldest to newest, at least 3 values)

    Returns:
        Dict with keys:
        - velocity: RSI change rate (current - previous)
        - acceleration: Change in velocity (current velocity - previous velocity)
        - interpretation: "accelerating_up" | "accelerating_down" | "decelerating_up" | "decelerating_down" | "stable"
        Returns None if insufficient data (< 3 values).
    """
    if len(rsi_history) < 3:
        return None

    velocity = rsi_history[-1] - rsi_history[-2]
    prev_velocity = rsi_history[-2] - rsi_history[-3]
    acceleration = velocity - prev_velocity

    # Determine interpretation
    if abs(velocity) < 1 and abs(acceleration) < 1:
        interpretation = "stable"
    elif velocity > 0 and acceleration > 0:
        interpretation = "accelerating_up"
    elif velocity > 0 and acceleration < 0:
        interpretation = "decelerating_up"
    elif velocity < 0 and acceleration < 0:
        interpretation = "accelerating_down"
    elif velocity < 0 and acceleration > 0:
        interpretation = "decelerating_down"
    else:
        # Edge case: velocity or acceleration is exactly 0
        interpretation = "stable"

    return {
        "velocity": velocity,
        "acceleration": acceleration,
        "interpretation": interpretation,
    }


def calculate_zscore(values: list[float], lookback: int = 90) -> dict | None:
    """
    Calculate z-score for statistical extreme detection.

    Args:
        values: List of values (e.g., RSI history), oldest to newest
        lookback: Number of periods for mean/std calculation (default: 90)

    Returns:
        Dict with keys:
        - current: Current value
        - mean: Rolling mean over lookback period
        - std: Rolling standard deviation
        - zscore: (current - mean) / std
        - extreme: "oversold" | "overbought" | "normal"
        Returns None if insufficient data (< 10 values).
    """
    if len(values) < 10:
        return None

    # Use all available values if less than lookback
    data = values[-lookback:] if len(values) >= lookback else values
    current = values[-1]

    # Calculate mean
    mean = sum(data) / len(data)

    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std = variance ** 0.5

    # Calculate z-score (handle zero std)
    if std == 0:
        zscore = 0.0
    else:
        zscore = (current - mean) / std

    # Classify extreme
    if zscore < -2.0:
        extreme = "oversold"
    elif zscore > 2.0:
        extreme = "overbought"
    else:
        extreme = "normal"

    return {
        "current": current,
        "mean": round(mean, 4),
        "std": round(std, 4),
        "zscore": round(zscore, 4),
        "extreme": extreme,
    }


def calculate_beta_adjusted_rsi(
    coin_returns: list[float],
    btc_returns: list[float],
    coin_rsi: float,
    btc_rsi: float,
) -> dict | None:
    """
    Calculate beta-adjusted relative strength vs BTC.

    Args:
        coin_returns: Daily % returns for coin (oldest to newest)
        btc_returns: Daily % returns for BTC (same period)
        coin_rsi: Current RSI of coin
        btc_rsi: Current RSI of BTC

    Returns:
        Dict with keys:
        - beta: Coin's beta to BTC (covariance / variance)
        - expected_rsi: What RSI we'd expect given BTC's RSI and beta
        - residual: coin_rsi - expected_rsi
        - interpretation: "outperforming" | "underperforming" | "expected"
        Returns None if insufficient data (< 30 values) or mismatched lengths.
    """
    if len(coin_returns) < 30 or len(btc_returns) < 30:
        return None
    if len(coin_returns) != len(btc_returns):
        return None

    n = len(coin_returns)

    # Calculate means
    mean_coin = sum(coin_returns) / n
    mean_btc = sum(btc_returns) / n

    # Calculate covariance and variance
    covariance = sum(
        (coin_returns[i] - mean_coin) * (btc_returns[i] - mean_btc) for i in range(n)
    ) / n
    variance_btc = sum((b - mean_btc) ** 2 for b in btc_returns) / n

    # Calculate beta (handle zero variance)
    if variance_btc == 0:
        beta = 1.0  # Default to market beta
    else:
        beta = covariance / variance_btc

    # Expected RSI based on BTC RSI and beta
    expected_rsi = 50 + beta * (btc_rsi - 50)

    # Residual: actual - expected
    residual = coin_rsi - expected_rsi

    # Interpretation
    if residual > 5:
        interpretation = "outperforming"
    elif residual < -5:
        interpretation = "underperforming"
    else:
        interpretation = "expected"

    return {
        "beta": round(beta, 4),
        "expected_rsi": round(expected_rsi, 4),
        "residual": round(residual, 4),
        "interpretation": interpretation,
    }


def calculate_mean_reversion_prob(
    rsi_history: list[float], current_rsi: float, lookback: int = 90
) -> dict | None:
    """
    Calculate mean reversion probability based on historical RSI behavior.

    Args:
        rsi_history: Historical RSI values (oldest to newest)
        current_rsi: Current RSI to evaluate
        lookback: How far back to analyze (default: 90)

    Returns:
        Dict with keys:
        - current_rsi: Input RSI
        - bucket: RSI range bucket (e.g., "25-30")
        - occurrences: How many times RSI was in this bucket
        - reversals: How many of those led to reversal toward 50 within 5 periods
        - probability: reversals / occurrences (0-1)
        - confidence: "high" | "medium" | "low" based on sample size
        Returns None if insufficient data (< 30 values).
    """
    if len(rsi_history) < 30:
        return None

    # Use lookback or all available
    data = rsi_history[-lookback:] if len(rsi_history) >= lookback else rsi_history

    # Determine bucket (5-point ranges)
    bucket_start = int(current_rsi // 5) * 5
    bucket_end = bucket_start + 5
    bucket = f"{bucket_start}-{bucket_end}"

    # Find all occurrences in history where RSI was in same bucket
    occurrences = 0
    reversals = 0

    for i in range(len(data) - 5):  # Need 5 periods ahead to check
        rsi = data[i]
        # Check if in same bucket
        if bucket_start <= rsi < bucket_end:
            occurrences += 1

            # Check for reversal in next 5 periods
            is_oversold = rsi < 50
            next_5 = data[i + 1 : i + 6]

            if is_oversold:
                # Reversal = any of next 5 values > current + 5 (moving toward 50)
                if any(v > rsi + 5 for v in next_5):
                    reversals += 1
            else:
                # Reversal = any of next 5 values < current - 5 (moving toward 50)
                if any(v < rsi - 5 for v in next_5):
                    reversals += 1

    # Calculate probability (handle zero occurrences)
    if occurrences == 0:
        probability = 0.0
    else:
        probability = reversals / occurrences

    # Determine confidence
    if occurrences >= 10:
        confidence = "high"
    elif occurrences >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "current_rsi": current_rsi,
        "bucket": bucket,
        "occurrences": occurrences,
        "reversals": reversals,
        "probability": round(probability, 4),
        "confidence": confidence,
    }


def detect_volatility_regime(
    price_history: list[float], period: int = 14
) -> dict | None:
    """
    Detect volatility regime based on ATR compression/expansion.

    Args:
        price_history: List of prices (oldest to newest)
        period: ATR period (default: 14)

    Returns:
        Dict with keys:
        - current_atr: Current ATR value (normalized as % of price)
        - avg_atr: Rolling average ATR over 4x period
        - ratio: current_atr / avg_atr
        - regime: "compressed" | "normal" | "expanded"
        Returns None if insufficient data (need 4*period + 1 prices).
    """
    min_required = 4 * period + 1
    if len(price_history) < min_required:
        return None

    # Calculate True Range for each day (simplified: abs(close[i] - close[i-1]))
    true_ranges = []
    for i in range(1, len(price_history)):
        tr = abs(price_history[i] - price_history[i - 1])
        true_ranges.append(tr)

    # Calculate ATR as SMA of TR over period
    def calculate_atr(tr_slice: list[float], price: float) -> float:
        """Calculate normalized ATR as percentage of price."""
        atr = sum(tr_slice) / len(tr_slice)
        return (atr / price) * 100 if price > 0 else 0

    # Current ATR (last `period` TRs)
    current_tr_slice = true_ranges[-period:]
    current_price = price_history[-1]
    current_atr = calculate_atr(current_tr_slice, current_price)

    # Average ATR over 4*period
    # We need to calculate ATR at each point over the last 4*period days
    # and then average those ATRs
    lookback = 4 * period
    atr_values = []
    for i in range(lookback):
        # Calculate ATR at position -(lookback - i)
        # tr index = price index - 1 (since TR starts at index 1)
        end_idx = len(true_ranges) - (lookback - 1 - i)
        start_idx = end_idx - period
        if start_idx >= 0:
            tr_slice = true_ranges[start_idx:end_idx]
            price_at_point = price_history[end_idx]  # +1 offset for price vs TR
            if len(tr_slice) == period:
                atr_values.append(calculate_atr(tr_slice, price_at_point))

    if not atr_values:
        return None

    avg_atr = sum(atr_values) / len(atr_values)

    # Calculate ratio
    ratio = current_atr / avg_atr if avg_atr > 0 else 1.0

    # Determine regime
    if ratio < 0.7:
        regime = "compressed"
    elif ratio > 1.3:
        regime = "expanded"
    else:
        regime = "normal"

    return {
        "current_atr": round(current_atr, 4),
        "avg_atr": round(avg_atr, 4),
        "ratio": round(ratio, 4),
        "regime": regime,
    }
