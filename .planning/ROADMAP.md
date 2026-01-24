# Roadmap: AssetPicker

## Overview

Build a Python/Streamlit webapp that visualizes crypto RSI against liquidity metrics to spot investment opportunities. v1.0 delivered core RSI scatter plot. v2.0 adds advanced screening: regime detection, divergence scoring, sector analysis, funding rates, and opportunity ranking.

## Domain Expertise

None (crypto/trading domain knowledge embedded in feature specs)

## Milestones

- ✅ **v1.0 MVP** - Phases 1-6 (shipped 2026-01-23)
- 🚧 **v2.0 Advanced Screening** - Phases 7-14 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (7.1, 7.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1-6: v1.0 MVP** - Core RSI scatter plot with weekly alignment (SHIPPED)
- [x] **Phase 7: Data Layer Extensions** - Calculations for regime, acceleration, z-scores, sectors, beta
- [x] **Phase 8: Funding Rate Integration** - Binance/Bybit API for funding rates + open interest
- [ ] **Phase 9: Visual Marker System** - Bull/bear divergence icons with scoring visualization
- [ ] **Phase 10: Main Chart Enhancements** - Regime banner, beta-adjusted colors, sector strength
- [ ] **Phase 11: Signal Lifecycle Display** - Combined lifecycle badges + volatility context view
- [ ] **Phase 12: Sector Momentum View** - Sector rotation flow visualization
- [ ] **Phase 13: Acceleration Quadrant** - RSI acceleration + volatility regime new quadrant
- [ ] **Phase 14: Opportunity Leaderboard** - Decay score ranked table with all factors

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

### 🚧 v2.0 Advanced Screening (In Progress)

**Milestone Goal:** Transform basic RSI screener into a multi-dimensional opportunity detection system with regime awareness, divergence detection, sector analysis, funding rate confluence, and composite scoring.

---

### Phase 7: Data Layer Extensions
**Goal**: Build all calculation engines before any UI work
**Depends on**: Phase 6 (v1.0 complete)
**Research**: Likely (z-score statistics, beta calculation formulas)
**Research topics**: Statistical z-score implementation, rolling beta calculation, sector classification approach
**Plans**: TBD

Calculations to implement:
1. **Regime Transition Detection** — BTC weekly RSI trend + momentum for bull/bear/transition states
2. **RSI Acceleration** — Second derivative of RSI (velocity + acceleration)
3. **Z-Score Thresholds** — Per-coin rolling mean/stddev for statistical extreme detection
4. **Mean Reversion Probability** — Historical success rate at similar RSI levels
5. **Beta-Adjusted Relative Strength** — Each coin's beta to BTC, expected vs actual RSI
6. **Sector Classification** — Group coins by narrative (L1, DeFi, AI, etc.) with sector-level RSI
7. **Multi-Timeframe Divergence** — Daily + weekly divergence detection with scoring (1/2/4)
8. **Signal Lifecycle State** — Fresh/Confirmed/Extended/Resolving classification
9. **Volatility Regime** — ATR compression/expansion detection
10. **Opportunity Decay Score** — Composite formula with time decay

---

### Phase 8: Funding Rate Integration
**Goal**: Integrate free Binance/Bybit APIs for perpetual futures positioning data
**Depends on**: Phase 7
**Research**: Likely (external API)
**Research topics**: Binance funding rate API, Bybit funding rate API, open interest endpoints, rate limits
**Plans**: TBD

Deliverables:
1. **Funding Rate Fetcher** — Get current funding rates for coins with perp markets
2. **Open Interest Changes** — Track OI increases/decreases
3. **Positioning Matrix** — Combine funding + OI into crowded long/short detection
4. **Confluence Detection** — Flag when funding aligns with RSI extremes

---

### Phase 9: Visual Marker System
**Goal**: Implement custom divergence icons with scoring visualization on scatter plot
**Depends on**: Phase 7 (divergence scores calculated)
**Research**: Unlikely (Plotly customization)
**Plans**: TBD

Visual encoding spec:
- **Bullish divergence**: Plus sign (+) shape instead of circle
- **Bearish divergence**: Diamond (◆) shape instead of circle
- **Score 1 (single timeframe)**: Bold inner shape only
- **Score 2 (strong single)**: Bold inner + thin outer ring
- **Score 4 (multi-timeframe confluence)**: Bold inner + bold outer ring
- **Neutral (no divergence)**: Standard circle

Implementation:
1. Custom Plotly marker symbols
2. Score-based sizing/layering
3. Legend explaining the visual system
4. Tooltip includes divergence details

---

### Phase 10: Main Chart Enhancements
**Goal**: Enhance existing scatter plot with regime context, beta coloring, sector strength
**Depends on**: Phase 7, Phase 8
**Research**: Unlikely (extending existing Plotly code)
**Plans**: TBD

Enhancements:
1. **Regime Banner** — Persistent header showing current regime (Bull ↗, Bull ↘, Bear ↗, Bear ↘, Transition)
2. **Beta-Adjusted Coloring** — Optional mode: color by residual (underperforming/expected/outperforming vs BTC beta)
3. **Sector-Relative Badges** — Small indicator if coin is best/worst in its sector
4. **Z-Score Labels** — Optional display of statistical extreme (-2.3σ) next to coin symbols
5. **Toggle Controls** — UI switches between color modes (weekly RSI vs beta residual)

---

### Phase 11: Signal Lifecycle Display
**Goal**: New combined view showing signal lifecycle + volatility context (your ideas #7 + #8)
**Depends on**: Phase 7
**Research**: Unlikely (internal UI)
**Plans**: TBD

Display components:
1. **Signal Lifecycle Table** — All coins with extreme RSI, showing:
   - Lifecycle stage badge (🆕 Fresh, ✓ Confirmed, ⏳ Extended, ↗ Resolving)
   - Days in zone
   - Price change since signal
   - Mean reversion probability from historical data
2. **Volatility Context Column** — Show volatility regime (⚡ Compressed, 🌊 High Vol)
3. **Combined Interpretation** — Fresh + Compressed = highest conviction
4. **Explanatory UI** — Brief description of what each badge means

---

### Phase 12: Sector Momentum View
**Goal**: Sector rotation visualization (your idea #9)
**Depends on**: Phase 7
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Display components:
1. **Sector Bar Chart** — Horizontal bars showing sector RSI
2. **7-Day Momentum Arrow** — Direction indicator for each sector
3. **Rotation Signal** — Highlight sectors: RSI < 35 AND 7d change > 0 (just turning)
4. **Time Since Bottom** — Days since sector hit lowest RSI
5. **Drill-Down** — Click sector to filter main scatter to just those coins

---

### Phase 13: Acceleration Quadrant
**Goal**: New quadrant display combining RSI acceleration + volatility regime (your ideas #10 + #11)
**Depends on**: Phase 7
**Research**: Unlikely (Plotly quadrant similar to main chart)
**Plans**: TBD

Axes:
- **X-axis**: RSI Acceleration (negative = decelerating, positive = accelerating)
- **Y-axis**: Volatility Ratio (compressed < 0.7 | normal | expanded > 1.3)

Quadrants:
| Position | Meaning |
|----------|---------|
| Top-Right | Accelerating + High Vol = Explosive move in progress |
| Top-Left | Decelerating + High Vol = Move exhausting |
| Bottom-Right | Accelerating + Compressed = Coiled spring (BEST SIGNAL) |
| Bottom-Left | Decelerating + Compressed = Dormant |

Visual:
1. Same scatter plot style as main chart
2. Quadrant labels/colors
3. Color dots by current RSI level
4. Tooltips with full context

---

### Phase 14: Opportunity Leaderboard
**Goal**: Final integration — ranked table with composite decay score (your idea #12)
**Depends on**: All prior phases (7-13)
**Research**: Unlikely (internal aggregation)
**Plans**: TBD

Score formula:
```
Score = Base_Score × Freshness_Multiplier × Confluence_Multiplier

Where:
Base_Score = abs(Z-score of RSI)
Freshness = 1.0 if signal < 3 days, decay to 0.3 at 14+ days
Confluence = 1.0 + sum of:
  - Weekly RSI also extreme: +0.2
  - Divergence present: +0.3 (or +0.5 for multi-TF)
  - Positive decorrelation: +0.2
  - Volatility compressed: +0.2
  - Sector turning: +0.1
  - Funding alignment: +0.2
```

Display:
1. **Ranked Table** — All coins sorted by opportunity score (highest first)
2. **Score Breakdown** — Expandable row showing factor contributions
3. **Bull/Bear Split** — Tabs for long opportunities vs short opportunities
4. **Quick Filters** — Filter by sector, minimum score, signal age
5. **Explanatory Footer** — How the score works

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
| 9. Visual Marker System | v2.0 | 0/TBD | Not started | - |
| 10. Main Chart Enhancements | v2.0 | 0/TBD | Not started | - |
| 11. Signal Lifecycle Display | v2.0 | 0/TBD | Not started | - |
| 12. Sector Momentum View | v2.0 | 0/TBD | Not started | - |
| 13. Acceleration Quadrant | v2.0 | 0/TBD | Not started | - |
| 14. Opportunity Leaderboard | v2.0 | 0/TBD | Not started | - |
