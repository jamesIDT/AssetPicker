---
phase: 17-chart-theming
plan: 01
subsystem: ui
tags: [plotly, dark-theme, charts, visualization]

requires:
  - phase: 15-design-system
    provides: CSS tokens and color palette for dark theme
  - phase: 16-layout-restructure
    provides: Dashboard layout with chart containers
provides:
  - Dark-themed RSI Scatter chart with cream text and light marker outlines
  - Dark-themed Acceleration Quadrant chart with consistent styling
  - Dark-themed Sector Momentum bar chart
affects: [18-table-styling, 19-sidebar-refinement]

tech-stack:
  added: []
  patterns: ["Dark theme Plotly charts with cream (#FFFFE3) text and rgba backgrounds"]

key-files:
  created: []
  modified:
    - src/charts.py
    - app.py

key-decisions:
  - "Use rgba(90,90,90,0.3) for plot_bgcolor to provide subtle contrast from paper_bgcolor"
  - "Increase quadrant shading opacity to 0.12-0.15 for visibility on dark backgrounds"
  - "Use light marker outlines (rgba white 0.4-0.6) instead of dark for pop on dark background"
  - "Preserve RdYlGn colorscale unchanged - works better on dark than light backgrounds"

patterns-established:
  - "Dark Plotly chart template: paper_bgcolor=#4A4A4A, plot_bgcolor=rgba(90,90,90,0.3)"
  - "Cream text: #FFFFE3 for axes, labels, colorbars, annotations"
  - "Grid lines: rgba(255,255,227,0.08) for subtle cream"
  - "Border/divider lines: rgba(255,255,227,0.15)"

issues-created: []

duration: 4min
completed: 2026-01-24
---

# Phase 17 Plan 01: Chart Theming Summary

**Dark-themed Plotly charts with cream text, subtle quadrant shading, and preserved RdYlGn colorscale for RSI visualization**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-24T14:54:13Z
- **Completed:** 2026-01-24T14:58:14Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- RSI Scatter chart updated with dark backgrounds, cream text, light marker outlines, and dark legend panels
- Acceleration Quadrant chart styled consistently with cream text and adjusted quadrant shading
- Sector Momentum bar chart themed with dark backgrounds and cream axis labels
- All charts maintain RdYlGn colorscale which is MORE vibrant on dark backgrounds

## Task Commits

Each task was committed atomically:

1. **Task 1: Update RSI Scatter chart theming** - `613347a` (feat)
2. **Task 2: Update Acceleration Quadrant chart theming** - `879fded` (feat)
3. **Task 3: Update Sector Momentum bar chart theming** - `0b00492` (feat)

## Files Created/Modified

- `src/charts.py` - Updated build_rsi_scatter() and build_acceleration_quadrant() with dark theme styling
- `app.py` - Updated Sector Momentum bar chart with dark theme styling

## Decisions Made

- **Plot background strategy:** Used rgba(90,90,90,0.3) for plot_bgcolor to provide subtle contrast from the #4A4A4A paper_bgcolor without being distracting
- **Quadrant shading:** Increased opacity from 0.06-0.08 to 0.10-0.15 for visibility on dark backgrounds (Coiled Spring quadrant gets 0.15 as it's the "best signal" zone)
- **Marker outlines:** Changed from dark (rgba black) to light (rgba white) for markers to pop on dark background
- **RdYlGn preservation:** Colorscale left unchanged - the red-yellow-green spectrum actually looks MORE vibrant against dark backgrounds

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- All three chart types now have consistent dark theme styling
- Ready for Phase 18 (Table Styling) to update dataframes and tables
- Color palette and text styling patterns established and can be reused

---
*Phase: 17-chart-theming*
*Completed: 2026-01-24*
