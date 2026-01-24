"""Sector classification and sector-level RSI aggregation."""

# Sector mappings for major crypto assets
SECTOR_MAPPINGS = {
    # Layer 1s
    "bitcoin": "L1",
    "ethereum": "L1",
    "solana": "L1",
    "cardano": "L1",
    "avalanche-2": "L1",
    "polkadot": "L1",
    "near": "L1",
    "cosmos": "L1",
    # DeFi
    "uniswap": "DeFi",
    "aave": "DeFi",
    "lido-dao": "DeFi",
    "maker": "DeFi",
    "compound-governance-token": "DeFi",
    # AI/Compute
    "render-token": "AI",
    "fetch-ai": "AI",
    "singularitynet": "AI",
    "akash-network": "AI",
    # Gaming/Metaverse
    "immutable-x": "Gaming",
    "the-sandbox": "Gaming",
    "axie-infinity": "Gaming",
    "gala": "Gaming",
    # Memes
    "dogecoin": "Meme",
    "shiba-inu": "Meme",
    "pepe": "Meme",
    "floki": "Meme",
    # Infrastructure
    "chainlink": "Infra",
    "the-graph": "Infra",
    "filecoin": "Infra",
    "arweave": "Infra",
}


def get_sector(coin_id: str) -> str:
    """
    Get sector classification for a coin.

    Args:
        coin_id: CoinGecko coin ID

    Returns:
        Sector name or "Other" if not mapped
    """
    return SECTOR_MAPPINGS.get(coin_id, "Other")


def calculate_sector_rsi(coins: list[dict]) -> dict:
    """
    Calculate market-cap weighted average RSI per sector.

    Args:
        coins: List of coin dicts with keys:
            - id: CoinGecko coin ID
            - daily_rsi: Current daily RSI
            - market_cap (optional): For weighting

    Returns:
        Dict mapping sector -> dict with:
            - rsi: Market-cap weighted average RSI
            - coins: List of coin IDs in sector
            - count: Number of coins
    """
    # Group coins by sector
    sector_data: dict[str, list[dict]] = {}

    for coin in coins:
        coin_id = coin.get("id", "")
        daily_rsi = coin.get("daily_rsi")

        # Skip coins without RSI
        if daily_rsi is None:
            continue

        sector = get_sector(coin_id)

        if sector not in sector_data:
            sector_data[sector] = []

        sector_data[sector].append(coin)

    # Calculate weighted RSI per sector
    result = {}

    for sector, sector_coins in sector_data.items():
        coin_ids = [c.get("id", "") for c in sector_coins]
        count = len(sector_coins)

        # Check if market_cap available for weighting
        has_market_cap = all(c.get("market_cap") for c in sector_coins)

        if has_market_cap and count > 0:
            # Weighted average by market cap
            total_cap = sum(c["market_cap"] for c in sector_coins)
            if total_cap > 0:
                weighted_rsi = sum(
                    c["daily_rsi"] * c["market_cap"] / total_cap for c in sector_coins
                )
            else:
                # Fallback to simple average
                weighted_rsi = sum(c["daily_rsi"] for c in sector_coins) / count
        else:
            # Simple average
            weighted_rsi = sum(c["daily_rsi"] for c in sector_coins) / count

        result[sector] = {
            "rsi": round(weighted_rsi, 2),
            "coins": coin_ids,
            "count": count,
        }

    return result


def calculate_sector_momentum(coins: list[dict]) -> dict:
    """
    Calculate sector momentum with 7-day RSI change and rotation signals.

    Args:
        coins: List of coin dicts with keys:
            - id: CoinGecko coin ID
            - daily_rsi: Current daily RSI
            - market_cap (optional): For weighting
            - rsi_history: List of last 30 daily RSI values (oldest to newest)

    Returns:
        Dict mapping sector -> dict with:
            - current_rsi: Current weighted RSI
            - rsi_7d_ago: RSI from 7 days ago (or None if insufficient data)
            - momentum: "rising" | "falling" | "flat"
            - momentum_arrow: "↗" | "↘" | "→"
            - change_7d: Numeric change (or None)
            - is_rotation_signal: True if RSI < 35 AND change_7d > 0
            - days_since_bottom: Days since sector's lowest RSI in last 30 days
            - coins: List of coin IDs in sector
            - count: Number of coins
    """
    # Group coins by sector
    sector_data: dict[str, list[dict]] = {}

    for coin in coins:
        coin_id = coin.get("id", "")
        daily_rsi = coin.get("daily_rsi")

        # Skip coins without RSI
        if daily_rsi is None:
            continue

        sector = get_sector(coin_id)

        if sector not in sector_data:
            sector_data[sector] = []

        sector_data[sector].append(coin)

    result = {}
    momentum_threshold = 3.0  # Points change to count as rising/falling

    for sector, sector_coins in sector_data.items():
        coin_ids = [c.get("id", "") for c in sector_coins]
        count = len(sector_coins)

        # Check if market_cap available for weighting
        has_market_cap = all(c.get("market_cap") for c in sector_coins)

        # Calculate current weighted RSI
        if has_market_cap and count > 0:
            total_cap = sum(c["market_cap"] for c in sector_coins)
            if total_cap > 0:
                current_rsi = sum(
                    c["daily_rsi"] * c["market_cap"] / total_cap for c in sector_coins
                )
            else:
                current_rsi = sum(c["daily_rsi"] for c in sector_coins) / count
        else:
            current_rsi = sum(c["daily_rsi"] for c in sector_coins) / count

        # Calculate historical weighted RSI (7 days ago)
        rsi_7d_ago = None
        coins_with_history = [
            c for c in sector_coins
            if c.get("rsi_history") and len(c["rsi_history"]) >= 7
        ]

        if coins_with_history:
            has_hist_mcap = all(c.get("market_cap") for c in coins_with_history)

            if has_hist_mcap and len(coins_with_history) > 0:
                total_cap = sum(c["market_cap"] for c in coins_with_history)
                if total_cap > 0:
                    rsi_7d_ago = sum(
                        c["rsi_history"][-7] * c["market_cap"] / total_cap
                        for c in coins_with_history
                    )
                else:
                    rsi_7d_ago = sum(
                        c["rsi_history"][-7] for c in coins_with_history
                    ) / len(coins_with_history)
            else:
                rsi_7d_ago = sum(
                    c["rsi_history"][-7] for c in coins_with_history
                ) / len(coins_with_history)

        # Calculate momentum
        change_7d = None
        momentum = "flat"
        momentum_arrow = "→"

        if rsi_7d_ago is not None:
            change_7d = current_rsi - rsi_7d_ago
            if change_7d > momentum_threshold:
                momentum = "rising"
                momentum_arrow = "↗"
            elif change_7d < -momentum_threshold:
                momentum = "falling"
                momentum_arrow = "↘"

        # Calculate rotation signal
        is_rotation_signal = (
            current_rsi < 35
            and change_7d is not None
            and change_7d > 0
        )

        # Calculate days since bottom in last 30 days
        days_since_bottom = None
        coins_with_30d_history = [
            c for c in sector_coins
            if c.get("rsi_history") and len(c["rsi_history"]) >= 30
        ]

        if coins_with_30d_history:
            # Calculate weighted RSI for each of the last 30 days
            has_hist_mcap = all(c.get("market_cap") for c in coins_with_30d_history)
            daily_weighted_rsi = []

            for day_idx in range(30):
                if has_hist_mcap:
                    total_cap = sum(c["market_cap"] for c in coins_with_30d_history)
                    if total_cap > 0:
                        day_rsi = sum(
                            c["rsi_history"][-(30 - day_idx)] * c["market_cap"] / total_cap
                            for c in coins_with_30d_history
                        )
                    else:
                        day_rsi = sum(
                            c["rsi_history"][-(30 - day_idx)]
                            for c in coins_with_30d_history
                        ) / len(coins_with_30d_history)
                else:
                    day_rsi = sum(
                        c["rsi_history"][-(30 - day_idx)]
                        for c in coins_with_30d_history
                    ) / len(coins_with_30d_history)
                daily_weighted_rsi.append(day_rsi)

            # Find the minimum and its position
            min_rsi = min(daily_weighted_rsi)
            min_idx = daily_weighted_rsi.index(min_rsi)
            days_since_bottom = 29 - min_idx  # 0 = today, 29 = 30 days ago

        result[sector] = {
            "current_rsi": round(current_rsi, 2),
            "rsi_7d_ago": round(rsi_7d_ago, 2) if rsi_7d_ago is not None else None,
            "momentum": momentum,
            "momentum_arrow": momentum_arrow,
            "change_7d": round(change_7d, 2) if change_7d is not None else None,
            "is_rotation_signal": is_rotation_signal,
            "days_since_bottom": days_since_bottom,
            "coins": coin_ids,
            "count": count,
        }

    return result
