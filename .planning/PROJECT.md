# AssetPicker

## What This Is

A personal crypto screening tool that visualizes RSI (Relative Strength Index) against liquidity metrics to identify potential investment opportunities. Displays a scatter plot where position encodes daily RSI vs volume/market-cap ratio, and color encodes weekly RSI alignment—making it easy to spot oversold or overbought outliers at a glance.

## Core Value

Surface crypto assets where both daily AND weekly RSI align in extreme zones (both oversold or both overbought) with adequate liquidity—the strongest potential signals.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Scatter plot with daily RSI (x-axis) vs volume/mcap ratio (y-axis)
- [ ] Color encoding for weekly RSI (green=oversold → red=overbought)
- [ ] Visual zone shading for oversold (<30) and overbought (>70) regions
- [ ] Tooltip on hover showing coin stats (name, price, RSI values, volume, mcap)
- [ ] "Potential Opportunities" list below chart (daily RSI < 30)
- [ ] "Exercise Caution" list below chart (daily RSI > 70)
- [ ] Highlight coins where both daily AND weekly RSI align in extreme zones
- [ ] JSON config file for watchlist management (30-50 coins)
- [ ] Manual refresh button with timestamp display
- [ ] CoinGecko Pro API integration for market data

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

**RSI calculation**: Standard 14-period RSI formula. Daily RSI uses daily closes, weekly RSI uses weekly closes.

## Constraints

- **API**: CoinGecko Pro — user has existing subscription
- **Stack**: Python + Streamlit + Plotly — fast to build, interactive charts
- **Watchlist size**: 30-50 coins — balances coverage with API efficiency
- **Refresh model**: On-demand only — daily/weekly signals don't need real-time

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Volume/MCap ratio for Y-axis | Normalized liquidity metric comparable across market caps | — Pending |
| Color encoding for weekly RSI | Enables 3D visualization on 2D plane, shows timeframe alignment | — Pending |
| Streamlit over React | Faster to build, Plotly integration, sufficient for personal tool | — Pending |
| JSON watchlist over UI | Simpler implementation, easy to edit manually | — Pending |
| Classic 30/70 RSI thresholds | Well-understood, standard interpretation | — Pending |

---
*Last updated: 2025-01-23 after initialization*
