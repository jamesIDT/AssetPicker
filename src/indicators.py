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
