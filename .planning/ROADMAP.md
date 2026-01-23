# Roadmap: AssetPicker

## Overview

Build a Python/Streamlit webapp that visualizes crypto RSI against liquidity metrics to spot investment opportunities. Starting with project foundation, then data layer (CoinGecko + RSI), followed by interactive Plotly visualization, and finishing with summary lists and polish.

## Domain Expertise

None

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundation** - Project structure, dependencies, config files ✓
- [x] **Phase 2: CoinGecko Integration** - API client with market data and OHLC fetching ✓
- [x] **Phase 3: RSI Calculation** - 14-period RSI algorithm for daily and weekly timeframes ✓
- [x] **Phase 4: Core Visualization** - Plotly scatter plot with RSI/liquidity encodings ✓
- [ ] **Phase 5: Interaction & Lists** - Tooltips, zone shading, opportunity/caution lists
- [ ] **Phase 6: Polish** - Refresh UI, loading states, error handling

## Phase Details

### Phase 1: Foundation
**Goal**: Working project skeleton with all config files in place
**Depends on**: Nothing (first phase)
**Research**: Unlikely (standard Python/Streamlit setup)
**Plans**: TBD

Key deliverables:
- Project structure per spec (`app.py`, `src/` modules)
- `requirements.txt` with dependencies
- `.env.example` template for API key
- `.gitignore` for Python + env files
- `watchlist.json` with initial coin list
- Basic `app.py` that runs (placeholder UI)

### Phase 2: CoinGecko Integration
**Goal**: Working API client that fetches all required data
**Depends on**: Phase 1
**Research**: Likely (external API)
**Research topics**: CoinGecko Pro API endpoints, rate limits, OHLC data format, authentication headers
**Plans**: TBD

Key deliverables:
- `src/coingecko.py` client class
- API key authentication via .env
- `get_coin_market_data()` - price, volume, mcap
- `get_coin_ohlc()` or `get_coin_market_chart()` - historical prices
- Rate limit handling (respect 500 calls/min)
- Error handling for API failures

### Phase 3: RSI Calculation
**Goal**: Accurate RSI calculation matching TradingView
**Depends on**: Phase 2
**Research**: Unlikely (standard algorithm)
**Plans**: TBD

Key deliverables:
- `src/rsi.py` module
- `calculate_rsi()` with 14-period lookback
- `get_daily_rsi()` from daily closes
- `get_weekly_rsi()` from weekly closes
- Data transformation pipeline (OHLC → RSI)
- Verification against TradingView values

### Phase 4: Core Visualization
**Goal**: Interactive scatter plot with all data encodings
**Depends on**: Phase 3
**Research**: Unlikely (standard Plotly patterns)
**Plans**: TBD

Key deliverables:
- `src/charts.py` module
- Plotly scatter plot in Streamlit
- X-axis: Daily RSI (0-100)
- Y-axis: Vol/MCap ratio (log scale)
- Color: Weekly RSI gradient (green → yellow → red)
- Point labels with coin symbols
- Session state for data persistence

### Phase 5: Interaction & Lists
**Goal**: Full interactivity and summary lists
**Depends on**: Phase 4
**Research**: Unlikely (Plotly/Streamlit standard patterns)
**Plans**: TBD

Key deliverables:
- Hover tooltips (name, price, RSI values, volume, mcap)
- Visual zone shading (green left, red right)
- "Potential Opportunities" list (daily RSI < 30)
- "Exercise Caution" list (daily RSI > 70)
- Star indicator for aligned weekly RSI
- Sorted lists (most extreme first)

### Phase 6: Polish
**Goal**: Production-ready personal tool
**Depends on**: Phase 5
**Research**: Unlikely (refinement)
**Plans**: TBD

Key deliverables:
- Refresh button with loading indicator
- Last updated timestamp display
- Error states for API/network failures
- Graceful handling of missing data
- UI refinements per spec layout

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 1/1 | Complete | 2026-01-23 |
| 2. CoinGecko Integration | 1/1 | Complete | 2026-01-23 |
| 3. RSI Calculation | 1/1 | Complete | 2026-01-23 |
| 4. Core Visualization | 1/1 | Complete | 2026-01-23 |
| 5. Interaction & Lists | 0/TBD | Not started | - |
| 6. Polish | 0/TBD | Not started | - |
