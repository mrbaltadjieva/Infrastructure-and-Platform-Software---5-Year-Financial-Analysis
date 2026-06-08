"""
charts/row2.py
==============
Row 2 panels:
  Col 1  Horizontal bar: trailing revenue ($M).
  Col 2  Grouped bar: operating margin vs net margin (%).
  Col 3  Bubble scatter: FCF ($M) vs revenue growth (%).
"""

import pandas as pd
import plotly.graph_objects as go

from config import COLORS
from charts.helpers import safe_get, bubble_size


def add_revenue_bar(fig, fundamentals: pd.DataFrame) -> None:
    """Horizontal bar chart of TTM revenue, sorted ascending.

    Sorted ascending so the largest bar appears at the top, which reads
    more naturally for a horizontal layout.

    Parameters
    ----------
    fig:
        Plotly figure to add the trace to.
    fundamentals:
        Snapshot fundamentals DataFrame (output of collect_fundamentals).
    """
    rev = fundamentals["Revenue_M"].sort_values()
    fig.add_trace(
        go.Bar(
            x=rev.values,
            y=rev.index,
            orientation="h",
            marker_color=[COLORS[t] for t in rev.index],
            text=[f"${v:,.0f}M" for v in rev.values],
            textposition="outside",
            name="Revenue",
            showlegend=False,
        ),
        row=2, col=1,
    )


def add_margin_bars(fig, fundamentals: pd.DataFrame, ticker_list: list[str]) -> None:
    """Grouped bar chart of operating margin vs net margin per ticker.

    Operating margin (full opacity) vs net margin (lower opacity) side by
    side. The gap between the two highlights interest expense and taxes.

    Parameters
    ----------
    fig:
        Plotly figure to add the traces to.
    fundamentals:
        Snapshot fundamentals DataFrame.
    ticker_list:
        Ordered list of ticker symbols.
    """
    op_margins  = [safe_get(fundamentals, t, "Operating_Margin") for t in ticker_list]
    net_margins = [safe_get(fundamentals, t, "Profit_Margin")    for t in ticker_list]

    fig.add_trace(
        go.Bar(
            x=ticker_list,
            y=op_margins,
            name="Op margin",
            marker_color=[COLORS[t] for t in ticker_list],
        ),
        row=2, col=2,
    )
    fig.add_trace(
        go.Bar(
            x=ticker_list,
            y=net_margins,
            name="Net margin",
            marker_color=[COLORS[t] for t in ticker_list],
            opacity=0.6,
        ),
        row=2, col=2,
    )


def add_fcf_scatter(fig, fundamentals: pd.DataFrame, ticker_list: list[str]) -> None:
    """Bubble scatter: FCF ($M) on y-axis vs revenue growth (%) on x-axis.

    Bubble size encodes market cap (log-scaled). The ideal quadrant is
    top-right (high FCF + high growth). Tickers in the bottom-left are
    shrinking and cash-constrained.

    Parameters
    ----------
    fig:
        Plotly figure to add the traces to.
    fundamentals:
        Snapshot fundamentals DataFrame.
    ticker_list:
        Ordered list of ticker symbols.
    """
    for t in ticker_list:
        mktcap = safe_get(fundamentals, t, "Market_Cap_B")
        fig.add_trace(
            go.Scatter(
                x=[safe_get(fundamentals, t, "Revenue_Growth")],
                y=[safe_get(fundamentals, t, "FCF_M")],
                mode="markers+text",
                text=[t],
                textposition="top center",
                marker=dict(
                    size=bubble_size(mktcap),
                    color=COLORS[t],
                    line=dict(width=1, color="white"),
                ),
                name=t,
                showlegend=False,
            ),
            row=2, col=3,
        )
