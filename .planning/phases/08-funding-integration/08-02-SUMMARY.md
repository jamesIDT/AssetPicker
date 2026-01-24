---
phase: 08-funding-integration
plan: 02
subsystem: indicators
tags: [funding, positioning, confluence, rsi, squeeze-risk]

requires:
  - phase: 08-01
    provides: BinanceFundingClient for funding rates and OI data
provides:
  - Positioning matrix with crowded status and squeeze risk
  - Funding confluence detection for RSI signals
  - get_confluence_factors() for opportunity scoring integration
affects: [14-opportunity-scoring, ui-signals]

tech-stack:
  added: []
  patterns: [confluence-detection, multi-factor-analysis]

key-files:
  created: []
  modified: [src/funding.py, src/indicators.py]

key-decisions:
  - "Crowded threshold at 0.03% funding rate"
  - "Squeeze risk levels: high (>10% OI change), medium (>5%), low (>0%)"
  - "Bullish confluence: oversold RSI + negative funding (shorts paying)"
  - "Bearish confluence: overbought RSI + positive funding (longs paying)"

patterns-established:
  - "Confluence detection pattern: combine multiple signals for confirmation"

issues-created: []

duration: 2min
completed: 2026-01-24
---

# Phase 8 Plan 02: Positioning Matrix & Confluence Summary

**Positioning matrix with crowded detection and squeeze risk, plus funding confluence for RSI signals**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-24T03:42:05Z
- **Completed:** 2026-01-24T03:44:18Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Positioning matrix identifies crowded long/short with 0-100 intensity score
- Squeeze risk detection combines funding extremes with OI increases
- Funding confluence detection aligns oversold/overbought RSI with funding direction
- get_confluence_factors() aggregates all factors for opportunity scoring

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Positioning Matrix** - `d50fe20` (feat)
2. **Task 2: Add Funding Confluence Detection** - `18aac30` (feat)

**Plan metadata:** (pending)

## Files Created/Modified

- `src/funding.py` - Added PositioningData, calculate_positioning(), get_positioning_for_coins()
- `src/indicators.py` - Added detect_funding_confluence(), get_confluence_factors()

## Decisions Made

- Crowded threshold at 0.03% (0.0003 decimal) - aligns with industry standard
- Squeeze risk requires both crowded status AND positive OI change
- Funding confluence strength based on absolute funding rate intensity

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Next Phase Readiness

Phase 8 complete. All deliverables achieved:
1. Funding Rate Fetcher
2. Open Interest Changes
3. Positioning Matrix
4. Confluence Detection

Ready for Phase 9: Sector Analysis.

---
*Phase: 08-funding-integration*
*Completed: 2026-01-24*
