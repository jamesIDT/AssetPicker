# Phase 8: Funding Rate Integration Discovery

## Discovery Level
Level 2 - Standard Research (external API integration)

## Research Summary

### Binance Futures API (Public, No Auth Required)

**Current Funding Rate:**
- Endpoint: `GET /fapi/v1/premiumIndex`
- Base URL: `https://fapi.binance.com`
- Returns: `lastFundingRate`, `nextFundingTime`, `markPrice`, `indexPrice`
- Symbol format: `BTCUSDT` (uppercase)
- Can omit symbol to get all symbols

**Historical Funding Rates:**
- Endpoint: `GET /fapi/v1/fundingRate`
- Query params: `symbol`, `startTime`, `endTime`, `limit` (max 1000)
- Returns: `fundingRate`, `fundingTime`, `markPrice`

**Open Interest:**
- Endpoint: `GET /futures/data/openInterestHist`
- Query params: `symbol`, `period` (5m-1d), `limit` (max 500)
- Returns: `sumOpenInterest`, `sumOpenInterestValue`, `timestamp`
- Only data from past month available

### Bybit V5 API (Public, No Auth Required)

**Current Funding Rate + Open Interest:**
- Endpoint: `GET /v5/market/tickers`
- Base URL: `https://api.bybit.com`
- Query params: `category=linear` (for USDT perpetuals)
- Returns: `fundingRate`, `openInterest`, `openInterestValue`, `nextFundingTime`
- Symbol format: `BTCUSDT` (uppercase)

**Historical Funding Rates:**
- Endpoint: `GET /v5/market/funding/history`
- Query params: `category=linear`, `symbol`, `startTime`, `endTime`, `limit` (max 200)

**Historical Open Interest:**
- Endpoint: `GET /v5/market/open-interest`
- Query params: `category=linear`, `symbol`, `intervalTime` (5min-1d), `limit` (max 200)

### Rate Limits

- Binance: 1200 requests/min for market data
- Bybit: Generally generous for market data endpoints

### Symbol Mapping

The watchlist already has `symbol` field (e.g., "BTC").
Mapping to exchange symbols: `{symbol}USDT` (e.g., `BTCUSDT`)

Not all watchlist coins will have perpetual futures. Need to handle gracefully:
- Check if symbol exists on exchange
- Return None/null for coins without perps
- Don't fail entire request for missing symbols

### Confluence Logic (from Phase 14 roadmap)

Funding alignment adds +0.2 to confluence multiplier when:
- RSI oversold (< 30) AND funding rate negative (shorts paying longs)
- RSI overbought (> 70) AND funding rate positive (longs paying shorts)

Crowded positioning detection:
- High positive funding (> 0.03%) = crowded long
- High negative funding (< -0.03%) = crowded short
- Large OI + extreme funding = potential for short squeeze / long squeeze

## Implementation Decisions

1. **Use Binance as primary** (more volume, more coins have perps)
2. **Bybit as optional secondary** (for coins not on Binance)
3. **Create separate `src/funding.py` module** following project pattern
4. **Async httpx client** matching CoinGecko client pattern
5. **Symbol mapping** via simple uppercase + USDT suffix
6. **Graceful degradation** for coins without perps (return None, don't fail)

## Files to Create/Modify

- `src/funding.py` (new) - Binance/Bybit API clients
- `src/indicators.py` (modify) - Add confluence detection function
