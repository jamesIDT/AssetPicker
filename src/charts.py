"""Plotly chart builders for RSI scatter visualization."""

import plotly.graph_objects as go


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


def build_rsi_scatter(coin_data: list[dict]) -> go.Figure:
    """
    Build scatter plot showing daily RSI vs liquidity with weekly RSI color encoding.

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

    Returns:
        Plotly Figure object with the scatter plot
    """
    if not coin_data:
        fig = go.Figure()
        fig.update_layout(
            title="RSI vs Liquidity",
            xaxis_title="Daily RSI",
            yaxis_title="Volume / Market Cap",
            annotations=[
                {
                    "text": "No data available",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                }
            ],
        )
        return fig

    symbols = [c["symbol"] for c in coin_data]
    daily_rsi = [c["daily_rsi"] for c in coin_data]
    vol_mcap = [c["vol_mcap_ratio"] for c in coin_data]
    weekly_rsi = [c["weekly_rsi"] for c in coin_data]

    # Prepare customdata for enhanced tooltips: [name, price, volume, mcap, weekly_rsi]
    customdata = [
        [
            c["name"],
            format_currency(c["price"]),
            format_currency(c["volume"]),
            format_currency(c["market_cap"]),
            c["weekly_rsi"],
        ]
        for c in coin_data
    ]

    fig = go.Figure(
        data=go.Scatter(
            x=daily_rsi,
            y=vol_mcap,
            mode="markers+text",
            text=symbols,
            textposition="top center",
            customdata=customdata,
            marker={
                "size": 12,
                "color": weekly_rsi,
                "colorscale": "RdYlGn_r",
                "cmin": 0,
                "cmax": 100,
                "colorbar": {
                    "title": "Weekly RSI",
                    "tickvals": [0, 25, 50, 75, 100],
                },
            },
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{text})<br>"
                "Price: %{customdata[1]}<br>"
                "Volume: %{customdata[2]}<br>"
                "Market Cap: %{customdata[3]}<br>"
                "Daily RSI: %{x:.1f}<br>"
                "Weekly RSI: %{customdata[4]:.1f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="RSI vs Liquidity",
        xaxis_title="Daily RSI",
        yaxis_title="Volume / Market Cap",
        xaxis={
            "range": [0, 100],
            "dtick": 10,
        },
        yaxis={
            "type": "log",
        },
        showlegend=False,
    )

    # Add zone shading for oversold (green, 0-30) and overbought (red, 70-100)
    fig.add_vrect(
        x0=0,
        x1=30,
        fillcolor="green",
        opacity=0.1,
        layer="below",
        line_width=0,
    )
    fig.add_vrect(
        x0=70,
        x1=100,
        fillcolor="red",
        opacity=0.1,
        layer="below",
        line_width=0,
    )

    return fig
