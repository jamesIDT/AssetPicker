# Roadmap: AssetPicker

## Overview

Build a Python/Streamlit webapp that visualizes crypto RSI against liquidity metrics to spot investment opportunities. v1.0 delivered core RSI scatter plot. v2.0 adds advanced screening: regime detection, divergence scoring, sector analysis, funding rates, and opportunity ranking.

## Domain Expertise

None (crypto/trading domain knowledge embedded in feature specs)

## Milestones

- ✅ **v1.0 MVP** - Phases 1-6 (shipped 2026-01-23)
- ✅ **v2.0 Advanced Screening** - Phases 7-14 (shipped 2026-01-24)
- ✅ **v3.0 UX Dashboard Redesign** - Phases 15-20 (shipped 2026-01-24)
- 🚧 **v4.0 Multi-Timeframe Divergence** - Phases 21-26 (in progress)

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
- [x] **Phase 15: Design System** - CSS tokens, dark theme, typography, panel styling
- [x] **Phase 16: Layout Restructure** - Side-by-side quadrants, new information hierarchy
- [x] **Phase 17: Chart Theming** - Plotly charts updated to dark theme with new palette
- [x] **Phase 18: Component Refinement** - Restyle leaderboard, sector momentum, lifecycle panels
- [x] **Phase 19: Legends & Onboarding** - Collapsible "How to Read" panel, icon legends
- [x] **Phase 20: Polish & Integration** - Final visual polish, cleanup redundant elements
- [x] **Phase 21: Hourly Data Integration** - Add hourly OHLC fetch from CoinGecko with caching
- [ ] **Phase 22: Multi-Timeframe Candles** - Aggregate 4h/12h/3d candles, RSI & divergence for all 6 TFs
- [ ] **Phase 23: Segmented Ring Viz** - Multi-trace arc rendering around scatter markers
- [ ] **Phase 24: Timeframe Highlight** - Sidebar selector with opacity highlight mode
- [ ] **Phase 25: Divergence Matrix** - Grid component sorted by divergence count with tooltips
- [ ] **Phase 26: Polish & Performance** - Optimize rendering, test with full dataset

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

### ✅ v3.0 UX Dashboard Redesign (SHIPPED 2026-01-24)

**Milestone Goal:** Transform AssetPicker into a professional crypto analyst dashboard with hypothesis-validator inspired dark theme, side-by-side quadrants, and improved information hierarchy.

**Design Reference:** hypothesis-validator project (fonts, bevels, edges)
**Color Palette:** Dark gray (#4A4A4A), Silver (#CBCBCB), Cream (#FFFFE3), Slate blue (#6D8196), Yellow-orange accent (#FFB020)
**Constraint:** Preserve existing RSI red-green spectrum in chart data visualization

#### Phase 15: Design System (COMPLETE)
**Goal**: Create CSS tokens and base styling infrastructure for dark theme
**Depends on**: v2.0 complete
**Research**: Unlikely (Streamlit CSS injection patterns established)
**Plans**: 1 plan

Plans:
- [x] 15-01: CSS tokens + comprehensive base styling

#### Phase 16: Layout Restructure (COMPLETE)
**Goal**: Implement side-by-side quadrants layout with new information hierarchy
**Depends on**: Phase 15
**Research**: Unlikely (Streamlit columns/containers known)
**Plans**: 1 plan

Key changes:
- RSI Scatter + Acceleration Quadrant side-by-side as hero
- Market Regime banner always visible at top
- Opportunity Leaderboard + Sector Momentum below charts
- Signal Lifecycle collapsed by default

Plans:
- [x] 16-01: Layout restructure with hero charts and visible data panels

#### Phase 17: Chart Theming (COMPLETE)
**Goal**: Update Plotly charts to dark theme with new color palette
**Depends on**: Phase 15
**Research**: Unlikely (Plotly theming documented)
**Plans**: 1 plan

Changes:
- Dark backgrounds (paper_bgcolor, plot_bgcolor)
- Cream text on dark
- Light marker outlines for pop on dark
- Preserved RdYlGn colorscale (more vibrant on dark)

Plans:
- [x] 17-01: Dark theme for RSI Scatter, Acceleration Quadrant, Sector Momentum charts

#### Phase 18: Component Refinement
**Goal**: Restyle individual UI components to match design system
**Depends on**: Phase 16, Phase 17
**Research**: Unlikely (internal styling patterns)
**Plans**: TBD

Components:
- Opportunity Leaderboard (visual score bars, factor badges)
- Sector Momentum panel
- Signal Lifecycle display
- Filter controls

Plans:
- [x] 18-01: Restyle regime banner, leaderboard score bars, conviction badges

#### Phase 19: Legends & Onboarding (COMPLETE)
**Goal**: Replace inline chart legends with collapsible "How to Read" panel
**Depends on**: Phase 17
**Research**: Unlikely (UI patterns established)
**Plans**: 1 plan

Changes:
- Remove two large inline legend annotations from scatter chart
- Add collapsible legend panel with quadrant/marker/color explanations
- Minimal icon legend in chart corner for experienced users

Plans:
- [x] 19-01: Collapsible How to Read panel + minimal corner legend

#### Phase 20: Polish & Integration (COMPLETE)
**Goal**: Final visual polish, responsive testing, remove redundant elements
**Depends on**: Phase 18, Phase 19
**Research**: Unlikely (internal refinement)
**Plans**: 1 plan

Tasks:
- Remove redundant "Potential Opportunities" / "Exercise Caution" lists (merged into Leaderboard)
- Consistent spacing and alignment
- Loading state styling
- Error state styling

Plans:
- [x] 20-01: Remove redundant lists, style alerts, polish spacing

---

### 🚧 v4.0 Multi-Timeframe Divergence (In Progress)

**Milestone Goal:** Extend divergence detection to 6 timeframes (1h, 4h, 12h, 1d, 3d, 1w) with visual segmented rings on scatter plot and a dedicated divergence analysis matrix.

**Spec:** .planning/2025-01-25-multi-timeframe-divergence-display.md

#### Phase 21: Hourly Data Integration

**Goal**: Add hourly OHLC data fetch from CoinGecko with appropriate caching
**Depends on**: v3.0 complete
**Research**: Likely (CoinGecko hourly endpoint specifics)
**Research topics**: CoinGecko hourly OHLC endpoint, rate limits, data format
**Plans**: TBD

Plans:
- [x] 21-01: Hourly OHLC pipeline with caching

#### Phase 22: Multi-Timeframe Candles

**Goal**: Aggregate 4h, 12h, 3d candles from raw data; calculate RSI and divergence for all 6 timeframes
**Depends on**: Phase 21
**Research**: Unlikely (existing RSI/divergence patterns)
**Plans**: TBD

Plans:
- [ ] 22-01: TBD

#### Phase 23: Segmented Ring Viz

**Goal**: Implement segmented ring visualization around scatter markers (6 segments, one per timeframe)
**Depends on**: Phase 22
**Research**: Likely (Plotly arc/shape rendering)
**Research topics**: Plotly scatterpolar, custom shapes, multi-trace performance
**Plans**: TBD

Plans:
- [ ] 23-01: TBD

#### Phase 24: Timeframe Highlight

**Goal**: Add timeframe selector to sidebar with highlight mode (selected TF glows, others fade)
**Depends on**: Phase 23
**Research**: Unlikely (existing sidebar patterns)
**Plans**: TBD

Plans:
- [ ] 24-01: TBD

#### Phase 25: Divergence Matrix

**Goal**: Build divergence analysis grid component sorted by divergence count with cell tooltips
**Depends on**: Phase 22
**Research**: Unlikely (Streamlit dataframe styling)
**Plans**: TBD

Plans:
- [ ] 25-01: TBD

#### Phase 26: Polish & Performance

**Goal**: Optimize ring rendering performance, test with full 48-coin dataset, handle edge cases
**Depends on**: Phase 23, 24, 25
**Research**: Unlikely (internal refinement)
**Plans**: TBD

Plans:
- [ ] 26-01: TBD

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
| 15. Design System | v3.0 | 1/1 | Complete | 2026-01-24 |
| 16. Layout Restructure | v3.0 | 1/1 | Complete | 2026-01-24 |
| 17. Chart Theming | v3.0 | 1/1 | Complete | 2026-01-24 |
| 18. Component Refinement | v3.0 | 1/1 | Complete | 2026-01-24 |
| 19. Legends & Onboarding | v3.0 | 1/1 | Complete | 2026-01-24 |
| 20. Polish & Integration | v3.0 | 1/1 | Complete | 2026-01-24 |
| 21. Hourly Data Integration | v4.0 | 1/1 | Complete | 2026-01-25 |
| 22. Multi-Timeframe Candles | v4.0 | 0/? | Not started | - |
| 23. Segmented Ring Viz | v4.0 | 0/? | Not started | - |
| 24. Timeframe Highlight | v4.0 | 0/? | Not started | - |
| 25. Divergence Matrix | v4.0 | 0/? | Not started | - |
| 26. Polish & Performance | v4.0 | 0/? | Not started | - |
