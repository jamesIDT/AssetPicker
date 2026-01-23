---
status: complete
type: technical-specification
depth: normal
created: 2025-01-23
rounds_completed: 3
total_rounds_planned: 3
---

# Crypto RSI Screener - Technical Specification

## Overview

A Python/Streamlit webapp that visualizes cryptoasset RSI (Relative Strength Index) against liquidity metrics to identify potential investment opportunities. The tool plots coins on a scatter chart where position and color encode multiple dimensions of market data, making it easy to spot outliers.

## Validated Assumptions

- User has a paid CoinGecko Pro API subscription (key to be stored in `.env`)
- Watchlist of 30-50 coins managed via config file
- This is a personal research/screening tool, not production trading
- Daily and weekly RSI timeframes are sufficient (no intraday)
- Classic 30/70 RSI thresholds are appropriate

## Core Requirements

### 1. Data Source

- **API**: CoinGecko Pro API
- **Authentication**: API key from `.env` file
- **Rate Limits**: Respect CoinGecko Pro tier limits (500 calls/min)

### 2. Watchlist Management

- **Format**: JSON config file (`watchlist.json`)
- **Structure**:
  ```json
  {
    "coins": [
      {"id": "bitcoin", "symbol": "BTC"},
      {"id": "ethereum", "symbol": "ETH"}
    ]
  }
  ```
- **Location**: Project root directory
- **Size**: 30-50 coins initially

### 3. Data Requirements

For each coin, fetch:
- Current price (USD)
- 24h trading volume
- Market cap
- Historical OHLC data (for RSI calculation):
  - Daily: Last 14+ days
  - Weekly: Last 14+ weeks

### 4. RSI Calculation

Standard RSI formula with 14-period lookback:

```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss (over 14 periods)
```

Calculate for:
- **Daily RSI**: Using daily close prices
- **Weekly RSI**: Using weekly close prices

### 5. Visualization

#### Primary Chart: Scatter Plot

| Dimension | Encoding |
|-----------|----------|
| X-axis | Daily RSI (0-100) |
| Y-axis | Volume/Market Cap ratio (log scale recommended) |
| Color | Weekly RSI (gradient: green=oversold, yellow=neutral, red=overbought) |
| Size | Fixed or optionally by market cap |
| Label | Coin symbol on hover |

#### Visual Zones

- **Oversold zone**: RSI < 30 (left side, green-tinted background)
- **Neutral zone**: RSI 30-70 (center, no tint)
- **Overbought zone**: RSI > 70 (right side, red-tinted background)

#### Interaction

- **Hover/Click**: Tooltip showing:
  - Coin name and symbol
  - Current price
  - Daily RSI value
  - Weekly RSI value
  - Volume/MCap ratio
  - 24h volume
  - Market cap

#### Summary Lists Below Chart

**"Potential Opportunities" (Oversold)**
- Coins where daily RSI < 30
- Sorted by RSI ascending (most oversold first)
- Highlight if weekly RSI also < 30 (strong signal)

**"Exercise Caution" (Overbought)**
- Coins where daily RSI > 70
- Sorted by RSI descending (most overbought first)
- Highlight if weekly RSI also > 70 (strong signal)

### 6. Refresh Behavior

- **On-demand only**: Manual "Refresh Data" button
- Show timestamp of last refresh
- Loading indicator during data fetch

## Technical Architecture

### Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | Streamlit |
| Charting | Plotly (interactive scatter plots) |
| HTTP Client | httpx or requests |
| Config | python-dotenv for env vars |

### Project Structure

```
crypto-rsi-screener/
├── .env                    # API keys (gitignored)
├── .env.example            # Template for env vars
├── .gitignore
├── .planning/              # Specifications
├── requirements.txt
├── watchlist.json          # Coin watchlist config
├── app.py                  # Main Streamlit app
└── src/
    ├── __init__.py
    ├── coingecko.py        # CoinGecko API client
    ├── rsi.py              # RSI calculation logic
    └── charts.py           # Plotly chart builders
```

### Key Components

#### 1. CoinGecko Client (`src/coingecko.py`)

```python
class CoinGeckoClient:
    def __init__(self, api_key: str)
    def get_coin_market_data(self, coin_ids: list[str]) -> list[dict]
    def get_coin_ohlc(self, coin_id: str, days: int) -> list[dict]
    def get_coin_market_chart(self, coin_id: str, days: int) -> dict
```

#### 2. RSI Calculator (`src/rsi.py`)

```python
def calculate_rsi(prices: list[float], period: int = 14) -> float
def get_daily_rsi(ohlc_data: list[dict]) -> float
def get_weekly_rsi(ohlc_data: list[dict]) -> float
```

#### 3. Chart Builder (`src/charts.py`)

```python
def create_rsi_scatter(
    data: list[dict],  # coin data with RSI values
    oversold_threshold: int = 30,
    overbought_threshold: int = 70
) -> plotly.graph_objects.Figure
```

### Data Flow

1. User clicks "Refresh Data" button
2. Load watchlist from `watchlist.json`
3. For each coin in watchlist:
   - Fetch market data (price, volume, mcap)
   - Fetch OHLC history (90 days for daily, 1 year for weekly)
   - Calculate daily RSI
   - Calculate weekly RSI
   - Compute volume/mcap ratio
4. Store computed data in Streamlit session state
5. Render scatter plot with Plotly
6. Generate opportunity/caution lists

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  Crypto RSI Screener                    [Refresh Data]  │
│  Last updated: 2025-01-23 14:30:00                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              ┌─────────────────────────┐                │
│   Vol/MCap   │    Scatter Plot         │                │
│      ↑       │    (interactive)        │                │
│      │       │                         │                │
│              └─────────────────────────┘                │
│                    Daily RSI →                          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Potential Opportunities (Oversold)                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Coin    Daily RSI  Weekly RSI  Vol/MCap  Price  │   │
│  │ XYZ     22         28 ★        0.15      $1.23  │   │
│  │ ABC     25         45          0.08      $0.45  │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Exercise Caution (Overbought)                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Coin    Daily RSI  Weekly RSI  Vol/MCap  Price  │   │
│  │ DEF     82         78 ★        0.22      $5.67  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

★ = Weekly RSI also in extreme zone (strong signal)
```

## Configuration

### Environment Variables (`.env`)

```
COINGECKO_API_KEY=your_api_key_here
```

### Watchlist Format (`watchlist.json`)

```json
{
  "coins": [
    {"id": "bitcoin", "symbol": "BTC"},
    {"id": "ethereum", "symbol": "ETH"},
    {"id": "solana", "symbol": "SOL"}
  ]
}
```

CoinGecko coin IDs can be found at: https://api.coingecko.com/api/v3/coins/list

## Success Criteria

1. App loads and displays scatter plot with all watchlist coins
2. RSI calculations match manual verification against TradingView
3. Color encoding clearly distinguishes weekly RSI levels
4. Opportunity/caution lists correctly filter by RSI thresholds
5. Refresh completes within 30 seconds for 50 coins
6. Tooltips display all required metrics on hover

## Future Enhancements (Out of Scope)

- Multiple watchlists
- Historical RSI trend charts per coin
- Price alerts based on RSI thresholds
- Export to CSV
- Additional indicators (MACD, Bollinger Bands)

## Implementation Order

1. Set up project structure and dependencies
2. Implement CoinGecko client with API key auth
3. Implement RSI calculation logic
4. Create basic Streamlit app with refresh button
5. Build scatter plot with Plotly
6. Add tooltip interaction
7. Add opportunity/caution summary lists
8. Add visual zone shading
9. Polish UI and error handling
