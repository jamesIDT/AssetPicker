"""Persistent data storage for the RSI screener."""

import json
from datetime import datetime
from pathlib import Path

# Data directory relative to project root
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "screener_data.json"


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
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_data() -> dict | None:
    """
    Load screener data from persistent storage.

    Returns:
        Dictionary with keys: coin_data, divergence_data, last_updated,
        failed_coins, btc_regime, btc_weekly_rsi
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
