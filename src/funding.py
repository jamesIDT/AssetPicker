"""Binance Futures API client for fetching funding rates and open interest."""

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class FundingData:
    """Funding rate data for a perpetual contract."""

    symbol: str
    last_funding_rate: float
    next_funding_time: int
    mark_price: float


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

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "BinanceFundingClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
