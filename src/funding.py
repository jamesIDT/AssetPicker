"""Binance Futures API client for fetching funding rates and open interest."""

import asyncio
from dataclasses import dataclass
from typing import Any, Literal

import httpx


@dataclass
class FundingData:
    """Funding rate data for a perpetual contract."""

    symbol: str
    last_funding_rate: float
    next_funding_time: int
    mark_price: float


@dataclass
class OpenInterestData:
    """Open interest data point."""

    symbol: str
    sum_open_interest: float
    sum_open_interest_value: float
    timestamp: int


@dataclass
class OpenInterestChange:
    """Open interest change metrics."""

    current_oi: float
    change_24h_pct: float
    direction: Literal["increasing", "decreasing", "stable"]


@dataclass
class PositioningData:
    """Complete positioning data for a symbol."""

    funding_rate: float
    oi_change_24h: float | None
    crowded: Literal["long", "short", "neutral"]
    crowded_score: int
    squeeze_risk: Literal["high", "medium", "low"] | None


class BinanceFundingError(Exception):
    """Exception raised for Binance Futures API errors."""

    pass


class BinanceFundingClient:
    """Async client for Binance Futures API (funding rates and open interest)."""

    def __init__(self) -> None:
        """Initialize Binance Futures client."""
        self.base_url = "https://fapi.binance.com"
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict | list:
        """
        Make an async GET request to the Binance Futures API.

        Args:
            endpoint: API endpoint path (e.g., "/fapi/v1/premiumIndex")
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            BinanceFundingError: If the API returns a non-2xx status
        """
        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, params=params)

        if response.status_code != 200:
            raise BinanceFundingError(
                f"API request failed: {response.status_code} - {response.text}"
            )

        return response.json()

    @staticmethod
    def symbol_to_exchange(symbol: str) -> str:
        """
        Convert a symbol to Binance exchange format.

        Args:
            symbol: Uppercase symbol (e.g., "BTC", "ETH")

        Returns:
            Exchange format symbol (e.g., "BTCUSDT")
        """
        return f"{symbol.upper()}USDT"

    @staticmethod
    def exchange_to_symbol(exchange_symbol: str) -> str:
        """
        Convert a Binance exchange symbol to standard format.

        Args:
            exchange_symbol: Exchange format symbol (e.g., "BTCUSDT")

        Returns:
            Standard symbol (e.g., "BTC")
        """
        if exchange_symbol.endswith("USDT"):
            return exchange_symbol[:-4]
        return exchange_symbol

    async def get_all_funding_rates(self) -> dict[str, FundingData]:
        """
        Fetch funding rates for all perpetual contracts.

        Returns:
            Dict mapping exchange symbol -> FundingData
        """
        try:
            result = await self._request("/fapi/v1/premiumIndex")
            if not isinstance(result, list):
                return {}

            funding_data: dict[str, FundingData] = {}
            for item in result:
                symbol = item.get("symbol", "")
                try:
                    funding_data[symbol] = FundingData(
                        symbol=symbol,
                        last_funding_rate=float(item.get("lastFundingRate", 0)),
                        next_funding_time=int(item.get("nextFundingTime", 0)),
                        mark_price=float(item.get("markPrice", 0)),
                    )
                except (ValueError, TypeError):
                    continue

            return funding_data
        except BinanceFundingError:
            return {}

    async def get_funding_for_symbols(
        self, symbols: list[str]
    ) -> dict[str, FundingData | None]:
        """
        Fetch funding rates for specific symbols.

        Args:
            symbols: List of uppercase symbols (e.g., ["BTC", "ETH"])

        Returns:
            Dict mapping original symbol -> FundingData or None if not found
        """
        all_rates = await self.get_all_funding_rates()

        result: dict[str, FundingData | None] = {}
        for symbol in symbols:
            exchange_symbol = self.symbol_to_exchange(symbol)
            result[symbol] = all_rates.get(exchange_symbol)

        return result

    async def get_open_interest(self, symbol: str) -> list[OpenInterestData]:
        """
        Fetch historical open interest data for a symbol.

        Args:
            symbol: Uppercase symbol (e.g., "BTC")

        Returns:
            List of OpenInterestData points (last 24 hours, hourly)
        """
        exchange_symbol = self.symbol_to_exchange(symbol)
        params = {
            "symbol": exchange_symbol,
            "period": "1h",
            "limit": 24,
        }

        try:
            result = await self._request("/futures/data/openInterestHist", params)
            if not isinstance(result, list):
                return []

            oi_data: list[OpenInterestData] = []
            for item in result:
                try:
                    oi_data.append(
                        OpenInterestData(
                            symbol=item.get("symbol", exchange_symbol),
                            sum_open_interest=float(item.get("sumOpenInterest", 0)),
                            sum_open_interest_value=float(
                                item.get("sumOpenInterestValue", 0)
                            ),
                            timestamp=int(item.get("timestamp", 0)),
                        )
                    )
                except (ValueError, TypeError):
                    continue

            return oi_data
        except BinanceFundingError:
            return []

    async def get_open_interest_change(self, symbol: str) -> OpenInterestChange | None:
        """
        Calculate open interest change metrics for a symbol.

        Args:
            symbol: Uppercase symbol (e.g., "BTC")

        Returns:
            OpenInterestChange with current OI, 24h change %, and direction.
            Returns None if data is unavailable.
        """
        oi_data = await self.get_open_interest(symbol)

        if len(oi_data) < 2:
            return None

        # Sort by timestamp to ensure correct order
        oi_data.sort(key=lambda x: x.timestamp)

        oldest = oi_data[0]
        newest = oi_data[-1]

        current_oi = newest.sum_open_interest_value

        # Calculate percentage change
        if oldest.sum_open_interest_value > 0:
            change_pct = (
                (newest.sum_open_interest_value - oldest.sum_open_interest_value)
                / oldest.sum_open_interest_value
            ) * 100
        else:
            change_pct = 0.0

        # Determine direction based on thresholds
        if change_pct > 5:
            direction: Literal["increasing", "decreasing", "stable"] = "increasing"
        elif change_pct < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        return OpenInterestChange(
            current_oi=current_oi,
            change_24h_pct=round(change_pct, 2),
            direction=direction,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "BinanceFundingClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


def create_symbol_mapping(coin_ids: list[dict]) -> dict[str, str]:
    """
    Create a mapping from CoinGecko IDs to Binance exchange symbols.

    Args:
        coin_ids: List of dicts with "id" and "symbol" fields from watchlist.json

    Returns:
        Dict mapping CoinGecko ID -> exchange symbol (e.g., "bitcoin" -> "BTCUSDT")

    Example:
        >>> coins = [{"id": "bitcoin", "symbol": "btc"}, {"id": "ethereum", "symbol": "eth"}]
        >>> create_symbol_mapping(coins)
        {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT"}
    """
    mapping: dict[str, str] = {}
    for coin in coin_ids:
        coin_id = coin.get("id", "")
        symbol = coin.get("symbol", "")
        if coin_id and symbol:
            mapping[coin_id] = BinanceFundingClient.symbol_to_exchange(symbol)
    return mapping


def calculate_positioning(
    funding_rate: float, oi_change_pct: float | None = None
) -> dict:
    """
    Calculate positioning analysis from funding rate and OI change.

    Args:
        funding_rate: Funding rate as decimal (e.g., 0.0005 = 0.05%)
        oi_change_pct: OI 24h change percentage (optional)

    Returns:
        Dict with:
        - crowded: "long" | "short" | "neutral"
        - crowded_score: 0-100 intensity (0=neutral, 100=extreme)
        - squeeze_risk: "high" | "medium" | "low" | None
    """
    # Determine crowded status based on funding threshold (0.03%)
    threshold = 0.0003
    if funding_rate > threshold:
        crowded: Literal["long", "short", "neutral"] = "long"
    elif funding_rate < -threshold:
        crowded = "short"
    else:
        crowded = "neutral"

    # Calculate crowded score: abs(funding) / 0.001 * 100, capped at 100
    crowded_score = min(int(abs(funding_rate) / 0.001 * 100), 100)

    # Determine squeeze risk based on crowded status and OI change
    squeeze_risk: Literal["high", "medium", "low"] | None = None
    if crowded != "neutral" and oi_change_pct is not None:
        if oi_change_pct > 10:
            squeeze_risk = "high"
        elif oi_change_pct > 5:
            squeeze_risk = "medium"
        elif oi_change_pct > 0:
            squeeze_risk = "low"

    return {
        "crowded": crowded,
        "crowded_score": crowded_score,
        "squeeze_risk": squeeze_risk,
    }


async def get_positioning_for_coins(
    client: BinanceFundingClient, symbols: list[str]
) -> dict[str, PositioningData]:
    """
    Fetch positioning data for multiple symbols efficiently.

    Args:
        client: BinanceFundingClient instance
        symbols: List of uppercase symbols (e.g., ["BTC", "ETH"])

    Returns:
        Dict mapping symbol -> PositioningData
    """
    # Fetch all funding rates in one call
    funding_data = await client.get_funding_for_symbols(symbols)

    # Fetch OI changes for all symbols in parallel
    oi_tasks = [client.get_open_interest_change(symbol) for symbol in symbols]
    oi_results = await asyncio.gather(*oi_tasks)
    oi_data = dict(zip(symbols, oi_results))

    # Combine into positioning data
    result: dict[str, PositioningData] = {}
    for symbol in symbols:
        funding = funding_data.get(symbol)
        oi = oi_data.get(symbol)

        if funding is None:
            continue

        oi_change = oi.change_24h_pct if oi else None
        positioning = calculate_positioning(funding.last_funding_rate, oi_change)

        result[symbol] = PositioningData(
            funding_rate=funding.last_funding_rate,
            oi_change_24h=oi_change,
            crowded=positioning["crowded"],
            crowded_score=positioning["crowded_score"],
            squeeze_risk=positioning["squeeze_risk"],
        )

    return result
