---
phase: 07-data-layer-extensions
plan: 01
subsystem: indicators
tags: [rsi, volatility, regime, atr, acceleration]

# Dependency graph
requires:
  - phase: 06-polish
    provides: Core RSI calculation pattern (Wilder's smoothing)
provides:
  - detect_regime function for bull/bear/transition state
  - calculate_rsi_acceleration for velocity and acceleration
  - detect_volatility_regime for ATR compression/expansion
affects: [07-02, 07-03, 07-04, 10, 13, 14]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Pure calculation functions with None for insufficient data"]

key-files:
  created: [src/indicators.py]
  modified: []

key-decisions:
  - "Transition detection based on 50-crossing in last 3 periods"
  - "Momentum threshold of 3 RSI points for rising/falling"
  - "Volatility regime thresholds: <0.7 compressed, >1.3 expanded"

patterns-established:
  - "Indicator functions return dict | None for consistent error handling"

issues-created: []

# Metrics
duration: 2min
completed: 2026-01-24
---

# Phase 7 Plan 1: Core Indicators Foundation Summary

**New indicators.py module with regime detection, RSI acceleration, and volatility regime calculations**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-24T09:00:00Z
- **Completed:** 2026-01-24T09:02:00Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- Created new `src/indicators.py` module with 3 pure calculation functions
- Regime detection distinguishes bull/bear/transition with momentum direction
- RSI acceleration provides velocity and second derivative for momentum analysis
- Volatility regime uses normalized ATR to detect compressed/normal/expanded states

## Task Commits

All three functions implemented in single module creation:

1. **Task 1: Regime Transition Detection** - `b681831` (feat)
2. **Task 2: RSI Acceleration** - included in `b681831`
3. **Task 3: Volatility Regime Detection** - included in `b681831`

_Note: All functions implemented together as they share the same module_

## Files Created/Modified
- `src/indicators.py` - New module with detect_regime, calculate_rsi_acceleration, detect_volatility_regime

## Decisions Made
- Used 3-point threshold for momentum direction (rising/falling) - provides meaningful signal without noise
- Transition state triggers on 50-crossing within 3 periods - captures regime changes in progress
- Volatility regime uses 4x period lookback for average ATR - provides stable baseline
- Simplified True Range calculation (close-to-close) since we only have close prices from CoinGecko

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Next Phase Readiness
- Core indicator foundation complete
- Ready for plan 07-02 (Z-Score and Statistical Analysis)
- Functions are pure calculations with no I/O, ready for integration

---
*Phase: 07-data-layer-extensions*
*Completed: 2026-01-24*
