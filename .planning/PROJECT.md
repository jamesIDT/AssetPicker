# AssetPicker

## What This Is

A personal crypto screening tool that visualizes RSI (Relative Strength Index) against liquidity metrics to identify potential investment opportunities. Displays an interactive scatter plot where position encodes daily RSI vs volume/market-cap ratio, and color encodes weekly RSI alignment—making it easy to spot oversold or overbought outliers at a glance.

## Core Value

Surface crypto assets where both daily AND weekly RSI align in extreme zones (both oversold or both overbought) with adequate liquidity—the strongest potential signals.

## Current State

**Version:** v2.0 Advanced Screening shipped 2026-01-24
**Stack:** Python 3.x + Streamlit + Plotly + httpx + pandas
**LOC:** ~3,700 lines of Python
**Status:** Full multi-factor opportunity detection system, production-ready

## Requirements

### Validated

**v1.0 Core Features:**
- Scatter plot with daily RSI (x-axis) vs volume/mcap ratio (y-axis)
- Color encoding for weekly RSI (green=oversold → red=overbought)
- Visual zone shading for oversold (<30) and overbought (>70) regions
- Tooltip on hover showing coin stats (name, price, RSI values, volume, mcap)
- "Potential Opportunities" list below chart (daily RSI < 30)
- "Exercise Caution" list below chart (daily RSI > 70)
- Highlight coins where both daily AND weekly RSI align in extreme zones
- JSON config file for watchlist management (48 coins)
- Manual refresh button with timestamp display
- CoinGecko Pro API integration for market data

**v2.0 Advanced Screening:**
- Regime detection (Bull ↗, Bull ↘, Bear ↗, Bear ↘, Transition) with banner display
- RSI acceleration calculation (velocity + second derivative)
- Z-score statistical extremes with optional labels
- Beta-adjusted relative strength with color mode toggle
- Sector classification (Majors, DeFi, AI, DeSci) with weighted RSI
- Multi-timeframe divergence detection with scoring (1/2/4)
- Visual divergence markers (+/◆) with ring-based score layering
- Signal lifecycle stages (Fresh/Confirmed/Extended/Resolving)
- Volatility regime detection (Compressed/Normal/High Vol)
- Conviction ratings (★★★ = Fresh + Compressed)
- Sector momentum with rotation signals (RSI < 35 AND rising)
- Acceleration Quadrant (4-zone chart: acceleration × volatility)
- Funding rate integration (Binance/Bybit perpetual rates)
- Open interest tracking for positioning imbalance
- Opportunity decay score with multi-factor confluence
- Opportunity Leaderboard with Long/Short tabs and filters

### Active

(None — v2.0 complete)

### Out of Scope

- Price alerts/notifications — adds complexity, not needed for screening
- Multiple watchlists — single list sufficient for v1
- Additional indicators (MACD, Bollinger) — RSI focus keeps it simple
- UI-based watchlist editing — JSON file is fine
- Historical RSI trend charts — can add later if needed
- Export to CSV — manual analysis sufficient
- Real-time auto-refresh — on-demand is enough for daily/weekly signals

## Context

**Related project**: User has IDT-SuperAnalyst project with CoinGecko integration and various crypto analysis agents. This is a focused, standalone screening tool rather than an extension of that system.

**API access**: User has paid CoinGecko Pro tier (key stored in .env). Pro tier provides 500 calls/min and better historical data access.

**Use case**: Personal investment research. Not production trading—manual decision-making after screening.

**RSI calculation**: Wilder's smoothed 14-period RSI formula. Daily RSI uses daily closes, weekly RSI uses weekly closes with ISO week boundaries.

## Constraints

- **API**: CoinGecko Pro — user has existing subscription
- **Stack**: Python + Streamlit + Plotly — fast to build, interactive charts
- **Watchlist size**: 30-50 coins — balances coverage with API efficiency
- **Refresh model**: On-demand only — daily/weekly signals don't need real-time

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Volume/MCap ratio for Y-axis | Normalized liquidity metric comparable across market caps | Good |
| Color encoding for weekly RSI | Enables 3D visualization on 2D plane, shows timeframe alignment | Good |
| Streamlit over React | Faster to build, Plotly integration, sufficient for personal tool | Good |
| JSON watchlist over UI | Simpler implementation, easy to edit manually | Good |
| Classic 30/70 RSI thresholds | Well-understood, standard interpretation | Good |
| httpx over requests | Async capability for concurrent API calls | Good |
| Pure Python RSI (no pandas) | Minimal dependencies, simpler codebase | Good |
| Wilder's smoothed RSI | Industry standard, matches TradingView | Good |
| RdYlGn_r colorscale | Intuitive red=danger, green=opportunity | Good |
| Log scale Y-axis | Handles wide vol/mcap ratio range effectively | Good |
| Tuple return for partial failures | Clean error handling without losing good data | Good |
| st.stop() for unrecoverable errors | Prevents cascading issues in UI | Good |
| Divergence markers (+/◆) | Shape instantly conveys bull/bear direction | Good |
| Ring layering for scores | Visual hierarchy without cluttering chart | Good |
| 4-sector classification | Majors/DeFi/AI/DeSci covers 48-coin watchlist | Good |
| Multiplicative opportunity score | Base × Freshness × Confluence captures decay | Good |
| Signal lifecycle stages | Clear progression from Fresh → Resolving | Good |
| Shared filters above tabs | Persists state across Long/Short switching | Good |

---
*Last updated: 2026-01-24 after v2.0 milestone*
