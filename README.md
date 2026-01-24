# AssetPicker

A sophisticated cryptocurrency screening tool that identifies investment opportunities through multi-factor technical analysis. Built for personal use, AssetPicker goes beyond basic RSI screening to detect statistical extremes, market regime shifts, divergence confluences, and high-conviction trade setups.

**Version:** 2.0 Advanced Screening
**Stack:** Python + Streamlit + Plotly + CoinGecko Pro API

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Overview](#overview)
3. [Understanding the Main Dashboard](#understanding-the-main-dashboard)
4. [Feature Reference](#feature-reference)
   - [Market Regime Transition Detector](#1-market-regime-transition-detector)
   - [RSI Divergence Detection](#2-rsi-divergence-detection)
   - [Beta-Adjusted Relative Strength](#3-beta-adjusted-relative-strength)
   - [Z-Score Statistical Extremes](#4-z-score-statistical-extremes)
   - [Funding Rate Positioning](#5-funding-rate-positioning)
   - [Sector Rotation Analysis](#6-sector-rotation-analysis)
   - [Mean Reversion Probability](#7-mean-reversion-probability)
   - [Signal Lifecycle Tracking](#8-signal-lifecycle-tracking)
   - [Correlation Break Detection](#9-correlation-break-detection)
   - [RSI Acceleration](#10-rsi-acceleration)
   - [Volatility Regime Context](#11-volatility-regime-context)
   - [Opportunity Leaderboard](#12-opportunity-leaderboard)
5. [Interpreting the Scatter Plot](#interpreting-the-scatter-plot)
6. [Configuration](#configuration)
7. [Glossary](#glossary)

---

## Quick Start

### Prerequisites
- Python 3.9+
- CoinGecko Pro API key

### Installation

```bash
# Clone or download the project
cd AssetPicker

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "COINGECKO_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Overview

### What This App Does

AssetPicker monitors 48 cryptocurrency assets across four sectors (Majors, DeFi, AI, DeSci) and identifies potential investment opportunities using a multi-factor analysis system. Rather than relying on simple "RSI below 30 = buy" signals, it combines multiple confirming factors to surface high-conviction setups.

### Why These Signals Matter

Traditional RSI screening has a critical flaw: a coin at RSI 25 could be a great buying opportunity OR a value trap falling further. AssetPicker addresses this by:

1. **Contextualizing signals** - Is the broader market bullish or bearish? Is this coin's RSI normal for its volatility profile?
2. **Detecting confluence** - Do multiple independent signals agree? Daily AND weekly divergence is much stronger than daily alone.
3. **Tracking signal freshness** - A 2-day-old oversold signal is actionable; a 14-day-old one may be a value trap.
4. **Scoring opportunities** - Combines all factors into a single actionability score with time decay.

### Key Principle: Transitions > States

The most valuable signals aren't "we're in a bull market" but rather "the market regime is changing." By the time everyone knows it's bullish, the easy gains are gone. This app focuses on detecting transitions early.

---

## Understanding the Main Dashboard

When you load the app, you'll see several sections:

### Top Banner: Market Regime
Shows BTC's current regime state with a momentum indicator:
- **Bull ↗** - Bull market, strengthening
- **Bull ↘** - Bull market, but weakening (caution)
- **Bear ↗** - Bear market, but improving (watch for turn)
- **Bear ↘** - Bear market, deteriorating

### Main Chart: RSI Scatter Plot
The central visualization plots all 48 coins on two axes:
- **X-axis (Daily RSI):** 0-100 scale, with shaded zones at 30 (oversold) and 70 (overbought)
- **Y-axis (Vol/MCap Ratio):** Trading activity relative to market cap (log scale)

Colors indicate either Weekly RSI or Beta-Adjusted performance (toggle in controls).

### Signal Lists
Two columns showing:
- **Opportunities (RSI < 30):** Potentially oversold coins worth investigating
- **Caution (RSI > 70):** Potentially overbought coins to avoid or exit

### Expandable Sections
- **Signal Lifecycle Analysis:** Deep dive into signal freshness and conviction
- **Sector Momentum:** Rotation signals showing capital flow between sectors
- **Acceleration Quadrant:** Velocity × Volatility matrix for timing entries
- **Opportunity Leaderboard:** Ranked list of highest-conviction setups

---

## Feature Reference

### 1. Market Regime Transition Detector

**Purpose:** Detect when the market regime is changing, not just what regime we're in.

**How It Works:**

The app tracks BTC's weekly RSI and identifies four key states:

| Signal | Detection | What It Means |
|--------|-----------|---------------|
| **Regime Weakening** | BTC weekly RSI was >60, now crossing below 50 | Bull market may be ending. Reduce aggression on overbought signals. |
| **Regime Strengthening** | BTC weekly RSI was <40, now crossing above 50 | Bear market may be ending. Oversold signals become high-confidence. |
| **Regime Confirmed** | BTC weekly RSI sustained >60 for 4+ weeks | Strong bull. Buy the dips aggressively. |
| **Regime Deteriorating** | BTC weekly RSI sustained <40 for 4+ weeks | Strong bear. Oversold can get more oversold. |

**Momentum Arrow:**

The arrow next to the regime indicator shows whether momentum is accelerating or decelerating:
- **Bull ↗** = Bull and strengthening (high confidence)
- **Bull ↘** = Bull but weakening (increasing caution warranted)
- **Bear ↗** = Bear but improving (watch for reversal)
- **Bear ↘** = Bear and deteriorating (maximum caution)

**Why This Matters:**

A coin at RSI 25 during "Bear ↘" is very different from RSI 25 during "Bear ↗". The former might fall further; the latter might be catching the reversal early.

---

### 2. RSI Divergence Detection

**Purpose:** Identify when price and momentum disagree, signaling potential reversals.

**How It Works:**

A divergence occurs when price makes a new low but RSI makes a higher low (bullish), or price makes a new high but RSI makes a lower high (bearish). The app scans for divergences on two timeframes:

| Divergence Type | Score | Interpretation |
|-----------------|-------|----------------|
| Daily bullish divergence only | 1 | Weak signal, often fails |
| Weekly bullish divergence only | 2 | Moderate signal, longer-term |
| **Daily + Weekly bullish divergence** | **4** | **Strong confluence - high probability reversal** |
| Daily bearish + Weekly still bullish | 0 | Noise - weekly trend wins |

**Visual Indicators:**

On the scatter plot, coins with divergences show special markers:
- **◆ (Diamond):** Divergence present
- **+ (Plus):** Bullish divergence specifically
- **Ring around marker:** Strength indicator (stronger = more visible ring)

**Additional Factors Tracked:**

- **Age:** How many bars since divergence formed? Fresh (1-3 bars) is actionable. Stale (10+ bars) may have resolved.
- **Depth:** How extreme is the divergence? Price down 20% while RSI flat = strong. Price down 5% while RSI up slightly = weak.

---

### 3. Beta-Adjusted Relative Strength

**Purpose:** Compare a coin's RSI to what's *expected* given its relationship with BTC.

**The Problem It Solves:**

Different altcoins have different natural "betas" to BTC. SOL typically moves 1.5× BTC. LINK might move 0.8×. If BTC's RSI drops 20 points and SOL drops 30 points, that's exactly expected behavior for a 1.5 beta coin - not underperformance.

**How It Works:**

The app calculates each coin's historical beta to BTC (rolling 30-day correlation × relative volatility), then computes:

```
Expected RSI = 50 + Beta × (BTC_RSI - 50)
Residual = Actual RSI - Expected RSI
```

| Residual | Interpretation |
|----------|----------------|
| -15 or below | Underperforming even for its beta - genuine weakness or opportunity |
| ~0 | Moving exactly as expected - no signal |
| +15 or above | Outperforming its beta - showing genuine strength |

**Color Mode Toggle:**

Use the "Color by Beta Residual" toggle to switch the scatter plot colors from Weekly RSI (absolute) to Beta Residual (relative to BTC expectations):
- **Blue:** Underperforming expectations (potential opportunity if oversold)
- **Gray:** Moving as expected
- **Orange:** Outperforming expectations (genuine strength)

---

### 4. Z-Score Statistical Extremes

**Purpose:** Identify when a coin's RSI is statistically rare, not just below/above arbitrary thresholds.

**The Problem It Solves:**

Using fixed 30/70 thresholds ignores that different coins have different normal ranges. A coin that typically oscillates between RSI 40-60 being at RSI 35 is genuinely unusual. A naturally volatile coin at RSI 25 might be routine.

**How It Works:**

For each coin, calculate rolling mean and standard deviation of RSI over 90 days:

```
Z-Score = (Current_RSI - Mean_RSI) / StdDev_RSI
```

| Z-Score | Interpretation | Expected Frequency |
|---------|----------------|-------------------|
| Z < -2.0 | Extremely oversold for this coin | ~2% of days |
| Z < -1.5 | Notably oversold | ~7% of days |
| -1.0 < Z < 1.0 | Normal range | ~68% of days |
| Z > 1.5 | Notably overbought | ~7% of days |
| Z > 2.0 | Extremely overbought | ~2% of days |

**Visual Display:**

Z-scores appear as badges next to coin symbols: **"SOL: -2.3σ"** makes it immediately clear this is a statistically rare event.

**Why This Matters:**

A coin at -2.5 standard deviations is genuinely rare (about 1% of days). This is what you want to catch - not just "below 30" but "statistically exceptional for this specific asset."

---

### 5. Funding Rate Positioning

**Purpose:** Detect crowded trades using perpetual futures positioning data.

**Data Source:** Binance Futures API (free, public endpoints)

**The Positioning Matrix:**

Funding rates + open interest changes together tell a rich story:

| Funding Rate | OI Rising | OI Falling |
|--------------|-----------|------------|
| **Positive** (longs paying) | New longs entering - crowded long, squeeze risk ⚠️ | Longs closing - momentum exhaustion |
| **Negative** (shorts paying) | New shorts entering - crowded short, squeeze potential 🎯 | Shorts closing - covering rally may be ending |

**The Golden Signal:**

**Negative funding + Rising OI + Oversold RSI = Maximum confluence**

Everyone is piling into shorts on an already oversold asset. Short squeeze incoming.

**Visual Indicators:**

In tooltips and tables:
- 🎯 = "Crowded short + oversold" (high-conviction long opportunity)
- ⚠️ = "Crowded long + overbought" (high-conviction avoid/short)

---

### 6. Sector Rotation Analysis

**Purpose:** Identify which sectors capital is flowing into/out of.

**The Problem It Solves:**

Average sector RSI is static. What's more valuable is momentum flow - catching the sector that's been beaten down and is *just starting to turn*, not one that's already recovered.

**How It Works:**

For each sector (Majors, DeFi, AI, DeSci), the app calculates:
- Current sector RSI (market-cap weighted average)
- Sector RSI 7 days ago
- Sector momentum = Current - 7d ago

| Scenario | Signal |
|----------|--------|
| RSI 32, 7d change +8 | 🟢 Recovering from oversold (BUY sector) |
| RSI 28, 7d change -5 | Still falling, wait for turn |
| RSI 68, 7d change -12 | Rolling over from overbought (EXIT sector) |
| RSI 45, 7d change +15 | Strong momentum, may have missed entry |

**The Sweet Spot:**

**Sector RSI < 35 AND 7d change > 0** = Just starting to turn. This catches the rotation early.

**Additional Data:**

- **Days since sector bottom:** Early recovery (1-3 days) = fresh opportunity. Late recovery (10+ days) = may have missed it.
- **Sector leaders/laggards:** Which specific coins are driving the sector's performance?

---

### 7. Mean Reversion Probability

**Purpose:** Understand what historically happens when a coin reaches similar RSI levels.

**The Problem It Solves:**

"SOL is oversold" doesn't tell you what to expect. "SOL is in a zone that historically reverses 82% of the time with an average 12-day recovery" is actionable information.

**How It Works:**

For each coin, the app analyzes historical behavior at the current RSI level:
- **Mean reversion magnitude:** When RSI hit this level before, how much did it bounce?
- **Mean reversion time:** How long did the bounce take?
- **Success rate:** What % of times did it actually bounce vs continue falling?

**Example Display:**

```
SOL @ RSI 24
Historical outcome from this level:
  → Avg bounce: +45 RSI points
  → Avg time: 12 days
  → Success rate: 82%
```

**Confidence Levels:**

Mean reversion probability is combined with other factors:
- High probability + fresh signal + compressed volatility = ★★★ conviction
- High probability + stale signal + high volatility = ★☆☆ conviction

---

### 8. Signal Lifecycle Tracking

**Purpose:** Track how long a signal has been active and whether it's working.

**The Problem It Solves:**

Time alone isn't enough. Has the signal been confirmed by price? Is it strengthening or fading?

**Signal Lifecycle Stages:**

| Stage | Definition | Action |
|-------|------------|--------|
| **Fresh 🆕** (0-2 days) | Just entered extreme zone | Watch closely, prepare position |
| **Confirmed ✓** (3-5 days + price reaction) | RSI in zone AND price has stabilized/reversed | Execute trade |
| **Extended ⏳** (6+ days, no reversal) | Stuck in extreme zone | Likely value trap, avoid |
| **Resolving ↗** | Was extreme, now exiting zone | Move is happening, may be late |

**Price Confirmation:**

The app tracks price change since signal started:

| Scenario | Interpretation |
|----------|----------------|
| Signal 3 days old, price +8% | Signal was right, momentum confirming |
| Signal 3 days old, price -5% | Signal failing, not working |
| Signal 10 days old, price flat | Stale signal, no catalyst |

---

### 9. Correlation Break Detection

**Purpose:** Flag when a coin breaks from its normal BTC correlation.

**Why Correlation Breaks Matter:**

Decorrelation often precedes big moves. A coin that normally follows BTC suddenly doing its own thing suggests something unique is happening.

**Event Types:**

| Event | Detection | Meaning |
|-------|-----------|---------|
| **Positive Decorrelation** | BTC down, alt flat/up | Strong hands accumulating; alt has unique catalyst |
| **Negative Decorrelation** | BTC up, alt flat/down | Alt is weak; may have unique problems |
| **Correlation Spike** | Correlation jumps to >0.95 | Macro risk-off event; everything moving together; individual signals unreliable |
| **Correlation Collapse** | Correlation drops <0.3 | Alt on its own journey; worth investigating why |

**Visual Display:**

On the scatter plot, a subtle "D" icon appears for coins currently decorrelated from BTC. Tooltip shows correlation value and direction.

**The Most Interesting Signal:**

A decorrelation without obvious news suggests quiet accumulation. This is often more bullish than a decorrelation with a known catalyst.

---

### 10. RSI Acceleration

**Purpose:** Detect when momentum is changing before RSI crosses key levels.

**The Insight:**

RSI measures momentum. But the *rate of change* of momentum is often more predictive. When RSI is at 28 but acceleration is positive (RSI curve bending upward), the reversal is starting even though RSI is still "oversold."

**How It Works:**

```
RSI_velocity = RSI_today - RSI_3d_ago
RSI_acceleration = RSI_velocity_today - RSI_velocity_3d_ago
```

| State | Meaning |
|-------|---------|
| RSI low + acceleration positive | 🎯 Reversal starting - early entry signal |
| RSI low + acceleration negative | Still falling - wait |
| RSI high + acceleration negative | Reversal starting - early exit signal |
| RSI high + acceleration positive | Momentum continuing - hold |

**Visual Display:**

Acceleration appears as an arrow with angle:
- **Flat arrow:** No acceleration
- **Curved up arrow:** Positive acceleration (momentum improving)
- **Curved down arrow:** Negative acceleration (momentum deteriorating)

---

### 11. Volatility Regime Context

**Purpose:** Adjust signal confidence based on current volatility conditions.

**The Insight:**

Signals during volatility compression are much more valuable than signals during high volatility. When volatility is compressed and RSI hits an extreme, the subsequent move is often explosive. When volatility is already high, RSI extremes may just be noise.

**How It Works:**

```
Volatility Ratio = Current ATR / Average ATR (60-day)
```

| Volatility Ratio | Context |
|------------------|---------|
| < 0.7 | **Compressed** - Signals high-confidence, explosive moves likely ⚡ |
| 0.7 - 1.3 | Normal - Standard signal interpretation |
| > 1.3 | **Expanded** - Signals may be noise, market chaotic 🌊 |

**The Golden Setup:**

**Oversold RSI + Compressed volatility = Coiled spring ready to explode upward**

This is the highest-conviction setup: statistically oversold AND volatility suggests a big move is coming.

**Visual Display:**

Volatility context badges: "⚡ Compressed" or "🌊 High Vol"

---

### 12. Opportunity Leaderboard

**Purpose:** Rank all opportunities by actionability, combining all factors with time decay.

**The Scoring Formula:**

```
Final Score = Base Score × Freshness Multiplier × Confluence Multiplier
```

**Components:**

| Factor | Calculation |
|--------|-------------|
| **Base Score** | Absolute value of Z-score (how statistically extreme) |
| **Freshness Multiplier** | 1.0 if signal < 3 days old, decays exponentially to 0.3 at 14+ days |
| **Confluence Multiplier** | 1.0 + bonuses for confirming factors |

**Confluence Bonuses:**

| Factor | Bonus |
|--------|-------|
| Weekly RSI also extreme | +0.2 |
| Divergence present | +0.3 to +0.5 |
| Positive decorrelation | +0.2 |
| Volatility compressed | +0.2 |
| Sector turning | +0.1 |
| Funding alignment | +0.2 |

**Two Tabs:**

- **Long Opportunities:** Oversold coins ranked by score (buy candidates)
- **Short/Avoid:** Overbought coins ranked by score (exit/short candidates)

**Filter Controls:**

- **Sector filter:** Focus on specific sectors
- **Min score threshold:** Only show high-conviction opportunities

---

## Interpreting the Scatter Plot

The main scatter plot uses a **quadrant framework** to categorize coins:

```
                    Vol/MCap Ratio (Activity)
                           High
                            │
          Capitulation      │     Peak Momentum
         (Oversold +        │    (Overbought +
          High Activity)    │     High Activity)
                            │
    ────────────────────────┼────────────────────────
                            │                    RSI
         Forgotten          │     Quiet Pump
        (Oversold +         │    (Overbought +
         Low Activity)      │     Low Activity)
                            │
                           Low
              30                        70
```

### Quadrant Interpretations:

| Quadrant | RSI | Volume | Interpretation |
|----------|-----|--------|----------------|
| **Capitulation** | < 30 | High | Active selling, potential bottom, watch for reversal |
| **Forgotten** | < 30 | Low | Cheap but nobody cares, may need catalyst |
| **Peak Momentum** | > 70 | High | Maximum euphoria, high risk of correction |
| **Quiet Pump** | > 70 | Low | Rising without attention, potentially sustainable |

### Color Coding:

**Weekly RSI Mode (default):**
- **Green:** Weekly RSI < 40 (oversold on higher timeframe)
- **Yellow:** Weekly RSI 40-60 (neutral)
- **Red:** Weekly RSI > 60 (overbought on higher timeframe)

**Beta Residual Mode:**
- **Blue:** Underperforming BTC-adjusted expectations
- **Gray:** Performing as expected
- **Orange:** Outperforming BTC-adjusted expectations

---

## Configuration

### Watchlist

Edit `watchlist.json` to modify tracked coins:

```json
{
  "coins": [
    {"id": "bitcoin", "symbol": "BTC"},
    {"id": "ethereum", "symbol": "ETH"},
    {"id": "solana", "symbol": "SOL"}
  ]
}
```

The `id` must match CoinGecko's coin ID (found in their URL).

### Sectors

Sector assignments are defined in `src/sectors.py`. Modify `SECTOR_MAPPINGS` to recategorize coins:

```python
SECTOR_MAPPINGS = {
    "Majors": ["bitcoin", "ethereum", "solana", ...],
    "DeFi": ["uniswap", "aave", "maker", ...],
    "AI": ["bittensor", "near", "render-token", ...],
    "DeSci": ["bio-protocol", "vitadao", ...],
}
```

### Environment Variables

Create a `.env` file:

```
COINGECKO_API_KEY=your_pro_api_key_here
```

---

## Glossary

| Term | Definition |
|------|------------|
| **RSI (Relative Strength Index)** | Momentum oscillator measuring speed and magnitude of price changes. Range 0-100. Traditionally, <30 = oversold, >70 = overbought. |
| **Daily RSI** | RSI calculated on daily closing prices (14-period). |
| **Weekly RSI** | RSI calculated on weekly closing prices. More significant for trend analysis. |
| **Z-Score** | Number of standard deviations from the mean. -2 means 2 standard deviations below average (statistically rare). |
| **Beta** | Measure of how much an asset moves relative to BTC. Beta 1.5 means it typically moves 1.5× BTC's movement. |
| **Residual** | Difference between actual value and expected value. Positive residual = outperforming expectations. |
| **Divergence** | When price and momentum (RSI) move in opposite directions, suggesting a potential reversal. |
| **Confluence** | Multiple independent signals agreeing. Higher confluence = higher probability. |
| **Funding Rate** | In perpetual futures, the rate longs pay shorts (positive) or shorts pay longs (negative). |
| **Open Interest (OI)** | Total value of outstanding futures contracts. Rising OI = new positions entering. |
| **ATR (Average True Range)** | Volatility indicator measuring average daily price range. |
| **Vol/MCap Ratio** | Trading volume divided by market cap. Higher = more trading activity relative to size. |
| **Mean Reversion** | The tendency for prices to return to their historical average. |
| **Regime** | Market state (bull/bear) based on BTC's trend. |
| **Decorrelation** | When an asset stops moving in sync with BTC. |

---

## Data Sources

- **Market Data:** CoinGecko Pro API (120-day price history)
- **Funding Rates:** Binance Futures API (public endpoints)
- **Calculations:** All indicators computed locally in Python

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI (app.py)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Data Layer (src/)                                          │
│  ├── coingecko.py   → Async API client                      │
│  ├── rsi.py         → Wilder's smoothed RSI                 │
│  ├── indicators.py  → 15+ technical calculations            │
│  ├── sectors.py     → Sector classification & momentum      │
│  ├── funding.py     → Binance Futures integration           │
│  └── charts.py      → Plotly visualization builders         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## License

Personal use tool. Not financial advice. Always do your own research.
