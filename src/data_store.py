"""Persistent data storage for the RSI screener."""

import json
from datetime import datetime
from pathlib import Path

# Data directory relative to project root
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "screener_data.json"

# Hourly data caching (separate from main screener data)
HOURLY_DATA_FILE = DATA_DIR / "hourly_data.json"
HOURLY_CACHE_TTL_MINUTES = 60  # 1 hour TTL - hourly data doesn't need frequent refresh


def ensure_data_dir() -> None:
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)


def save_data(
    coin_data: list[dict],
    divergence_data: list[dict],
    last_updated: datetime,
    failed_coins: int,
    btc_regime: dict | None,
    btc_weekly_rsi: float | None,
    multi_tf_divergence: dict | None = None,
    multi_tf_rsi: dict | None = None,
) -> None:
    """Save screener data to persistent storage."""
    ensure_data_dir()

    data = {
        "coin_data": coin_data,
        "divergence_data": divergence_data,
        "last_updated": last_updated.isoformat() if last_updated else None,
        "failed_coins": failed_coins,
        "btc_regime": btc_regime,
        "btc_weekly_rsi": btc_weekly_rsi,
        "multi_tf_divergence": multi_tf_divergence or {},
        "multi_tf_rsi": multi_tf_rsi or {},
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_data() -> dict | None:
    """
    Load screener data from persistent storage.

    Returns:
        Dictionary with keys: coin_data, divergence_data, last_updated,
        failed_coins, btc_regime, btc_weekly_rsi, multi_tf_divergence
        Or None if no data file exists.
    """
    if not DATA_FILE.exists():
        return None

    try:
        with open(DATA_FILE) as f:
            data = json.load(f)

        # Convert ISO string back to datetime
        if data.get("last_updated"):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])

        return data
    except (json.JSONDecodeError, KeyError, ValueError):
        # If file is corrupted, return None so app fetches fresh data
        return None


def data_exists() -> bool:
    """Check if persistent data exists."""
    return DATA_FILE.exists()


def save_hourly_data(hourly_history: dict[str, dict], last_updated: datetime) -> None:
    """
    Save raw hourly history data with timestamp.

    Args:
        hourly_history: Dict mapping coin_id -> market_chart response
        last_updated: Timestamp for TTL checking
    """
    ensure_data_dir()

    data = {
        "hourly_history": hourly_history,
        "last_updated": last_updated.isoformat(),
    }

    with open(HOURLY_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_hourly_data() -> dict | None:
    """
    Load hourly history data from persistent storage.

    Returns:
        Dict with 'hourly_history' and 'last_updated' keys,
        or None if file doesn't exist or is corrupted.
    """
    if not HOURLY_DATA_FILE.exists():
        return None

    try:
        with open(HOURLY_DATA_FILE) as f:
            data = json.load(f)

        # Convert ISO string back to datetime
        if data.get("last_updated"):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])

        return data
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def is_hourly_cache_valid() -> bool:
    """
    Check if hourly cache exists and is within TTL.

    Returns:
        True if cache is valid and fresh, False if expired or missing.
    """
    data = load_hourly_data()
    if data is None:
        return False

    last_updated = data.get("last_updated")
    if not isinstance(last_updated, datetime):
        return False

    age_minutes = (datetime.now() - last_updated).total_seconds() / 60
    return age_minutes < HOURLY_CACHE_TTL_MINUTES
