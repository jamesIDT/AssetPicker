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

    # Compute ratio history (each point's ATR / overall avg) for coil timeline
    ratio_history = [round(v / avg_atr, 4) if avg_atr > 0 else 1.0 for v in atr_values[-14:]]

    return {
        "current_atr": round(current_atr, 4),
        "avg_atr": round(avg_atr, 4),
        "ratio": round(ratio, 4),
        "regime": regime,
        "volatility_history": ratio_history,  # Last 14 days as ratio values for coil timeline
    }


def detect_divergence(
    price_history: list[float], rsi_history: list[float], lookback: int = 14
) -> dict | None:
    """
    Detect bullish or bearish divergence between price and RSI.

    Args:
        price_history: Recent prices (oldest to newest)
        rsi_history: Corresponding RSI values
        lookback: Period to check for divergence

    Returns:
        Dict with keys:
        - type: "bullish" | "bearish" | "none"
        - strength: 1 | 2 (1 = weak divergence, 2 = strong divergence)
        - description: Human-readable description
        Returns None if insufficient data.
    """
    if len(price_history) < lookback or len(rsi_history) < lookback:
        return None
    if len(price_history) != len(rsi_history):
        return None

    # Use last `lookback` values
    prices = price_history[-lookback:]
    rsis = rsi_history[-lookback:]

    # Find local extremes (lows for bullish, highs for bearish)
    # We need at least 2 extremes to detect divergence

    def find_local_lows(values: list[float]) -> list[tuple[int, float]]:
        """Find local minima indices and values."""
        lows = []
        for i in range(1, len(values) - 1):
            if values[i] < values[i - 1] and values[i] <= values[i + 1]:
                lows.append((i, values[i]))
        # Also check endpoints
        if len(values) >= 2:
            if values[0] < values[1]:
                lows.insert(0, (0, values[0]))
            if values[-1] < values[-2]:
                lows.append((len(values) - 1, values[-1]))
        return lows

    def find_local_highs(values: list[float]) -> list[tuple[int, float]]:
        """Find local maxima indices and values."""
        highs = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i - 1] and values[i] >= values[i + 1]:
                highs.append((i, values[i]))
        # Also check endpoints
        if len(values) >= 2:
            if values[0] > values[1]:
                highs.insert(0, (0, values[0]))
            if values[-1] > values[-2]:
                highs.append((len(values) - 1, values[-1]))
        return highs

    # Check for bullish divergence: price lower low, RSI higher low
    price_lows = find_local_lows(prices)
    if len(price_lows) >= 2:
        # Get two most significant lows (first and last in lookback)
        first_low = price_lows[0]
        last_low = price_lows[-1]

        # Price makes lower low
        if last_low[1] < first_low[1]:
            # Check RSI at same indices
            first_rsi = rsis[first_low[0]]
            last_rsi = rsis[last_low[0]]

            # RSI makes higher low (divergence)
            if last_rsi > first_rsi:
                rsi_diff = last_rsi - first_rsi
                strength = 2 if rsi_diff >= 5 else 1
                return {
                    "type": "bullish",
                    "strength": strength,
                    "description": f"Bullish divergence: price lower low, RSI higher low (+{rsi_diff:.1f})",
                }

    # Check for bearish divergence: price higher high, RSI lower high
    price_highs = find_local_highs(prices)
    if len(price_highs) >= 2:
        first_high = price_highs[0]
        last_high = price_highs[-1]

        # Price makes higher high
        if last_high[1] > first_high[1]:
            # Check RSI at same indices
            first_rsi = rsis[first_high[0]]
            last_rsi = rsis[last_high[0]]

            # RSI makes lower high (divergence)
            if last_rsi < first_rsi:
                rsi_diff = first_rsi - last_rsi
                strength = 2 if rsi_diff >= 5 else 1
                return {
                    "type": "bearish",
                    "strength": strength,
                    "description": f"Bearish divergence: price higher high, RSI lower high (-{rsi_diff:.1f})",
                }

    return {
        "type": "none",
        "strength": 0,
        "description": "No divergence detected",
    }


def classify_signal_lifecycle(
    rsi_history: list[float], extreme_threshold: float = 30.0, is_oversold: bool = True
) -> dict | None:
    """
    Classify signal lifecycle state based on RSI behavior in extreme zones.

    Args:
        rsi_history: RSI values (oldest to newest, at least 5 values)
        extreme_threshold: RSI level for extreme (30 for oversold, 70 for overbought)
        is_oversold: True for oversold signals, False for overbought

    Returns:
        Dict with keys:
        - state: "fresh" | "confirmed" | "extended" | "resolving" | "none"
        - days_in_zone: How many consecutive periods in extreme zone
        - entry_rsi: RSI when signal started
        - current_rsi: Current RSI
        - emoji: State emoji for UI display
        Returns None if insufficient history (< 5 values).
    """
    if len(rsi_history) < 5:
        return None

    current_rsi = rsi_history[-1]

    # Check if current RSI is in extreme zone
    def is_extreme(rsi: float) -> bool:
        if is_oversold:
            return rsi < extreme_threshold
        else:
            return rsi > extreme_threshold

    # Count consecutive days in extreme zone from the end
    days_in_zone = 0
    entry_rsi = current_rsi

    for i in range(len(rsi_history) - 1, -1, -1):
        if is_extreme(rsi_history[i]):
            days_in_zone += 1
            entry_rsi = rsi_history[i]
        else:
            break

    # Check for resolving state: was in zone but now moving toward 50
    # Crossed back within last 2 periods
    is_resolving = False
    if days_in_zone == 0 and len(rsi_history) >= 2:
        # Check if we were in zone 1 or 2 periods ago
        if is_extreme(rsi_history[-2]) or (
            len(rsi_history) >= 3 and is_extreme(rsi_history[-3])
        ):
            # Now moving toward 50
            if is_oversold:
                if current_rsi > rsi_history[-2]:
                    is_resolving = True
            else:
                if current_rsi < rsi_history[-2]:
                    is_resolving = True

    # Classify state
    if is_resolving:
        state = "resolving"
        # For resolving, find the entry RSI from recent extreme
        for i in range(len(rsi_history) - 2, -1, -1):
            if is_extreme(rsi_history[i]):
                entry_rsi = rsi_history[i]
                break
    elif days_in_zone == 0:
        state = "none"
    elif days_in_zone <= 2:
        state = "fresh"
    elif days_in_zone <= 5:
        state = "confirmed"
    else:
        state = "extended"

    # Emoji mapping
    emoji_map = {
        "fresh": "🆕",
        "confirmed": "✓",
        "extended": "⏳",
        "resolving": "↗" if is_oversold else "↘",
        "none": "",
    }

    return {
        "state": state,
        "days_in_zone": days_in_zone,
        "entry_rsi": round(entry_rsi, 2),
        "current_rsi": round(current_rsi, 2),
        "emoji": emoji_map[state],
    }


def calculate_divergence_score(
    daily_divergence: dict | None, weekly_divergence: dict | None
) -> int:
    """
    Calculate multi-timeframe divergence score.

    Args:
        daily_divergence: Result from detect_divergence for daily timeframe
        weekly_divergence: Result from detect_divergence for weekly timeframe

    Returns:
        Score based on divergence confluence:
        - 0: No divergence on either timeframe
        - 1: Single timeframe divergence (strength 1)
        - 2: Single timeframe divergence (strength 2)
        - 4: Both timeframes show divergence
    """
    # Check if we have valid divergences (not "none" type)
    daily_has = (
        daily_divergence is not None and daily_divergence.get("type") != "none"
    )
    weekly_has = (
        weekly_divergence is not None and weekly_divergence.get("type") != "none"
    )

    # Both timeframes = highest score
    if daily_has and weekly_has:
        return 4

    # Single timeframe - score based on strength
    if daily_has:
        return daily_divergence.get("strength", 1)
    if weekly_has:
        return weekly_divergence.get("strength", 1)

    # No divergence
    return 0


def detect_funding_confluence(
    daily_rsi: float, funding_rate: float | None
) -> dict:
    """
    Detect confluence between RSI extremes and funding rate direction.

    Args:
        daily_rsi: Daily RSI value
        funding_rate: Funding rate as decimal (can be None)

    Returns:
        Dict with:
        - aligned: bool (True if funding confirms RSI signal)
        - type: "bullish" | "bearish" | None
        - strength: "strong" | "moderate" | "weak" | None
    """
    if funding_rate is None:
        return {"aligned": False, "type": None, "strength": None}

    aligned = False
    conf_type: str | None = None
    strength: str | None = None

    # Bullish: RSI oversold (< 30) AND funding negative (shorts paying longs)
    if daily_rsi < 30 and funding_rate < 0:
        aligned = True
        conf_type = "bullish"
    # Bearish: RSI overbought (> 70) AND funding positive (longs paying shorts)
    elif daily_rsi > 70 and funding_rate > 0:
        aligned = True
        conf_type = "bearish"

    # Determine strength based on funding intensity
    if aligned:
        abs_funding = abs(funding_rate)
        if abs_funding > 0.0005:
            strength = "strong"
        elif abs_funding > 0.0002:
            strength = "moderate"
        else:
            strength = "weak"

    return {"aligned": aligned, "type": conf_type, "strength": strength}


def get_confluence_factors(
    daily_rsi: float,
    weekly_rsi: float | None,
    funding_rate: float | None,
    has_divergence: bool = False,
    volatility_compressed: bool = False,
    sector_turning: bool = False,
) -> dict:
    """
    Aggregate all confluence factors for opportunity scoring.

    Args:
        daily_rsi: Current daily RSI
        weekly_rsi: Current weekly RSI (can be None)
        funding_rate: Funding rate as decimal (can be None)
        has_divergence: True if divergence detected
        volatility_compressed: True if volatility regime is compressed
        sector_turning: True if sector RSI is turning

    Returns:
        Dict matching calculate_opportunity_score expected inputs:
        - weekly_extreme: bool
        - divergence: bool
        - funding_aligned: bool
        - volatility_compressed: bool
        - sector_turning: bool
    """
    # Weekly extreme check
    weekly_extreme = False
    if weekly_rsi is not None:
        weekly_extreme = weekly_rsi < 30 or weekly_rsi > 70

    # Funding alignment check
    funding_conf = detect_funding_confluence(daily_rsi, funding_rate)

    return {
        "weekly_extreme": weekly_extreme,
        "divergence": has_divergence,
        "funding_aligned": funding_conf["aligned"],
        "volatility_compressed": volatility_compressed,
        "sector_turning": sector_turning,
    }


def calculate_opportunity_score(factors: dict) -> dict:
    """
    Calculate composite opportunity score with decay and confluence factors.

    Args:
        factors: Dict with optional keys (missing factors = neutral contribution):
        - zscore: Z-score of RSI (from calculate_zscore)
        - days_in_zone: Days signal has been active
        - weekly_extreme: True if weekly RSI also in extreme
        - divergence_score: 0/1/2/4 from calculate_divergence_score
        - volatility_compressed: True if volatility regime is "compressed"
        - sector_turning: True if sector RSI is turning
        - funding_aligned: True if funding rate aligns with signal
        - decorrelation_positive: True if coin decorrelated favorably from BTC

    Returns:
        Dict with keys:
        - base_score: abs(zscore) or 1.0 if no zscore
        - freshness_multiplier: 1.0 to 0.3 based on days_in_zone
        - confluence_multiplier: 1.0 + sum of factor bonuses
        - final_score: base * freshness * confluence
        - factors: Dict showing contribution of each factor
    """
    # Base score from z-score
    zscore = factors.get("zscore", 0)
    base_score = abs(zscore) if zscore != 0 else 1.0

    # Freshness decay based on days in zone
    days = factors.get("days_in_zone", 0)
    if days <= 2:
        freshness = 1.0
    elif days <= 6:
        freshness = 0.8
    elif days <= 10:
        freshness = 0.6
    elif days <= 13:
        freshness = 0.4
    else:
        freshness = 0.3

    # Confluence multiplier - accumulate bonuses
    factor_contributions = {}
    confluence = 1.0

    # Weekly extreme: +0.2
    if factors.get("weekly_extreme", False):
        confluence += 0.2
        factor_contributions["weekly_extreme"] = 0.2

    # Divergence score: 1-2 → +0.3, 4 → +0.5
    divergence = factors.get("divergence_score", 0)
    if divergence >= 4:
        confluence += 0.5
        factor_contributions["divergence"] = 0.5
    elif divergence >= 1:
        confluence += 0.3
        factor_contributions["divergence"] = 0.3

    # Volatility compressed: +0.2
    if factors.get("volatility_compressed", False):
        confluence += 0.2
        factor_contributions["volatility_compressed"] = 0.2

    # Sector turning: +0.1
    if factors.get("sector_turning", False):
        confluence += 0.1
        factor_contributions["sector_turning"] = 0.1

    # Funding aligned: +0.2
    if factors.get("funding_aligned", False):
        confluence += 0.2
        factor_contributions["funding_aligned"] = 0.2

    # Decorrelation positive: +0.2
    if factors.get("decorrelation_positive", False):
        confluence += 0.2
        factor_contributions["decorrelation_positive"] = 0.2

    # Calculate final score
    final_score = base_score * freshness * confluence

    return {
        "base_score": round(base_score, 4),
        "freshness_multiplier": freshness,
        "confluence_multiplier": round(confluence, 2),
        "final_score": round(final_score, 4),
        "factors": factor_contributions,
    }


def calculate_price_acceleration(price_history: list[float]) -> dict | None:
    """
    Calculate price velocity and acceleration (second derivative).

    Args:
        price_history: List of price values over time (oldest to newest, at least 3 values)

    Returns:
        Dict with keys:
        - velocity: Price change rate as percent (current vs previous)
        - acceleration: Change in velocity (current velocity - previous velocity)
        - pct_change_3d: Total percent change over 3 periods
        Returns None if insufficient data (< 3 values).
    """
    if len(price_history) < 3:
        return None

    # Velocity = percent change from previous period
    if price_history[-2] == 0:
        return None
    velocity = (price_history[-1] - price_history[-2]) / price_history[-2] * 100

    # Previous velocity = percent change from 2 periods ago to 1 period ago
    if price_history[-3] == 0:
        return None
    prev_velocity = (price_history[-2] - price_history[-3]) / price_history[-3] * 100

    # Acceleration = change in velocity
    acceleration = velocity - prev_velocity

    # 3-period percent change
    if price_history[-3] == 0:
        return None
    pct_change_3d = (price_history[-1] - price_history[-3]) / price_history[-3] * 100

    return {
        "velocity": round(velocity, 4),
        "acceleration": round(acceleration, 4),
        "pct_change_3d": round(pct_change_3d, 4),
    }


def calculate_obv(prices: list[float], volumes: list[float]) -> list[float]:
    """
    Calculate On-Balance Volume (OBV) series.

    OBV is a cumulative indicator that adds volume on up-closes and subtracts
    volume on down-closes. It serves as a proxy for order flow / accumulation.

    Args:
        prices: List of closing prices (oldest to newest)
        volumes: List of volumes corresponding to each price (same length)

    Returns:
        List of OBV values (same length as input, first value is 0)
        Returns empty list if inputs are invalid or mismatched.
    """
    if len(prices) != len(volumes) or len(prices) < 2:
        return []

    obv = [0.0]
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            # Up day: add volume
            obv.append(obv[-1] + volumes[i])
        elif prices[i] < prices[i - 1]:
            # Down day: subtract volume
            obv.append(obv[-1] - volumes[i])
        else:
            # Unchanged: OBV stays the same
            obv.append(obv[-1])

    return obv


def calculate_obv_acceleration(obv_history: list[float]) -> dict | None:
    """
    Calculate OBV velocity and acceleration (second derivative).

    This measures whether volume conviction is building or waning.
    Positive acceleration = volume increasingly flowing in on up days.
    Negative acceleration = volume increasingly flowing in on down days.

    Args:
        obv_history: List of OBV values over time (oldest to newest, at least 3 values)

    Returns:
        Dict with keys:
        - velocity: OBV change rate (current - previous), normalized
        - acceleration: Change in velocity (current velocity - previous velocity)
        - interpretation: "accumulating" | "distributing" | "stable"
        Returns None if insufficient data (< 3 values).
    """
    if len(obv_history) < 3:
        return None

    # Calculate raw velocity (change in OBV)
    velocity = obv_history[-1] - obv_history[-2]
    prev_velocity = obv_history[-2] - obv_history[-3]
    acceleration = velocity - prev_velocity

    # Normalize velocity to a percentage of recent OBV range for comparability
    # Use the range over the last 10 periods (or available data) as denominator
    lookback = min(10, len(obv_history))
    recent_obv = obv_history[-lookback:]
    obv_range = max(recent_obv) - min(recent_obv)

    if obv_range > 0:
        normalized_velocity = (velocity / obv_range) * 100
        normalized_acceleration = (acceleration / obv_range) * 100
    else:
        normalized_velocity = 0.0
        normalized_acceleration = 0.0

    # Determine interpretation based on normalized values
    if abs(normalized_velocity) < 2 and abs(normalized_acceleration) < 2:
        interpretation = "stable"
    elif normalized_acceleration > 2:
        interpretation = "accumulating"  # Volume conviction building on up days
    elif normalized_acceleration < -2:
        interpretation = "distributing"  # Volume conviction building on down days
    else:
        interpretation = "stable"

    return {
        "velocity": round(normalized_velocity, 4),
        "acceleration": round(normalized_acceleration, 4),
        "raw_velocity": velocity,
        "raw_acceleration": acceleration,
        "interpretation": interpretation,
    }


def calculate_signal_persistence(
    rsi_history: list[float], price_history: list[float], threshold: float = 0.5
) -> dict | None:
    """
    Calculate signal persistence - tracking how long RSI has been leading price.

    This identifies "coiled springs" where the RSI-leading-price pattern has
    persisted over multiple periods, indicating building pressure.

    Args:
        rsi_history: List of RSI values (oldest to newest, at least 5 values)
        price_history: List of price values (oldest to newest, at least 5 values)
        threshold: Gap score threshold to consider RSI leading (default: 0.5)

    Returns:
        Dict with keys:
        - current_gap: Current gap score (latest RSI_accel - Price_accel)
        - persistence: Total periods (out of 5) with gap > threshold (0-5)
        - avg_gap: Average gap score over persistent periods
        - interpretation: "strong_coiled" | "building" | "weak" | "none"
        Returns None if insufficient data (< 5 values for either history).
    """
    if len(rsi_history) < 5 or len(price_history) < 5:
        return None

    # Calculate gap scores for recent periods
    # We need at least 3 values to calculate acceleration, so we can compute
    # gap scores for positions -5 to -1 (relative to end)
    gap_scores = []

    # For each period from -5 to -1, calculate the gap score at that point
    # We need i, i-1, i-2 values for acceleration calculation
    for offset in range(-5, 0):
        # Get slices ending at this offset
        # offset = -5 means we use indices ending at -5 (exclusive would be -4)
        rsi_slice = rsi_history[offset - 2 : offset + 1] if offset != -1 else rsi_history[offset - 2:]
        price_slice = price_history[offset - 2 : offset + 1] if offset != -1 else price_history[offset - 2:]

        if len(rsi_slice) < 3 or len(price_slice) < 3:
            continue

        # Calculate RSI acceleration at this point
        rsi_velocity = rsi_slice[-1] - rsi_slice[-2]
        rsi_prev_velocity = rsi_slice[-2] - rsi_slice[-3]
        rsi_accel = rsi_velocity - rsi_prev_velocity

        # Calculate price acceleration at this point (as percentage)
        if price_slice[-2] == 0 or price_slice[-3] == 0:
            continue
        price_velocity = (price_slice[-1] - price_slice[-2]) / price_slice[-2] * 100
        price_prev_velocity = (price_slice[-2] - price_slice[-3]) / price_slice[-3] * 100
        price_accel = price_velocity - price_prev_velocity

        # Gap score: RSI acceleration - Price acceleration
        # Positive = RSI leading price (bullish)
        gap_score = rsi_accel - price_accel
        gap_scores.append(gap_score)

    if not gap_scores:
        return None

    # Current gap is the most recent gap score
    current_gap = gap_scores[-1]

    # Count total periods (out of last 5) where gap > threshold
    # More forgiving than consecutive - allows temporary dips
    persistence = 0
    persistent_gaps = []
    for gap in gap_scores:
        if gap > threshold:
            persistence += 1
            persistent_gaps.append(gap)

    # Calculate average gap over persistent periods
    avg_gap = sum(persistent_gaps) / len(persistent_gaps) if persistent_gaps else 0.0

    # Determine interpretation based on total count (0-5 periods)
    # With lower threshold (0.5) and total count, we expect more spread
    if persistence >= 4 and current_gap > 2:
        interpretation = "strong_coiled"
    elif persistence >= 3 or current_gap > 2:
        interpretation = "building"
    elif persistence >= 2 or current_gap > 0.5:
        interpretation = "weak"
    else:
        interpretation = "none"

    return {
        "current_gap": round(current_gap, 4),
        "persistence": persistence,
        "avg_gap": round(avg_gap, 4),
        "interpretation": interpretation,
        "gap_history": [round(g, 4) for g in gap_scores],  # 5-period history for maturity ladder
    }


def calculate_multi_tf_divergence(
    hourly_data: dict | None,
    daily_data: dict | None,
    multi_tf_rsi: dict[str, float],
    lookback: int = 14,
) -> dict[str, dict]:
    """
    Calculate divergence signals for all 6 timeframes.

    Args:
        hourly_data: CoinGecko hourly data {"prices": [[ts_ms, price], ...]} or None
        daily_data: CoinGecko daily data {"prices": [[ts_ms, price], ...]} or None
        multi_tf_rsi: Dict of RSI values per timeframe from calculate_multi_tf_rsi
        lookback: Number of periods to check for divergence (default: 14)

    Returns:
        Dict keyed by timeframe with divergence info:
        {
            "1h": {"type": "bullish", "strength": 1, "description": "..."},
            "4h": {"type": "none", "strength": 0, "description": "..."},
            ...
        }
    """
    from src.rsi import (
        aggregate_to_4h_closes,
        aggregate_to_12h_closes,
        aggregate_to_3d_closes,
        calculate_rsi,
    )
    from datetime import datetime

    result: dict[str, dict] = {}

    def get_rsi_history(closes: list[float], period: int = 14) -> list[float]:
        """Calculate rolling RSI history for divergence detection."""
        if len(closes) < period + 1:
            return []

        rsi_history = []
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        if avg_loss == 0:
            rsi_history.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_history.append(100 - (100 / (1 + rs)))

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            if avg_loss == 0:
                rsi_history.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_history.append(100 - (100 / (1 + rs)))

        return rsi_history

    # Hourly-based timeframes
    if hourly_data:
        hourly_prices = hourly_data.get("prices", [])

        if hourly_prices:
            # 1h divergence
            if "1h" in multi_tf_rsi:
                closes_1h = [price for _, price in hourly_prices]
                rsi_history_1h = get_rsi_history(closes_1h)
                if len(closes_1h) >= lookback and len(rsi_history_1h) >= lookback:
                    div = detect_divergence(
                        closes_1h[-lookback:], rsi_history_1h[-lookback:], lookback
                    )
                    if div:
                        result["1h"] = div

            # 4h divergence
            if "4h" in multi_tf_rsi:
                closes_4h = aggregate_to_4h_closes(hourly_prices)
                rsi_history_4h = get_rsi_history(closes_4h)
                if len(closes_4h) >= lookback and len(rsi_history_4h) >= lookback:
                    div = detect_divergence(
                        closes_4h[-lookback:], rsi_history_4h[-lookback:], lookback
                    )
                    if div:
                        result["4h"] = div

            # 12h divergence
            if "12h" in multi_tf_rsi:
                closes_12h = aggregate_to_12h_closes(hourly_prices)
                rsi_history_12h = get_rsi_history(closes_12h)
                if len(closes_12h) >= lookback and len(rsi_history_12h) >= lookback:
                    div = detect_divergence(
                        closes_12h[-lookback:], rsi_history_12h[-lookback:], lookback
                    )
                    if div:
                        result["12h"] = div

    # Daily-based timeframes
    if daily_data:
        daily_prices = daily_data.get("prices", [])

        if daily_prices:
            # 1d divergence
            if "1d" in multi_tf_rsi:
                closes_1d = [price for _, price in daily_prices]
                rsi_history_1d = get_rsi_history(closes_1d)
                if len(closes_1d) >= lookback and len(rsi_history_1d) >= lookback:
                    div = detect_divergence(
                        closes_1d[-lookback:], rsi_history_1d[-lookback:], lookback
                    )
                    if div:
                        result["1d"] = div

            # 3d divergence
            if "3d" in multi_tf_rsi:
                closes_3d = aggregate_to_3d_closes(daily_prices)
                rsi_history_3d = get_rsi_history(closes_3d)
                if len(closes_3d) >= lookback and len(rsi_history_3d) >= lookback:
                    div = detect_divergence(
                        closes_3d[-lookback:], rsi_history_3d[-lookback:], lookback
                    )
                    if div:
                        result["3d"] = div

            # 1w divergence
            if "1w" in multi_tf_rsi:
                # Aggregate daily to weekly closes using ISO week grouping
                weekly_closes_dict: dict[tuple[int, int], float] = {}
                for timestamp_ms, price in daily_prices:
                    dt = datetime.fromtimestamp(timestamp_ms / 1000)
                    iso = dt.isocalendar()
                    week_key = (iso.year, iso.week)
                    weekly_closes_dict[week_key] = price

                sorted_weeks = sorted(weekly_closes_dict.keys())
                closes_1w = [weekly_closes_dict[week] for week in sorted_weeks]
                rsi_history_1w = get_rsi_history(closes_1w)

                if len(closes_1w) >= lookback and len(rsi_history_1w) >= lookback:
                    div = detect_divergence(
                        closes_1w[-lookback:], rsi_history_1w[-lookback:], lookback
                    )
                    if div:
                        result["1w"] = div

    return result
