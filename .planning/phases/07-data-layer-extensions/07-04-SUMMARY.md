---
phase: 07-data-layer-extensions
plan: 04
subsystem: indicators
tags: [signal-lifecycle, opportunity-score, decay, confluence, scoring]

requires:
  - phase: 07-data-layer-extensions
    provides: Statistical analysis, divergence scoring, sector classification
provides:
  - Signal lifecycle classification (fresh/confirmed/extended/resolving)
  - Opportunity decay score with confluence multipliers
  - Complete Phase 7 data layer for Phase 14 consumption
affects: [phase-11-signal-display, phase-14-leaderboard]

tech-stack:
  added: []
  patterns: [signal-aging-classification, composite-scoring-formula]

key-files:
  created: []
  modified: [src/indicators.py]

key-decisions:
  - "Lifecycle states: fresh (1-2d), confirmed (3-5d), extended (6+d)"
  - "Freshness decay: 1.0 → 0.8 → 0.6 → 0.4 → 0.3 at 14+ days"
  - "Confluence bonuses match Phase 14 roadmap spec exactly"

patterns-established:
  - "Opportunity scoring formula: base * freshness * confluence"
  - "Missing factors default to neutral (no penalty)"

issues-created: []

duration: 2min
completed: 2026-01-24
---

# Phase 7 Plan 4: Signal Lifecycle & Decay Score Summary

**Signal lifecycle classification with emoji states and composite opportunity scoring using freshness decay and confluence multipliers**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-24T11:00:00Z
- **Completed:** 2026-01-24T11:02:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- `classify_signal_lifecycle()` detects fresh/confirmed/extended/resolving states
- Handles both oversold (<threshold) and overbought (>threshold) signals
- `calculate_opportunity_score()` implements Phase 14 roadmap formula
- Freshness decay from 1.0 (fresh) to 0.3 (stale at 14+ days)
- Confluence multipliers: weekly extreme, divergence, volatility, sector, funding

## Task Commits

Each task was committed atomically:

1. **Task 1: Signal Lifecycle State** - `9272437` (feat)
2. **Task 2: Opportunity Decay Score** - `cb3c4e9` (feat)

**Plan metadata:** (this commit) (docs: complete plan)

## Files Created/Modified

- `src/indicators.py` - Added classify_signal_lifecycle(), calculate_opportunity_score()

## Decisions Made

- Signal lifecycle thresholds: fresh (1-2d), confirmed (3-5d), extended (6+d)
- Resolving state: crossed back within last 2 periods, moving toward 50
- Emoji mapping: fresh=new, confirmed=checkmark, extended=hourglass, resolving=arrow
- Confluence bonuses exactly match Phase 14 roadmap spec

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Phase 7 Complete

All 10 Data Layer calculations implemented:

1. Regime Transition Detection (07-01)
2. RSI Acceleration (07-01)
3. Z-Score Thresholds (07-01)
4. Mean Reversion Probability (07-02)
5. Beta-Adjusted Relative Strength (07-02)
6. Volatility Regime (07-02)
7. Sector Classification (07-03)
8. Multi-Timeframe Divergence (07-03)
9. Signal Lifecycle State (07-04)
10. Opportunity Decay Score (07-04)

New modules: `src/indicators.py`, `src/sectors.py`

## Next Phase Readiness

- Complete data layer ready for Phase 8: Funding Rate Integration
- All scoring calculations ready for Phase 14: Opportunity Leaderboard
- Signal lifecycle ready for Phase 11: Signal Lifecycle Display

---
*Phase: 07-data-layer-extensions*
*Completed: 2026-01-24*
