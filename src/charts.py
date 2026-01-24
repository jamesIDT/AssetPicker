"""Plotly chart builders for RSI scatter visualization."""

import math
from typing import Any

import plotly.graph_objects as go

# Quadrant labels and descriptions for the 2x2 grid
# Based on RSI (x-axis) and Liquidity (y-axis) combinations
QUADRANT_LABELS = {
    "top_left": {
        "title": "Capitulation",
        "desc": "Oversold + High Activity",
    },
    "top_right": {
        "title": "Peak Momentum",
        "desc": "Overbought + High Activity",
    },
    "bottom_left": {
        "title": "Forgotten",
        "desc": "Oversold + Low Activity",
    },
    "bottom_right": {
        "title": "Quiet Pump",
        "desc": "Overbought + Low Activity",
    },
}


def format_currency(value: float) -> str:
    """Format a number as currency with abbreviations for large values."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value:,.0f}"
    else:
        return f"${value:,.2f}"


def build_rsi_scatter(
    coin_data: list[dict],
    divergence_data: list[dict] | None = None,
    beta_data: list[float] | None = None,
    color_mode: str = "weekly_rsi",
    sector_data: list[dict] | None = None,
    zscore_data: list[dict | None] | None = None,
    show_zscore: bool = False,
) -> go.Figure:
    """
    Build scatter plot showing daily RSI vs liquidity with configurable color encoding.

    Args:
        coin_data: List of coin dicts with keys:
            - symbol: Coin symbol (e.g., "BTC")
            - name: Full coin name
            - daily_rsi: Daily RSI value (0-100)
            - weekly_rsi: Weekly RSI value (0-100)
            - vol_mcap_ratio: Volume / Market Cap ratio
            - price: Current price
            - volume: 24h trading volume
            - market_cap: Market capitalization
            - beta_info: Optional dict with beta, expected_rsi, residual, interpretation
        divergence_data: Optional list of divergence dicts (same order as coin_data):
            - type: "bullish" | "bearish" | "none"
            - score: 0 | 1 | 2 | 4
        beta_data: Optional list of beta residual values (same order as coin_data)
        color_mode: "weekly_rsi" or "beta_residual"
        sector_data: Optional list of sector dicts (same order as coin_data):
            - sector: Sector name (e.g., "L1", "DeFi")
            - sector_rank: "best" | "worst" | None
        zscore_data: Optional list of zscore dicts (same order as coin_data):
            - zscore: Z-score value
            - extreme: "oversold" | "overbought" | "normal"
        show_zscore: If True, show z-score labels for extreme readings (|z| > 1.5)

    Returns:
        Plotly Figure object with the scatter plot
    """
    # Calculate y-axis range from data or use defaults
    if coin_data:
        vol_mcap_values = [c["vol_mcap_ratio"] for c in coin_data if c["vol_mcap_ratio"] > 0]
        if vol_mcap_values:
            min_vol = min(vol_mcap_values)
            max_vol = max(vol_mcap_values)
            # Add padding and round to nice log values
            log_min = math.floor(math.log10(min_vol))
            log_max = math.ceil(math.log10(max_vol))
            y_range = [10 ** log_min, 10 ** log_max]
            # Calculate midpoint in log space for quadrant division
            log_mid = (log_min + log_max) / 2
            y_mid = 10 ** log_mid
        else:
            y_range = [0.001, 10]
            y_mid = 0.1
            log_min, log_max, log_mid = -3, 1, -1
    else:
        y_range = [0.001, 10]
        y_mid = 0.1
        log_min, log_max, log_mid = -3, 1, -1

    fig = go.Figure()

    # Add quadrant background shading (2x2 grid split at RSI=50 and log midpoint)
    # Dark theme: slightly more opaque for visibility on dark backgrounds
    # Top-left: Capitulation (green tint - opportunity)
    fig.add_shape(
        type="rect", x0=0, x1=50, y0=y_mid, y1=y_range[1],
        fillcolor="rgba(76, 175, 80, 0.12)", line_width=0, layer="below"
    )
    # Top-right: Peak Momentum (red tint - caution)
    fig.add_shape(
        type="rect", x0=50, x1=100, y0=y_mid, y1=y_range[1],
        fillcolor="rgba(244, 67, 54, 0.12)", line_width=0, layer="below"
    )
    # Bottom-left: Forgotten (neutral/gray tint)
    fig.add_shape(
        type="rect", x0=0, x1=50, y0=y_range[0], y1=y_mid,
        fillcolor="rgba(158, 158, 158, 0.08)", line_width=0, layer="below"
    )
    # Bottom-right: Quiet Pump (orange tint - warning)
    fig.add_shape(
        type="rect", x0=50, x1=100, y0=y_range[0], y1=y_mid,
        fillcolor="rgba(255, 152, 0, 0.12)", line_width=0, layer="below"
    )

    # Add quadrant divider lines (cream color for dark theme)
    fig.add_shape(
        type="line", x0=50, x1=50, y0=y_range[0], y1=y_range[1],
        line={"color": "rgba(255,255,227,0.15)", "width": 1, "dash": "dot"}
    )
    fig.add_shape(
        type="line", x0=0, x1=100, y0=y_mid, y1=y_mid,
        line={"color": "rgba(255,255,227,0.15)", "width": 1, "dash": "dot"}
    )

    # Add quadrant labels - x as RSI value, y as domain fraction (cream color for dark theme)
    label_font = {"size": 36, "color": "rgba(255,255,227,0.08)", "family": "Arial Black"}
    desc_font = {"size": 18, "color": "rgba(255,255,227,0.06)"}

    # Top-left: Capitulation (RSI 0-50, top half)
    fig.add_annotation(
        x=25, y=0.75, text=QUADRANT_LABELS["top_left"]["title"],
        showarrow=False, font=label_font, xref="x", yref="y domain"
    )
    fig.add_annotation(
        x=25, y=0.65, text=QUADRANT_LABELS["top_left"]["desc"],
        showarrow=False, font=desc_font, xref="x", yref="y domain"
    )

    # Top-right: Peak Momentum (RSI 50-100, top half)
    fig.add_annotation(
        x=75, y=0.75, text=QUADRANT_LABELS["top_right"]["title"],
        showarrow=False, font=label_font, xref="x", yref="y domain"
    )
    fig.add_annotation(
        x=75, y=0.65, text=QUADRANT_LABELS["top_right"]["desc"],
        showarrow=False, font=desc_font, xref="x", yref="y domain"
    )

    # Bottom-left: Forgotten (RSI 0-50, bottom half)
    fig.add_annotation(
        x=25, y=0.35, text=QUADRANT_LABELS["bottom_left"]["title"],
        showarrow=False, font=label_font, xref="x", yref="y domain"
    )
    fig.add_annotation(
        x=25, y=0.25, text=QUADRANT_LABELS["bottom_left"]["desc"],
        showarrow=False, font=desc_font, xref="x", yref="y domain"
    )

    # Bottom-right: Quiet Pump (RSI 50-100, bottom half)
    fig.add_annotation(
        x=75, y=0.35, text=QUADRANT_LABELS["bottom_right"]["title"],
        showarrow=False, font=label_font, xref="x", yref="y domain"
    )
    fig.add_annotation(
        x=75, y=0.25, text=QUADRANT_LABELS["bottom_right"]["desc"],
        showarrow=False, font=desc_font, xref="x", yref="y domain"
    )

    if not coin_data:
        fig.update_layout(
            title="RSI vs Liquidity",
            xaxis_title="Daily RSI",
            yaxis_title="Liquidity (Vol/MCap)",
            annotations=fig.layout.annotations + (
                {
                    "text": "No data available",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                },
            ),
        )
        return fig

    symbols = [c["symbol"] for c in coin_data]
    daily_rsi = [c["daily_rsi"] for c in coin_data]
    vol_mcap = [c["vol_mcap_ratio"] for c in coin_data]
    weekly_rsi = [c["weekly_rsi"] for c in coin_data]

    # Determine color values, colorscale, and range based on mode
    if color_mode == "beta_residual" and beta_data is not None:
        color_values = beta_data
        colorscale = "RdYlGn"  # NOT reversed - positive residual = green (outperforming)
        cmin, cmax = -20, 20
        colorbar_title = "Beta Residual"
        colorbar_tickvals = [-20, -10, 0, 10, 20]
    else:
        color_values = weekly_rsi
        colorscale = "RdYlGn_r"  # Reversed - low RSI = green (oversold = opportunity)
        cmin, cmax = 0, 100
        colorbar_title = "Weekly RSI"
        colorbar_tickvals = [0, 25, 50, 75, 100]

    # Build divergence info (default to none if not provided)
    if divergence_data is None:
        divergence_data = [{"type": "none", "score": 0} for _ in coin_data]
    elif len(divergence_data) != len(coin_data):
        # Fallback if lengths don't match
        divergence_data = [{"type": "none", "score": 0} for _ in coin_data]

    # Build sector info (default if not provided)
    if sector_data is None:
        sector_data = [{"sector": "Other", "sector_rank": None} for _ in coin_data]
    elif len(sector_data) != len(coin_data):
        sector_data = [{"sector": "Other", "sector_rank": None} for _ in coin_data]

    # Build zscore info (default if not provided)
    if zscore_data is None:
        zscore_data = [None for _ in coin_data]
    elif len(zscore_data) != len(coin_data):
        zscore_data = [None for _ in coin_data]

    # Build text labels - include z-score for extreme readings if show_zscore is True
    text_labels = []
    for i, c in enumerate(coin_data):
        symbol = c["symbol"]
        z_info = zscore_data[i] if zscore_data else None
        if show_zscore and z_info is not None:
            zscore_val = z_info.get("zscore", 0)
            if abs(zscore_val) > 1.5:
                # Format as "BTC (-2.3σ)" or "ETH (+1.8σ)"
                sign = "+" if zscore_val > 0 else ""
                symbol = f"{symbol} ({sign}{zscore_val:.1f}σ)"
        text_labels.append(symbol)

    # Prepare customdata for enhanced tooltips:
    # [name, price, volume, mcap, weekly_rsi, divergence_type, divergence_score, beta, residual, sector, sector_rank, zscore, zscore_extreme]
    customdata = []
    for i, (c, d, s) in enumerate(zip(coin_data, divergence_data, sector_data)):
        beta_info = c.get("beta_info")
        beta_val = beta_info.get("beta", 0) if beta_info else 0
        residual_val = beta_info.get("residual", 0) if beta_info else 0
        # Format sector rank as badge text
        sector_rank = s.get("sector_rank")
        if sector_rank == "best":
            rank_badge = " - Best in sector"
        elif sector_rank == "worst":
            rank_badge = " - Worst in sector"
        else:
            rank_badge = ""

        # Format z-score info
        z_info = zscore_data[i] if zscore_data else None
        if z_info is not None:
            zscore_val = z_info.get("zscore", 0)
            extreme = z_info.get("extreme", "normal")
            if extreme == "oversold":
                zscore_text = f"{zscore_val:+.2f}σ (Oversold)"
            elif extreme == "overbought":
                zscore_text = f"{zscore_val:+.2f}σ (Overbought)"
            else:
                zscore_text = f"{zscore_val:+.2f}σ"
        else:
            zscore_text = "N/A"

        customdata.append([
            c["name"],
            format_currency(c["price"]),
            format_currency(c["volume"]),
            format_currency(c["market_cap"]),
            c["weekly_rsi"],
            d["type"],
            d["score"],
            beta_val,
            residual_val,
            s.get("sector", "Other"),
            rank_badge,
            zscore_text,
        ])

    # Group coins by divergence type for efficient trace rendering
    # Indices for each group
    neutral_indices = []
    bullish_indices = []
    bearish_indices = []
    score_2_indices = []  # Score >= 2 (outer ring)
    score_4_indices = []  # Score == 4 (bold outer ring)

    for i, d in enumerate(divergence_data):
        div_type = d.get("type", "none")
        score = d.get("score", 0)

        if div_type == "bullish":
            bullish_indices.append(i)
        elif div_type == "bearish":
            bearish_indices.append(i)
        else:
            neutral_indices.append(i)

        if score >= 2:
            score_2_indices.append(i)
        if score == 4:
            score_4_indices.append(i)

    # Helper to extract subset by indices
    def subset(indices: list[int], values: list) -> list:
        return [values[i] for i in indices]

    # Common hovertemplate for all traces
    # customdata indices: 9=sector, 10=sector_rank_badge, 11=zscore_text
    if color_mode == "beta_residual":
        hovertemplate = (
            "<b>%{customdata[0]}</b> (%{text})<br>"
            "Price: %{customdata[1]}<br>"
            "Volume: %{customdata[2]}<br>"
            "Market Cap: %{customdata[3]}<br>"
            "Daily RSI: %{x:.1f}<br>"
            "Weekly RSI: %{customdata[4]:.1f}<br>"
            "Z-Score: %{customdata[11]}<br>"
            "Beta: %{customdata[7]:.2f} | Residual: %{customdata[8]:+.1f}<br>"
            "Sector: %{customdata[9]}%{customdata[10]}<br>"
            "Divergence: %{customdata[5]} (score %{customdata[6]})"
            "<extra></extra>"
        )
    else:
        hovertemplate = (
            "<b>%{customdata[0]}</b> (%{text})<br>"
            "Price: %{customdata[1]}<br>"
            "Volume: %{customdata[2]}<br>"
            "Market Cap: %{customdata[3]}<br>"
            "Daily RSI: %{x:.1f}<br>"
            "Weekly RSI: %{customdata[4]:.1f}<br>"
            "Z-Score: %{customdata[11]}<br>"
            "Sector: %{customdata[9]}%{customdata[10]}<br>"
            "Divergence: %{customdata[5]} (score %{customdata[6]})"
            "<extra></extra>"
        )

    # Layer 1: Outer rings for score >= 2 (thin ring)
    if score_2_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(score_2_indices, daily_rsi),
                y=subset(score_2_indices, vol_mcap),
                mode="markers",
                marker={
                    "size": 18,
                    "symbol": "circle-open",
                    "color": subset(score_2_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
                },
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Layer 2: Bold rings for score = 4 (overrides thin ring visually)
    if score_4_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(score_4_indices, daily_rsi),
                y=subset(score_4_indices, vol_mcap),
                mode="markers",
                marker={
                    "size": 20,
                    "symbol": "circle-open",
                    "color": subset(score_4_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "line": {"width": 3, "color": "rgba(255,255,255,0.6)"},
                },
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Layer 3: Neutral circles (no divergence)
    if neutral_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(neutral_indices, daily_rsi),
                y=subset(neutral_indices, vol_mcap),
                mode="markers+text",
                text=subset(neutral_indices, text_labels),
                textposition="top center",
                textfont={"size": 9, "color": "#FFFFE3"},
                customdata=subset(neutral_indices, customdata),
                marker={
                    "size": 10,
                    "symbol": "circle",
                    "color": subset(neutral_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "colorbar": {
                        "title": colorbar_title,
                        "tickvals": colorbar_tickvals,
                        "len": 0.8,
                        "tickfont": {"color": "#FFFFE3"},
                        "title_font": {"color": "#FFFFE3"},
                    },
                    "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
                },
                hovertemplate=hovertemplate,
                showlegend=False,
            )
        )

    # Layer 4: Bullish crosses (+)
    if bullish_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(bullish_indices, daily_rsi),
                y=subset(bullish_indices, vol_mcap),
                mode="markers+text",
                text=subset(bullish_indices, text_labels),
                textposition="top center",
                textfont={"size": 9, "color": "#FFFFE3"},
                customdata=subset(bullish_indices, customdata),
                marker={
                    "size": 12,
                    "symbol": "cross",
                    "color": subset(bullish_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "colorbar": None if neutral_indices else {
                        "title": colorbar_title,
                        "tickvals": colorbar_tickvals,
                        "len": 0.8,
                        "tickfont": {"color": "#FFFFE3"},
                        "title_font": {"color": "#FFFFE3"},
                    },
                    "line": {"width": 2, "color": "rgba(255,255,255,0.5)"},
                },
                hovertemplate=hovertemplate,
                showlegend=False,
            )
        )

    # Layer 5: Bearish diamonds
    if bearish_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(bearish_indices, daily_rsi),
                y=subset(bearish_indices, vol_mcap),
                mode="markers+text",
                text=subset(bearish_indices, text_labels),
                textposition="top center",
                textfont={"size": 9, "color": "#FFFFE3"},
                customdata=subset(bearish_indices, customdata),
                marker={
                    "size": 12,
                    "symbol": "diamond",
                    "color": subset(bearish_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "colorbar": None if (neutral_indices or bullish_indices) else {
                        "title": colorbar_title,
                        "tickvals": colorbar_tickvals,
                        "len": 0.8,
                        "tickfont": {"color": "#FFFFE3"},
                        "title_font": {"color": "#FFFFE3"},
                    },
                    "line": {"width": 2, "color": "rgba(255,255,255,0.5)"},
                },
                hovertemplate=hovertemplate,
                showlegend=False,
            )
        )

    # Fallback: if no coins in any category, add empty trace for colorbar
    if not neutral_indices and not bullish_indices and not bearish_indices:
        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="markers",
                marker={
                    "size": 10,
                    "color": [],
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "colorbar": {
                        "title": colorbar_title,
                        "tickvals": colorbar_tickvals,
                        "len": 0.8,
                        "tickfont": {"color": "#FFFFE3"},
                        "title_font": {"color": "#FFFFE3"},
                    },
                },
                showlegend=False,
            )
        )

    # Add divergence legend in top-left corner
    # Using paper coordinates to position relative to plot area
    legend_text = (
        "<b>📊 Divergence Markers</b><br>"
        "<span style='font-size:14px'>+</span> Bullish divergence<br>"
        "<span style='font-size:12px'>◆</span> Bearish divergence<br>"
        "<span style='font-size:10px'>●</span> No divergence<br>"
        "<br>"
        "<b>🎯 Divergence Score</b><br>"
        "0 = No divergence<br>"
        "1 = Single TF, weak (RSI Δ &lt; 5)<br>"
        "2 = Single TF, strong (RSI Δ ≥ 5)<br>"
        "4 = Multi-TF (daily + weekly)<br>"
        "<br>"
        "<b>🔘 Ring Visual</b><br>"
        "○ Thin ring = Score 2<br>"
        "<b>○</b> Bold ring = Score 4"
    )
    fig.add_annotation(
        x=0.01,
        y=0.99,
        xref="paper",
        yref="paper",
        text=legend_text,
        showarrow=False,
        font={"size": 10, "color": "#FFFFE3"},
        align="left",
        bgcolor="rgba(90, 90, 90, 0.95)",
        bordercolor="rgba(255, 255, 227, 0.2)",
        borderwidth=1,
        borderpad=8,
        xanchor="left",
        yanchor="top",
    )

    # Add color mode explanation in bottom-left
    if color_mode == "beta_residual":
        color_legend = (
            "<b>🎨 Color: Beta Residual</b><br>"
            "🟢 Green = Outperforming BTC<br>"
            "🟡 Yellow = Expected vs BTC<br>"
            "🔴 Red = Underperforming BTC"
        )
    else:
        color_legend = (
            "<b>🎨 Color: Weekly RSI</b><br>"
            "🟢 Green = Oversold (&lt;30)<br>"
            "🟡 Yellow = Neutral (30-70)<br>"
            "🔴 Red = Overbought (&gt;70)"
        )
    fig.add_annotation(
        x=0.01,
        y=0.01,
        xref="paper",
        yref="paper",
        text=color_legend,
        showarrow=False,
        font={"size": 10, "color": "#FFFFE3"},
        align="left",
        bgcolor="rgba(90, 90, 90, 0.95)",
        bordercolor="rgba(255, 255, 227, 0.2)",
        borderwidth=1,
        borderpad=8,
        xanchor="left",
        yanchor="bottom",
    )

    fig.update_layout(
        title="",
        xaxis_title="Daily RSI",
        yaxis_title="Liquidity (Vol/MCap)",
        xaxis={
            "range": [0, 100],
            "dtick": 25,
            "gridcolor": "rgba(255, 255, 227, 0.08)",
            "zeroline": False,
            "title_font": {"color": "#FFFFE3"},
            "tickfont": {"color": "#FFFFE3"},
        },
        yaxis={
            "type": "log",
            "range": [log_min, log_max],
            "gridcolor": "rgba(255, 255, 227, 0.08)",
            "zeroline": False,
            "title_font": {"color": "#FFFFE3"},
            "tickfont": {"color": "#FFFFE3"},
        },
        showlegend=False,
        paper_bgcolor="#4A4A4A",
        plot_bgcolor="rgba(90, 90, 90, 0.3)",
        margin={"l": 60, "r": 100, "t": 30, "b": 60},
        autosize=True,
        height=800,
    )

    return fig


def build_acceleration_quadrant(coins: list[dict[str, Any]]) -> go.Figure:
    """
    Build scatter plot showing RSI acceleration vs volatility regime for opportunity detection.

    Quadrants:
    - Top-Right (>0, >1.3): Accelerating + High Vol = Explosive move in progress
    - Top-Left (<0, >1.3): Decelerating + High Vol = Move exhausting
    - Bottom-Right (>0, <0.7): Accelerating + Compressed = Coiled spring (BEST SIGNAL)
    - Bottom-Left (<0, <0.7): Decelerating + Compressed = Dormant

    Args:
        coins: List of coin dicts with keys:
            - symbol: Coin symbol (e.g., "BTC")
            - daily_rsi: Daily RSI value (0-100)
            - acceleration: Dict with "acceleration" key from calculate_rsi_acceleration
            - volatility: Dict with "ratio" key from detect_volatility_regime

    Returns:
        Plotly Figure object with the quadrant scatter plot
    """
    fig = go.Figure()

    # Filter coins with both acceleration and volatility data
    valid_coins = []
    for coin in coins:
        accel = coin.get("acceleration")
        vol = coin.get("volatility")
        if accel is not None and vol is not None:
            accel_val = accel.get("acceleration")
            vol_ratio = vol.get("ratio")
            if accel_val is not None and vol_ratio is not None:
                valid_coins.append({
                    "symbol": coin.get("symbol", "?"),
                    "daily_rsi": coin.get("daily_rsi", 50),
                    "acceleration": accel_val,
                    "volatility_ratio": vol_ratio,
                    "volatility_regime": vol.get("regime", "normal"),
                    "interpretation": accel.get("interpretation", "stable"),
                })

    if not valid_coins:
        fig.update_layout(
            title="Acceleration Quadrant",
            xaxis_title="RSI Acceleration",
            yaxis_title="Volatility Ratio",
            annotations=[
                {
                    "text": "No acceleration/volatility data available",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                },
            ],
        )
        return fig

    # Extract data for plotting
    symbols = [c["symbol"] for c in valid_coins]
    accelerations = [c["acceleration"] for c in valid_coins]
    vol_ratios = [c["volatility_ratio"] for c in valid_coins]
    daily_rsis = [c["daily_rsi"] for c in valid_coins]

    # Build customdata for tooltips
    customdata = []
    for c in valid_coins:
        customdata.append([
            c["symbol"],
            c["daily_rsi"],
            c["acceleration"],
            c["volatility_regime"],
            c["interpretation"],
        ])

    # Add quadrant background shading
    # Calculate x-axis range from data
    x_min = min(accelerations) - 1
    x_max = max(accelerations) + 1
    # Ensure x-axis includes 0 for the vertical divider
    if x_min > -1:
        x_min = -1
    if x_max < 1:
        x_max = 1

    # y-axis range with padding
    y_min = min(vol_ratios) * 0.8
    y_max = max(vol_ratios) * 1.2
    # Ensure y-axis covers the threshold lines
    if y_min > 0.5:
        y_min = 0.5
    if y_max < 1.5:
        y_max = 1.5

    # Dark theme: slightly more opaque for visibility on dark backgrounds
    # Top-Left: Decelerating + High Vol = Exhausting (orange tint)
    fig.add_shape(
        type="rect", x0=x_min, x1=0, y0=1.3, y1=y_max,
        fillcolor="rgba(255, 152, 0, 0.12)", line_width=0, layer="below"
    )
    # Top-Right: Accelerating + High Vol = Explosive (red tint)
    fig.add_shape(
        type="rect", x0=0, x1=x_max, y0=1.3, y1=y_max,
        fillcolor="rgba(244, 67, 54, 0.12)", line_width=0, layer="below"
    )
    # Bottom-Left: Decelerating + Compressed = Dormant (gray tint)
    fig.add_shape(
        type="rect", x0=x_min, x1=0, y0=y_min, y1=0.7,
        fillcolor="rgba(158, 158, 158, 0.10)", line_width=0, layer="below"
    )
    # Bottom-Right: Accelerating + Compressed = Coiled Spring (green tint - BEST)
    fig.add_shape(
        type="rect", x0=0, x1=x_max, y0=y_min, y1=0.7,
        fillcolor="rgba(76, 175, 80, 0.15)", line_width=0, layer="below"
    )

    # Add quadrant boundary lines (cream color for dark theme)
    # Vertical line at x=0
    fig.add_shape(
        type="line", x0=0, x1=0, y0=y_min, y1=y_max,
        line={"color": "rgba(255,255,227,0.15)", "width": 1, "dash": "dot"}
    )
    # Horizontal line at y=0.7 (compressed threshold)
    fig.add_shape(
        type="line", x0=x_min, x1=x_max, y0=0.7, y1=0.7,
        line={"color": "rgba(255,255,227,0.15)", "width": 1, "dash": "dot"}
    )
    # Horizontal line at y=1.3 (expanded threshold)
    fig.add_shape(
        type="line", x0=x_min, x1=x_max, y0=1.3, y1=1.3,
        line={"color": "rgba(255,255,227,0.15)", "width": 1, "dash": "dot"}
    )

    # Add quadrant labels as annotations (cream color for dark theme)
    label_font = {"size": 24, "color": "rgba(255,255,227,0.10)", "family": "Arial Black"}

    # Top-Right: Explosive Move
    fig.add_annotation(
        x=0.85, y=0.92, text="Explosive Move 💥",
        showarrow=False, font=label_font, xref="paper", yref="paper"
    )
    # Top-Left: Exhausting
    fig.add_annotation(
        x=0.15, y=0.92, text="Exhausting ⚠️",
        showarrow=False, font=label_font, xref="paper", yref="paper"
    )
    # Bottom-Right: Coiled Spring (BEST)
    fig.add_annotation(
        x=0.85, y=0.08, text="Coiled Spring 🎯",
        showarrow=False, font=label_font, xref="paper", yref="paper"
    )
    # Bottom-Left: Dormant
    fig.add_annotation(
        x=0.15, y=0.08, text="Dormant 💤",
        showarrow=False, font=label_font, xref="paper", yref="paper"
    )

    # Add scatter trace
    fig.add_trace(
        go.Scatter(
            x=accelerations,
            y=vol_ratios,
            mode="markers+text",
            text=symbols,
            textposition="top center",
            textfont={"size": 9, "color": "#FFFFE3"},
            customdata=customdata,
            marker={
                "size": 12,
                "color": daily_rsis,
                "colorscale": "RdYlGn_r",  # Low RSI = green (oversold = opportunity)
                "cmin": 0,
                "cmax": 100,
                "colorbar": {
                    "title": "Daily RSI",
                    "tickvals": [0, 25, 50, 75, 100],
                    "len": 0.8,
                    "tickfont": {"color": "#FFFFE3"},
                    "title_font": {"color": "#FFFFE3"},
                },
                "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Daily RSI: %{customdata[1]:.1f}<br>"
                "Acceleration: %{customdata[2]:+.2f}<br>"
                "Volatility Regime: %{customdata[3]}<br>"
                "Interpretation: %{customdata[4]}"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        title="",
        xaxis_title="RSI Acceleration",
        yaxis_title="Volatility Ratio",
        xaxis={
            "range": [x_min, x_max],
            "zeroline": True,
            "zerolinecolor": "rgba(255, 255, 227, 0.15)",
            "gridcolor": "rgba(255, 255, 227, 0.08)",
            "title_font": {"color": "#FFFFE3"},
            "tickfont": {"color": "#FFFFE3"},
        },
        yaxis={
            "range": [y_min, y_max],
            "zeroline": False,
            "gridcolor": "rgba(255, 255, 227, 0.08)",
            "title_font": {"color": "#FFFFE3"},
            "tickfont": {"color": "#FFFFE3"},
        },
        showlegend=False,
        paper_bgcolor="#4A4A4A",
        plot_bgcolor="rgba(90, 90, 90, 0.3)",
        margin={"l": 60, "r": 100, "t": 30, "b": 60},
        autosize=True,
        height=500,
    )

    return fig
