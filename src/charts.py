"""Plotly chart builders for RSI scatter visualization."""

import plotly.graph_objects as go


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

    fig = go.Figure(
        data=go.Scatter(
            x=daily_rsi,
            y=vol_mcap,
            mode="markers+text",
            text=symbols,
            textposition="top center",
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
                "<b>%{text}</b><br>"
                "Daily RSI: %{x:.1f}<br>"
                "Vol/MCap: %{y:.4f}<br>"
                "Weekly RSI: %{marker.color:.1f}"
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

    return fig
