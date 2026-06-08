"""
charts/dashboard.py
===================
Assembles and saves the full 3×3 Plotly dashboard.

Layout
------
Row 1  Stock price indexed to 100 (full width, 5 years).
Row 2  Revenue (TTM) | Operating vs net margin | FCF vs revenue growth.
Row 3  Deep dive ticker 1 | Deep dive ticker 2 | EV/Revenue multiples.
"""

import os
import webbrowser

import pandas as pd
from plotly.subplots import make_subplots

from config import TICKERS, COLORS, DEEP_DIVE_TICKERS, OUTPUT_PATH
from data.prices import indexed_prices
from data.financials import annual_margins
from charts import helpers
from charts.row1 import add_price_chart
from charts.row2 import add_revenue_bar, add_margin_bars, add_fcf_scatter
from charts.row3 import add_deep_dive, add_ev_revenue_bar


def plot_dashboard_plotly(
    prices: pd.DataFrame,
    fundamentals: pd.DataFrame,
    annual: dict,
    output_path: str = OUTPUT_PATH,
) -> None:
    """Build and save the interactive Plotly dashboard as a standalone HTML file.

    Parameters
    ----------
    prices:
        Monthly adjusted close prices (output of collect_price_data).
    fundamentals:
        Snapshot fundamentals table (output of collect_fundamentals).
    annual:
        Annual income statement data (output of collect_annual_financials).
    output_path:
        Destination path for the HTML file.
    """
    idx = indexed_prices(prices) if not prices.empty else pd.DataFrame()
    ticker_list = list(TICKERS.keys())

    # Validate deep-dive tickers; pad with available tickers if needed.
    deep_dive = [t for t in DEEP_DIVE_TICKERS if t in TICKERS][:2]
    if len(deep_dive) < 2:
        deep_dive = (deep_dive + ticker_list)[:2]

    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            "Stock price - indexed to 100 (5 years)",
            "Revenue (TTM, $M)",
            "Operating vs net margin (%)",
            "FCF vs revenue growth",
            f"Deep dive: {deep_dive[0]}",
            f"Deep dive: {deep_dive[1]}",
            "EV / Revenue",
        ),
        specs=[
            [{"colspan": 3, "secondary_y": False}, None, None],
            [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": True},  {"secondary_y": True},  {"secondary_y": False}],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Row 1
    add_price_chart(fig, idx, ticker_list)

    # Row 2
    add_revenue_bar(fig, fundamentals)
    add_margin_bars(fig, fundamentals, ticker_list)
    add_fcf_scatter(fig, fundamentals, ticker_list)

    # Row 3
    for col_idx, ticker in enumerate(deep_dive, start=1):
        df = annual_margins(annual, ticker)
        add_deep_dive(fig, df, ticker, col_idx)

    add_ev_revenue_bar(fig, fundamentals)

    # Global layout
    fig.update_layout(
        height=1800,
        title=dict(
            text="Infrastructure & Platform Software - 5-Year Analysis",
            font=dict(size=20),
        ),
        template="plotly_dark",
        showlegend=True,
        barmode="group",
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
    )

    # Save
    abs_path = os.path.abspath(output_path)
    fig.write_html(
        abs_path,
        config={"scrollZoom": True, "displayModeBar": True},
        full_html=True,
        include_plotlyjs=True,
    )
    print(f"  Dashboard saved -> {abs_path}")

    try:
        webbrowser.open(f"file://{abs_path}", new=2)
        print("  Opened in browser.")
    except Exception as e:
        print(f"  Could not auto-open browser: {e}")
