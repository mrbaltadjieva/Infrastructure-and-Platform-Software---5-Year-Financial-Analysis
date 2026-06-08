"""
charts/row1.py
==============
Row 1: indexed price performance chart (full-width, spans all 3 columns).
"""

import pandas as pd
import plotly.graph_objects as go

from config import COLORS


def add_price_chart(fig, idx: pd.DataFrame, ticker_list: list[str]) -> None:
    """Add indexed price lines for all tickers to row 1.

    Each series is normalised to 100 at the first observation.
    A dashed baseline at y=100 makes outperformance/underperformance
    immediately visible.

    Parameters
    ----------
    fig:
        The Plotly figure (make_subplots instance) to add traces to.
    idx:
        Indexed price DataFrame (output of data.prices.indexed_prices).
    ticker_list:
        Ordered list of ticker symbols to plot.
    """
    for t in ticker_list:
        if not idx.empty and t in idx.columns:
            fig.add_trace(
                go.Scatter(
                    x=idx.index,
                    y=idx[t],
                    mode="lines",
                    name=t,
                    line=dict(color=COLORS[t], width=2),
                ),
                row=1, col=1,
            )

    fig.add_hline(y=100, line_dash="dash", opacity=0.3, row=1, col=1)
