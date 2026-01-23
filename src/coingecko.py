"""CoinGecko API client for fetching market data and OHLC prices."""

import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class CoinGeckoError(Exception):
    """Exception raised for CoinGecko API errors."""

    pass


class CoinGeckoClient:
    """Async client for CoinGecko Pro API."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize CoinGecko client.

        Args:
            api_key: CoinGecko Pro API key. If None, loads from COINGECKO_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
        self.base_url = "https://pro-api.coingecko.com/api/v3"
        self.headers: dict[str, str] = {}
        if self.api_key:
            self.headers["x-cg-pro-api-key"] = self.api_key
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _request(self, endpoint: str, params: dict | None = None) -> dict | list:
        """
        Make an async GET request to the CoinGecko API.

        Args:
            endpoint: API endpoint path (e.g., "/coins/markets")
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            CoinGeckoError: If the API returns a non-2xx status
        """
        url = f"{self.base_url}{endpoint}"
        response = await self._client.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise CoinGeckoError(
                f"API request failed: {response.status_code} - {response.text}"
            )

        return response.json()

    async def get_coins_market_data(
        self, coin_ids: list[str], vs_currency: str = "usd"
    ) -> list[dict]:
        """
        Fetch market data for multiple coins in one request.

        Args:
            coin_ids: List of CoinGecko coin IDs (e.g., ["bitcoin", "ethereum"])
            vs_currency: Target currency for prices (default: "usd")

        Returns:
            List of dicts with: id, symbol, name, current_price, market_cap, total_volume
        """
        if not coin_ids:
            return []

        params = {
            "vs_currency": vs_currency,
            "ids": ",".join(coin_ids),
            "order": "market_cap_desc",
            "per_page": 250,
            "sparkline": "false",
        }

        result = await self._request("/coins/markets", params)
        return result if isinstance(result, list) else []

    async def get_coin_market_chart(
        self, coin_id: str, vs_currency: str = "usd", days: int = 90
    ) -> dict:
        """
        Fetch historical price data for RSI calculation.

        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin")
            vs_currency: Target currency (default: "usd")
            days: Number of days of historical data (default: 90)

        Returns:
            Dict with 'prices', 'market_caps', 'total_volumes' arrays.
            Each array contains [timestamp_ms, value] pairs.
        """
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily",
        }

        result = await self._request(f"/coins/{coin_id}/market_chart", params)
        return result if isinstance(result, dict) else {}

    async def get_coins_history(
        self, coin_ids: list[str], vs_currency: str = "usd", days: int = 90
    ) -> dict[str, dict]:
        """
        Fetch historical data for multiple coins.

        Args:
            coin_ids: List of CoinGecko coin IDs
            vs_currency: Target currency (default: "usd")
            days: Number of days of historical data (default: 90)

        Returns:
            Dict mapping coin_id -> market_chart response.
            Failed fetches are excluded from the result.
        """
        if not coin_ids:
            return {}

        tasks = [
            self.get_coin_market_chart(coin_id, vs_currency, days)
            for coin_id in coin_ids
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        history: dict[str, dict] = {}
        for coin_id, result in zip(coin_ids, results):
            if isinstance(result, dict):
                history[coin_id] = result
            # Exceptions are silently excluded - failed coins won't appear in result

        return history

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "CoinGeckoClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
