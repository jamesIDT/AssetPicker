"""Plotly chart builders for RSI scatter visualization."""

import math
from typing import Any

import plotly.graph_objects as go


def hex_to_rgba(hex_color: str, opacity: float) -> str:
    """
    Convert hex color to rgba string.

    Args:
        hex_color: Hex color string (e.g., "#22c55e" or "22c55e")
        opacity: Opacity value between 0.0 and 1.0

    Returns:
        RGBA color string (e.g., "rgba(34,197,94,0.3)")
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


def get_segment_angles(segment_index: int) -> tuple[float, float]:
    """
    Get start and end angles for a ring segment (0-5).

    Segments are arranged clockwise from top:
    - Segment 0 (1w): Top center, -30 to 30 degrees from top
    - Segment 1 (3d): 30 to 90 degrees
    - Segment 2 (1d): 90 to 150 degrees
    - Segment 3 (12h): 150 to 210 degrees
    - Segment 4 (4h): 210 to 270 degrees
    - Segment 5 (1h): 270 to 330 degrees

    Returns angles in Plotly/SVG convention (0 = right, counterclockwise positive).
    We convert from "clockwise from top" to standard math convention.

    Args:
        segment_index: 0-5 for the six timeframe segments

    Returns:
        (start_angle, end_angle) in radians for standard math coords

    Example:
        >>> get_segment_angles(0)  # 1w segment at top
        (1.0471975511965976, 2.0943951023931953)  # 60 to 120 degrees
    """
    # Clockwise from top angles (degrees)
    segment_starts_from_top = [-30, 30, 90, 150, 210, 270]
    segment_ends_from_top = [30, 90, 150, 210, 270, 330]

    # Convert from "clockwise from top" to standard math convention
    # Standard: 0 = right (3 o'clock), counterclockwise positive
    # From top: 0 = top (12 o'clock), clockwise positive
    # Conversion: standard_angle = 90 - clockwise_from_top
    start_from_top = segment_starts_from_top[segment_index]
    end_from_top = segment_ends_from_top[segment_index]

    # Convert to standard convention (note: we swap start/end because we're reversing direction)
    start_angle_deg = 90 - end_from_top
    end_angle_deg = 90 - start_from_top

    # Convert to radians
    start_angle = math.radians(start_angle_deg)
    end_angle = math.radians(end_angle_deg)

    return (start_angle, end_angle)


def create_arc_segment_path(
    cx: float,
    cy: float,
    inner_radius_x: float,
    outer_radius_x: float,
    inner_radius_y: float,
    outer_radius_y: float,
    start_angle: float,
    end_angle: float,
) -> str:
    """
    Create SVG path string for an arc segment (donut slice).

    Supports elliptical arcs with different x and y radii, which is needed
    for log-scale y-axis where we want visually consistent ring sizes.

    The path traces:
    1. Start at inner arc start point
    2. Line to outer arc start point
    3. Arc along outer edge
    4. Line to inner arc end point
    5. Arc back along inner edge (reverse direction)
    6. Close path

    Args:
        cx: Center x coordinate (data coords)
        cy: Center y coordinate (data coords)
        inner_radius_x: Inner radius in x direction
        outer_radius_x: Outer radius in x direction
        inner_radius_y: Inner radius in y direction
        outer_radius_y: Outer radius in y direction
        start_angle: Start angle in radians (standard math: 0=right, CCW positive)
        end_angle: End angle in radians

    Returns:
        SVG path string suitable for fig.add_shape(type="path", path=...)
    """
    # Calculate the four corner points using elliptical coordinates
    # Inner arc: start and end
    inner_start_x = cx + inner_radius_x * math.cos(start_angle)
    inner_start_y = cy + inner_radius_y * math.sin(start_angle)
    inner_end_x = cx + inner_radius_x * math.cos(end_angle)
    inner_end_y = cy + inner_radius_y * math.sin(end_angle)

    # Outer arc: start and end
    outer_start_x = cx + outer_radius_x * math.cos(start_angle)
    outer_start_y = cy + outer_radius_y * math.sin(start_angle)
    outer_end_x = cx + outer_radius_x * math.cos(end_angle)
    outer_end_y = cy + outer_radius_y * math.sin(end_angle)

    # Determine arc flags
    # For 60-degree segments, we never need the large arc flag
    angle_span = end_angle - start_angle
    large_arc = 1 if abs(angle_span) > math.pi else 0

    # Sweep flag: 1 for counterclockwise (our convention)
    sweep_outer = 1  # CCW for outer arc (start to end)
    sweep_inner = 0  # CW for inner arc (end back to start)

    # Build SVG path
    # M = move to, L = line to, A = arc
    # Arc syntax: A rx ry x-axis-rotation large-arc-flag sweep-flag x y
    path = (
        f"M {inner_start_x:.6f} {inner_start_y:.6f} "
        f"L {outer_start_x:.6f} {outer_start_y:.6f} "
        f"A {outer_radius_x:.6f} {outer_radius_y:.6f} 0 {large_arc} {sweep_outer} "
        f"{outer_end_x:.6f} {outer_end_y:.6f} "
        f"L {inner_end_x:.6f} {inner_end_y:.6f} "
        f"A {inner_radius_x:.6f} {inner_radius_y:.6f} 0 {large_arc} {sweep_inner} "
        f"{inner_start_x:.6f} {inner_start_y:.6f} "
        f"Z"
    )

    return path

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
    color_mode: str = "beta_residual",
    sector_data: list[dict] | None = None,
    zscore_data: list[dict | None] | None = None,
    show_zscore: bool = False,
    height: int = 600,
    beta_benchmark: str = "BTC",
    multi_tf_divergence: dict[str, dict] | None = None,
    multi_tf_rsi: dict[str, dict] | None = None,
    show_timeframe: str | None = None,
    highlight_tf: str | None = None,
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
            - id: CoinGecko coin ID (for multi_tf_divergence lookup)
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
        height: Chart height in pixels (default 600)
        beta_benchmark: Label for beta benchmark ("BTC", "ETH", "Total3") for colorbar title
        multi_tf_divergence: Optional dict mapping coin_id to timeframe divergence data:
            {coin_id: {timeframe: {"type": "bullish"|"bearish"|"none", ...}}}
            Timeframes: 1h, 4h, 12h, 1d, 3d, 1w
        highlight_tf: Optional timeframe to highlight in ring segments.
            When set, the specified timeframe segment renders at full opacity (1.0)
            while other segments fade to 0.3 opacity. None shows all at full opacity.

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
            # Ensure we have a valid range (prevent division by zero)
            if log_min == log_max:
                log_min = log_min - 1
                log_max = log_max + 1
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
        line={"color": "rgba(246,248,247,0.15)", "width": 1, "dash": "dot"}
    )
    fig.add_shape(
        type="line", x0=0, x1=100, y0=y_mid, y1=y_mid,
        line={"color": "rgba(246,248,247,0.15)", "width": 1, "dash": "dot"}
    )

    # Add quadrant labels - x as RSI value, y as domain fraction (cream color for dark theme)
    label_font = {"size": 36, "color": "rgba(246,248,247,0.08)", "family": "Arial Black"}
    desc_font = {"size": 18, "color": "rgba(246,248,247,0.06)"}

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
    vol_mcap = [c["vol_mcap_ratio"] for c in coin_data]
    weekly_rsi = [c["weekly_rsi"] for c in coin_data]

    # Determine X-axis RSI based on show_timeframe
    # show_timeframe controls X-axis, highlight_tf controls ring highlighting
    TIMEFRAME_LABELS = {
        "1h": "1-Hour RSI",
        "4h": "4-Hour RSI",
        "12h": "12-Hour RSI",
        "1d": "Daily RSI",
        "3d": "3-Day RSI",
        "1w": "Weekly RSI",
    }

    if show_timeframe and multi_tf_rsi:
        # Use selected timeframe's RSI for X-axis
        x_axis_title = TIMEFRAME_LABELS.get(show_timeframe, f"{show_timeframe} RSI")
        daily_rsi = []
        for c in coin_data:
            coin_id = c.get("id")
            coin_tf_rsi = multi_tf_rsi.get(coin_id, {}) if coin_id else {}
            tf_rsi = coin_tf_rsi.get(show_timeframe)
            # Fall back to daily_rsi if timeframe RSI not available
            daily_rsi.append(tf_rsi if tf_rsi is not None else c["daily_rsi"])
    else:
        # Default to daily RSI
        x_axis_title = "Daily RSI"
        daily_rsi = [c["daily_rsi"] for c in coin_data]

    # Determine color values, colorscale, and range based on mode
    if color_mode == "beta_residual" and beta_data is not None:
        color_values = beta_data
        colorscale = "RdYlGn"  # NOT reversed - positive residual = green (outperforming)
        cmin, cmax = -20, 20
        colorbar_title = f"Beta vs {beta_benchmark}"
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

    # Layer 0: Multi-timeframe divergence as concentric rings (added BEFORE markers)
    # 6 concentric rings around each marker - inner to outer: 1w, 3d, 1d, 12h, 4h, 1h
    # Uses scatter markers with circle-open - fixed pixel size that moves with zoom
    TIMEFRAME_ORDER = ["1w", "3d", "1d", "12h", "4h", "1h"]
    DIVERGENCE_COLORS = {
        "bullish": "#22c55e",  # Green
        "bearish": "#ef4444",  # Red
        "none": "#6b7280",     # Gray
    }

    # Ring sizes in pixels (inner to outer): 1w=14, 3d=18, 1d=22, 12h=26, 4h=30, 1h=34
    RING_SIZES = [14, 18, 22, 26, 30, 34]
    RING_LINE_WIDTH = 2.5  # Thickness of each ring

    if multi_tf_divergence:
        # Add rings from outermost to innermost so inner rings draw on top
        for tf_idx in range(5, -1, -1):  # 5, 4, 3, 2, 1, 0 (1h down to 1w)
            tf = TIMEFRAME_ORDER[tf_idx]
            ring_size = RING_SIZES[tf_idx]

            ring_x = []
            ring_y = []
            ring_colors = []

            for i, c in enumerate(coin_data):
                coin_id = c.get("id")
                if not coin_id:
                    continue

                cx = daily_rsi[i]
                cy = vol_mcap[i]

                if cx is None or cy is None or cy <= 0:
                    continue

                # Get divergence data for this coin/timeframe
                coin_mtf = multi_tf_divergence.get(coin_id, {})
                tf_data = coin_mtf.get(tf, {})
                div_type = tf_data.get("type", "none") if tf_data else "none"
                base_color = DIVERGENCE_COLORS.get(div_type, DIVERGENCE_COLORS["none"])

                # Apply opacity for highlight mode
                if highlight_tf is None or highlight_tf == tf:
                    color = base_color
                else:
                    color = hex_to_rgba(base_color, 0.25)

                ring_x.append(cx)
                ring_y.append(cy)
                ring_colors.append(color)

            # Add scatter trace for this timeframe's ring
            if ring_x:
                fig.add_trace(
                    go.Scatter(
                        x=ring_x,
                        y=ring_y,
                        mode="markers",
                        marker={
                            "size": ring_size,
                            "symbol": "circle-open",
                            "color": ring_colors,
                            "line": {"width": RING_LINE_WIDTH, "color": ring_colors},
                        },
                        showlegend=False,
                        hoverinfo="skip",
                        name=f"Ring-{tf}",
                    )
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
                textfont={"size": 9, "color": "#F6F8F7"},
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
                        "tickfont": {"color": "#F6F8F7"},
                        "title_font": {"color": "#F6F8F7"},
                    },
                    "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
                },
                hovertemplate=hovertemplate,
                showlegend=False,
            )
        )

    # Layer 4: Bullish divergence coins (now circles - divergence shown via rings)
    if bullish_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(bullish_indices, daily_rsi),
                y=subset(bullish_indices, vol_mcap),
                mode="markers+text",
                text=subset(bullish_indices, text_labels),
                textposition="top center",
                textfont={"size": 9, "color": "#F6F8F7"},
                customdata=subset(bullish_indices, customdata),
                marker={
                    "size": 10,
                    "symbol": "circle",
                    "color": subset(bullish_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "colorbar": None if neutral_indices else {
                        "title": colorbar_title,
                        "tickvals": colorbar_tickvals,
                        "len": 0.8,
                        "tickfont": {"color": "#F6F8F7"},
                        "title_font": {"color": "#F6F8F7"},
                    },
                    "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
                },
                hovertemplate=hovertemplate,
                showlegend=False,
            )
        )

    # Layer 5: Bearish divergence coins (now circles - divergence shown via rings)
    if bearish_indices:
        fig.add_trace(
            go.Scatter(
                x=subset(bearish_indices, daily_rsi),
                y=subset(bearish_indices, vol_mcap),
                mode="markers+text",
                text=subset(bearish_indices, text_labels),
                textposition="top center",
                textfont={"size": 9, "color": "#F6F8F7"},
                customdata=subset(bearish_indices, customdata),
                marker={
                    "size": 10,
                    "symbol": "circle",
                    "color": subset(bearish_indices, color_values),
                    "colorscale": colorscale,
                    "cmin": cmin,
                    "cmax": cmax,
                    "colorbar": None if (neutral_indices or bullish_indices) else {
                        "title": colorbar_title,
                        "tickvals": colorbar_tickvals,
                        "len": 0.8,
                        "tickfont": {"color": "#F6F8F7"},
                        "title_font": {"color": "#F6F8F7"},
                    },
                    "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
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
                        "tickfont": {"color": "#F6F8F7"},
                        "title_font": {"color": "#F6F8F7"},
                    },
                },
                showlegend=False,
            )
        )

    # Minimal corner legend for experienced users
    # Include ring explanation if multi_tf_divergence is enabled
    icon_legend = "○ Score 2+  ○○ Score 4"
    if multi_tf_divergence:
        icon_legend += "  |  Rings: 1w(in)→1h(out) green=bull red=bear"
    fig.add_annotation(
        x=0.99,
        y=0.99,
        xref="paper",
        yref="paper",
        text=icon_legend,
        showarrow=False,
        font={"size": 9, "color": "#F6F8F7"},
        align="right",
        bgcolor="rgba(74, 79, 94, 0.85)",
        bordercolor="rgba(246, 248, 247, 0.15)",
        borderwidth=1,
        borderpad=4,
        xanchor="right",
        yanchor="top",
    )

    fig.update_layout(
        title="",
        xaxis_title=x_axis_title,
        yaxis_title="Liquidity (Vol/MCap)",
        xaxis={
            "range": [0, 100],
            "dtick": 25,
            "gridcolor": "rgba(246, 248, 247, 0.08)",
            "zeroline": False,
            "title_font": {"color": "#F6F8F7"},
            "tickfont": {"color": "#F6F8F7"},
        },
        yaxis={
            "type": "log",
            "range": [log_min, log_max],
            "gridcolor": "rgba(246, 248, 247, 0.08)",
            "zeroline": False,
            "title_font": {"color": "#F6F8F7"},
            "tickfont": {"color": "#F6F8F7"},
        },
        showlegend=False,
        paper_bgcolor="#3E4253",
        plot_bgcolor="rgba(74, 79, 94, 0.3)",
        margin={"l": 60, "r": 100, "t": 30, "b": 60},
        autosize=True,
        height=height,
    )

    return fig


def build_acceleration_quadrant(
    coins: list[dict[str, Any]],
    height: int = 600,
    timeframe: str | None = None,
    multi_tf_rsi: dict[str, dict] | None = None,
) -> go.Figure:
    """
    Build scatter plot showing RSI acceleration vs volatility regime for opportunity detection.

    Quadrants:
    - Top-Right (>0, >1.3): Accelerating + High Vol = Explosive move in progress
    - Top-Left (<0, >1.3): Decelerating + High Vol = Move exhausting
    - Bottom-Right (>0, <0.7): Accelerating + Compressed = Coiled spring (BEST SIGNAL)
    - Bottom-Left (<0, <0.7): Decelerating + Compressed = Dormant

    Args:
        coins: List of coin dicts with keys:
            - id: Coin ID for multi_tf_rsi lookup
            - symbol: Coin symbol (e.g., "BTC")
            - daily_rsi: Daily RSI value (0-100) - used if no timeframe specified
            - acceleration: Dict with "acceleration" key - used if no timeframe specified
            - volatility: Dict with "ratio" key from detect_volatility_regime
        height: Chart height in pixels (default 600)
        timeframe: Selected timeframe ("1h", "4h", "12h", "1d", "3d", "1w") or None for daily
        multi_tf_rsi: Dict mapping coin_id -> {timeframe: {"rsi": float, "history": list}}

    Returns:
        Plotly Figure object with the quadrant scatter plot
    """
    from src.indicators import calculate_rsi_acceleration

    fig = go.Figure()

    # Determine timeframe label for display
    tf_label = timeframe.upper() if timeframe else "Daily"

    # Filter coins with volatility data and calculate acceleration for selected timeframe
    valid_coins = []
    for coin in coins:
        vol = coin.get("volatility")
        if vol is None:
            continue
        vol_ratio = vol.get("ratio")
        if vol_ratio is None:
            continue

        coin_id = coin.get("id")
        symbol = coin.get("symbol", "?")

        # Get RSI and acceleration based on timeframe
        rsi_val = None
        accel_val = None
        interpretation = "stable"

        if timeframe and multi_tf_rsi and coin_id in multi_tf_rsi:
            tf_data = multi_tf_rsi[coin_id].get(timeframe)
            if tf_data:
                rsi_val = tf_data.get("rsi")
                history = tf_data.get("history", [])
                if len(history) >= 3:
                    accel_result = calculate_rsi_acceleration(history)
                    if accel_result:
                        accel_val = accel_result.get("acceleration")
                        interpretation = accel_result.get("interpretation", "stable")
        else:
            # Fall back to daily (default behavior)
            rsi_val = coin.get("daily_rsi", 50)
            accel = coin.get("acceleration")
            if accel:
                accel_val = accel.get("acceleration")
                interpretation = accel.get("interpretation", "stable")

        if rsi_val is not None and accel_val is not None:
            valid_coins.append({
                "symbol": symbol,
                "rsi": rsi_val,
                "acceleration": accel_val,
                "volatility_ratio": vol_ratio,
                "volatility_regime": vol.get("regime", "normal"),
                "interpretation": interpretation,
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
    rsi_values = [c["rsi"] for c in valid_coins]

    # Build customdata for tooltips
    customdata = []
    for c in valid_coins:
        customdata.append([
            c["symbol"],
            c["rsi"],
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
        line={"color": "rgba(246,248,247,0.15)", "width": 1, "dash": "dot"}
    )
    # Horizontal line at y=0.7 (compressed threshold)
    fig.add_shape(
        type="line", x0=x_min, x1=x_max, y0=0.7, y1=0.7,
        line={"color": "rgba(246,248,247,0.15)", "width": 1, "dash": "dot"}
    )
    # Horizontal line at y=1.3 (expanded threshold)
    fig.add_shape(
        type="line", x0=x_min, x1=x_max, y0=1.3, y1=1.3,
        line={"color": "rgba(246,248,247,0.15)", "width": 1, "dash": "dot"}
    )

    # Add quadrant labels as annotations (cream color for dark theme)
    label_font = {"size": 24, "color": "rgba(246,248,247,0.10)", "family": "Arial Black"}

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
            textfont={"size": 9, "color": "#F6F8F7"},
            customdata=customdata,
            marker={
                "size": 12,
                "color": rsi_values,
                "colorscale": "RdYlGn_r",  # Low RSI = green (oversold = opportunity)
                "cmin": 0,
                "cmax": 100,
                "colorbar": {
                    "title": f"{tf_label} RSI",
                    "tickvals": [0, 25, 50, 75, 100],
                    "len": 0.8,
                    "tickfont": {"color": "#F6F8F7"},
                    "title_font": {"color": "#F6F8F7"},
                },
                "line": {"width": 1, "color": "rgba(255,255,255,0.4)"},
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{tf_label} RSI: " + "%{customdata[1]:.1f}<br>"
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
            "zerolinecolor": "rgba(246, 248, 247, 0.15)",
            "gridcolor": "rgba(246, 248, 247, 0.08)",
            "title_font": {"color": "#F6F8F7"},
            "tickfont": {"color": "#F6F8F7"},
        },
        yaxis={
            "range": [y_min, y_max],
            "zeroline": False,
            "gridcolor": "rgba(246, 248, 247, 0.08)",
            "title_font": {"color": "#F6F8F7"},
            "tickfont": {"color": "#F6F8F7"},
        },
        showlegend=False,
        paper_bgcolor="#3E4253",
        plot_bgcolor="rgba(74, 79, 94, 0.3)",
        margin={"l": 60, "r": 100, "t": 30, "b": 60},
        autosize=True,
        height=height,
    )

    return fig


def build_divergence_matrix(
    coin_data: list[dict],
    multi_tf_divergence: dict[str, dict],
) -> tuple[list[dict], list[str]]:
    """
    Build divergence analysis matrix showing multi-timeframe divergence status per coin.

    Creates a sortable grid view of divergences across all 6 timeframes, enabling
    quick identification of coins with multiple divergence alignments.

    Args:
        coin_data: List of coin dicts with keys:
            - id: CoinGecko coin ID
            - symbol: Coin symbol (e.g., "BTC")
        multi_tf_divergence: Dict mapping coin_id to timeframe divergence data:
            {coin_id: {timeframe: {"type": "bullish"|"bearish"|"none", "description": "..."}}}
            Timeframes: 1h, 4h, 12h, 1d, 3d, 1w

    Returns:
        Tuple of (matrix_data, column_order) where:
            - matrix_data: List of dicts ready for DataFrame display
            - column_order: ["Symbol", "1h", "4h", "12h", "1d", "3d", "1w", "Total"]

    Example output row:
        {
            "Symbol": "BTC",
            "1h": "🟢",
            "4h": "⚪",
            "12h": "🔴",
            ...
            "Total": 2
        }
    """
    # Timeframe order (left to right, ascending significance)
    TIMEFRAME_ORDER = ["1h", "4h", "12h", "1d", "3d", "1w"]

    # Emoji indicators matching the color scheme from DIVERGENCE_COLORS
    EMOJI_MAP = {
        "bullish": "🟢",  # Green - bullish divergence
        "bearish": "🔴",  # Red - bearish divergence
        "none": "⚪",     # Gray - no divergence
    }

    matrix_data = []

    for coin in coin_data:
        coin_id = coin.get("id")
        symbol = coin.get("symbol", "???")

        if not coin_id:
            continue

        # Get multi-TF divergence data for this coin
        coin_mtf = multi_tf_divergence.get(coin_id, {})

        # Build row data
        row = {"Symbol": symbol}
        total_divergences = 0

        for tf in TIMEFRAME_ORDER:
            tf_data = coin_mtf.get(tf, {})
            div_type = tf_data.get("type", "none") if tf_data else "none"

            # Get emoji indicator
            emoji = EMOJI_MAP.get(div_type, EMOJI_MAP["none"])
            row[tf] = emoji

            # Count non-none divergences
            if div_type != "none":
                total_divergences += 1

        row["Total"] = total_divergences
        matrix_data.append(row)

    # Sort by total divergence count descending, then alphabetically by symbol
    matrix_data.sort(key=lambda x: (-x["Total"], x["Symbol"]))

    # Column order for display
    column_order = ["Symbol"] + TIMEFRAME_ORDER + ["Total"]

    return matrix_data, column_order
