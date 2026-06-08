"""
charts/helpers.py
=================
Shared utilities used across the individual chart modules.
"""

import numpy as np
import pandas as pd


def safe_get(df: pd.DataFrame, ticker: str, col: str, default: float = np.nan) -> float:
    """Safely retrieve a scalar value from a fundamentals DataFrame.

    Returns ``default`` (NaN by default) rather than raising KeyError when
    the ticker or column is absent, so chart rendering continues gracefully.

    Parameters
    ----------
    df:
        The fundamentals DataFrame (output of collect_fundamentals).
    ticker:
        Row label (ticker symbol) to look up.
    col:
        Column name to retrieve.
    default:
        Value to return if the lookup fails. Defaults to NaN.
    """
    try:
        return df.loc[ticker, col]
    except KeyError:
        return default


def bubble_size(market_cap_b: float, scale: float = 10.0, floor: float = 8.0) -> float:
    """Convert market cap (billions) to a Plotly marker pixel size.

    Uses log1p scaling so large companies don't render absurdly oversized
    bubbles while still preserving relative size differences.

    Parameters
    ----------
    market_cap_b:
        Market capitalisation in billions USD.
    scale:
        Multiplier applied after log1p transform.
    floor:
        Minimum pixel size so tiny-cap companies remain visible.
    """
    if np.isnan(market_cap_b) or market_cap_b <= 0:
        return floor
    return max(np.log1p(float(market_cap_b)) * scale, floor)
