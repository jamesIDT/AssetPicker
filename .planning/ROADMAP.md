# Roadmap: AssetPicker

## Overview

Build a Python/Streamlit webapp that visualizes crypto RSI against liquidity metrics to spot investment opportunities. v1.0 delivered core RSI scatter plot. v2.0 adds advanced screening: regime detection, divergence scoring, sector analysis, funding rates, and opportunity ranking.

## Domain Expertise

None (crypto/trading domain knowledge embedded in feature specs)

## Milestones

- ✅ **v1.0 MVP** - Phases 1-6 (shipped 2026-01-23)
- ✅ **v2.0 Advanced Screening** - Phases 7-14 (shipped 2026-01-24)
- 🚧 **v3.0 UX Dashboard Redesign** - Phases 15-20 (in progress)

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
- [ ] **Phase 17: Chart Theming** - Plotly charts updated to dark theme with new palette
- [ ] **Phase 18: Component Refinement** - Restyle leaderboard, sector momentum, lifecycle panels
- [ ] **Phase 19: Legends & Onboarding** - Collapsible "How to Read" panel, icon legends
- [ ] **Phase 20: Polish & Integration** - Final visual polish, cleanup redundant elements

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

### 🚧 v3.0 UX Dashboard Redesign (In Progress)

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

#### Phase 17: Chart Theming
**Goal**: Update Plotly charts to dark theme with new color palette
**Depends on**: Phase 15
**Research**: Unlikely (Plotly theming documented)
**Plans**: TBD

Changes:
- Dark backgrounds (paper_bgcolor, plot_bgcolor)
- Cream text on dark
- Monospace font family
- Yellow-orange accent for highlights

Plans:
- [ ] 17-01: TBD

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
- [ ] 18-01: TBD

#### Phase 19: Legends & Onboarding
**Goal**: Replace inline chart legends with collapsible "How to Read" panel
**Depends on**: Phase 17
**Research**: Unlikely (UI patterns established)
**Plans**: TBD

Changes:
- Remove two large inline legend annotations from scatter chart
- Add collapsible legend panel with quadrant/marker/color explanations
- Minimal icon legend in chart corner for experienced users

Plans:
- [ ] 19-01: TBD

#### Phase 20: Polish & Integration
**Goal**: Final visual polish, responsive testing, remove redundant elements
**Depends on**: Phase 18, Phase 19
**Research**: Unlikely (internal refinement)
**Plans**: TBD

Tasks:
- Remove redundant "Potential Opportunities" / "Exercise Caution" lists (merged into Leaderboard)
- Consistent spacing and alignment
- Loading state styling
- Error state styling

Plans:
- [ ] 20-01: TBD

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
| 17. Chart Theming | v3.0 | 0/? | Not started | - |
| 18. Component Refinement | v3.0 | 0/? | Not started | - |
| 19. Legends & Onboarding | v3.0 | 0/? | Not started | - |
| 20. Polish & Integration | v3.0 | 0/? | Not started | - |
