# Future Display Ideas

Additional visualizations for identifying investment opportunities using the same asset data.

---

## 1. Multi-Timeframe RSI Alignment Table

**Concept:** Highlight when daily AND weekly RSI agree - these are stronger signals.

| Asset | Daily RSI | Weekly RSI | Signal |
|-------|-----------|------------|--------|
| OLAS | 13.3 | 10.6 | **Double Oversold** |
| BTC | 45.2 | 52.1 | Neutral |

Coins with both timeframes oversold (<30) or overbought (>70) get highlighted. The current scatter shows this with stars, but a dedicated ranked table would make it clearer.

---

## 2. Momentum vs RSI Quadrant

**Axes:**
- **X:** 7-day price change % (momentum)
- **Y:** Daily RSI (value)

**Quadrants:**
| Position | Meaning |
|----------|---------|
| Top-Left | Falling price + still overbought = "Falling Knife" |
| Top-Right | Rising price + overbought = "FOMO Zone" |
| Bottom-Left | Falling price + oversold = "Capitulation" |
| Bottom-Right | Rising price + oversold = "Early Recovery" |

The **bottom-right** (rising + oversold) is the sweet spot - price is recovering while still technically cheap.

---

## 3. RSI Rate of Change

**Concept:** RSI at 35 and *rising* is very different from RSI at 35 and *falling*.

Show RSI direction over last 3-7 days:
- **RSI + Rising** = momentum turning bullish
- **RSI + Falling** = still deteriorating

A simple arrow or sparkline next to each asset would add this dimension.

---

## 4. Opportunity Score Ranking

**Concept:** Combine multiple factors into a single score:

```
Score = (100 - Daily RSI) × 0.4
      + (100 - Weekly RSI) × 0.3
      + Liquidity_Percentile × 0.2
      + RSI_Rising_Bonus × 0.1
```

Display as a ranked leaderboard - top 10 opportunities at a glance.

---

## 5. Volume Anomaly Detection

**Concept:** Unusual volume often precedes price moves.

- Calculate average volume over 30 days
- Flag coins with volume > 2x average today
- Cross-reference with RSI for context

High volume + oversold = potential accumulation by smart money.
