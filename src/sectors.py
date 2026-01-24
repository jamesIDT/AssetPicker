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
