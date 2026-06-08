"""
charts/row3.py
==============
Row 3 panels:
  Col 1-2  Deep-dive per ticker: annual revenue bars + margin lines.
  Col 3    Horizontal bar: EV/Revenue multiples.
"""

import pandas as pd
import plotly.graph_objects as go

from config import COLORS


def add_deep_dive(fig, df: pd.DataFrame, ticker: str, col_idx: int) -> None:
    """Annual revenue bars (primary y) with margin lines (secondary y).

    The dual-axis layout keeps absolute revenue ($M) and percentage margins
    on independent scales so neither series becomes unreadable.

    Parameters
    ----------
    fig:
        Plotly figure to add the traces to.
    df:
        Output of data.financials.annual_margins() for this ticker.
    ticker:
        Ticker symbol — used for colour lookup and trace names.
    col_idx:
        Column index (1 or 2) in row 3 to place the traces.
    """
    if df.empty:
        return

    # Primary y-axis: annual revenue bars.
    fig.add_trace(
        go.Bar(
            x=df.index.astype(str),
            y=df["Revenue_M"],
            marker_color=COLORS[ticker],
            name=f"{ticker} revenue ($M)",
        ),
        row=3, col=col_idx, secondary_y=False,
    )

    # Secondary y-axis: operating margin line (dashed white).
    fig.add_trace(
        go.Scatter(
            x=df.index.astype(str),
            y=df["Operating_Margin"],
            mode="lines+markers",
            name=f"{ticker} op margin %",
            line=dict(color="white", dash="dash"),
        ),
        row=3, col=col_idx, secondary_y=True,
    )

    # Secondary y-axis: net margin line (amber dotted).
    fig.add_trace(
        go.Scatter(
            x=df.index.astype(str),
            y=df["Net_Margin"],
            mode="lines+markers",
            name=f"{ticker} net margin %",
            line=dict(color="#BA7517", dash="dot"),
        ),
        row=3, col=col_idx, secondary_y=True,
    )

    fig.update_yaxes(title_text="Margin (%)", row=3, col=col_idx, secondary_y=True)


def add_ev_revenue_bar(fig, fundamentals: pd.DataFrame) -> None:
    """Horizontal bar chart of EV/Revenue multiples, sorted ascending.

    A lower multiple implies cheaper valuation relative to revenue, though
    context matters — growth rate, margins, and sector norms all affect
    what a "fair" multiple looks like.

    Parameters
    ----------
    fig:
        Plotly figure to add the trace to.
    fundamentals:
        Snapshot fundamentals DataFrame (output of collect_fundamentals).
    """
    evr = fundamentals["EV_Revenue"].sort_values()
    fig.add_trace(
        go.Bar(
            x=evr.values,
            y=evr.index,
            orientation="h",
            marker_color=[COLORS[t] for t in evr.index],
            text=[f"{v:.1f}x" for v in evr.values],
            textposition="outside",
            name="EV/Revenue",
            showlegend=False,
        ),
        row=3, col=3,
    )
