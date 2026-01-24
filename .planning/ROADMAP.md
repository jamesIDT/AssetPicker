# Roadmap: AssetPicker

## Overview

Build a Python/Streamlit webapp that visualizes crypto RSI against liquidity metrics to spot investment opportunities. v1.0 delivered core RSI scatter plot. v2.0 adds advanced screening: regime detection, divergence scoring, sector analysis, funding rates, and opportunity ranking.

## Domain Expertise

None (crypto/trading domain knowledge embedded in feature specs)

## Milestones

- ✅ **v1.0 MVP** - Phases 1-6 (shipped 2026-01-23)
- ✅ **v2.0 Advanced Screening** - Phases 7-14 (shipped 2026-01-24)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (7.1, 7.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1-6: v1.0 MVP** - Core RSI scatter plot with weekly alignment (SHIPPED)
- [x] **Phase 7: Data Layer Extensions** - Calculations for regime, acceleration, z-scores, sectors, beta
- [x] **Phase 8: Funding Rate Integration** - Binance/Bybit API for funding rates + open interest
- [x] **Phase 9: Visual Marker System** - Bull/bear divergence icons with scoring visualization
- [x] **Phase 10: Main Chart Enhancements** - Regime banner, beta-adjusted colors, sector strength
- [x] **Phase 11: Signal Lifecycle Display** - Combined lifecycle badges + volatility context view
- [x] **Phase 12: Sector Momentum View** - Sector rotation flow visualization
- [x] **Phase 13: Acceleration Quadrant** - RSI acceleration + volatility regime new quadrant
- [x] **Phase 14: Opportunity Leaderboard** - Decay score ranked table with all factors

## Phase Details

<details>
<summary>✅ v1.0 MVP (Phases 1-6) — SHIPPED 2026-01-23</summary>

### Phase 1: Foundation
**Goal**: Project structure, Streamlit app, config loading
**Status**: Complete

### Phase 2: CoinGecko Integration
**Goal**: API client for market data and OHLC history
**Status**: Complete

### Phase 3: RSI Calculation
**Goal**: Wilder's 14-period RSI for daily and weekly timeframes
**Status**: Complete

### Phase 4: Core Visualization
**Goal**: Plotly scatter plot with RSI vs liquidity
**Status**: Complete

### Phase 5: Interaction & Lists
**Goal**: Tooltips, opportunity lists, refresh button
**Status**: Complete

### Phase 6: Polish
**Goal**: Visual refinements, error handling, empty states
**Status**: Complete

</details>

<details>
<summary>✅ v2.0 Advanced Screening (Phases 7-14) — SHIPPED 2026-01-24</summary>

See [v2.0 Archive](milestones/v2.0-ROADMAP.md) for full details.

**Key Accomplishments:**
- Multi-factor opportunity scoring with composite decay formula
- Visual divergence markers (+/◆) with ring-based scoring
- Sector rotation detection with momentum signals
- Acceleration Quadrant identifying "coiled spring" opportunities
- Signal lifecycle classification with conviction ratings
- Funding rate confluence from Binance/Bybit APIs

</details>

---

## Progress

**Execution Order:**
Phases execute in numeric order: 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 1/1 | Complete | 2026-01-23 |
| 2. CoinGecko Integration | v1.0 | 1/1 | Complete | 2026-01-23 |
| 3. RSI Calculation | v1.0 | 1/1 | Complete | 2026-01-23 |
| 4. Core Visualization | v1.0 | 1/1 | Complete | 2026-01-23 |
| 5. Interaction & Lists | v1.0 | 1/1 | Complete | 2026-01-23 |
| 6. Polish | v1.0 | 1/1 | Complete | 2026-01-23 |
| 7. Data Layer Extensions | v2.0 | 4/4 | Complete | 2026-01-24 |
| 8. Funding Rate Integration | v2.0 | 2/2 | Complete | 2026-01-24 |
| 9. Visual Marker System | v2.0 | 1/1 | Complete | 2026-01-24 |
| 10. Main Chart Enhancements | v2.0 | 2/2 | Complete | 2026-01-24 |
| 11. Signal Lifecycle Display | v2.0 | 1/1 | Complete | 2026-01-24 |
| 12. Sector Momentum View | v2.0 | 1/1 | Complete | 2026-01-24 |
| 13. Acceleration Quadrant | v2.0 | 1/1 | Complete | 2026-01-24 |
| 14. Opportunity Leaderboard | v2.0 | 1/1 | Complete | 2026-01-24 |
