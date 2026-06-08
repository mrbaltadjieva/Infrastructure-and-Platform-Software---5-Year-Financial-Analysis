"""
data/financials.py
==================
Fetches annual income statement data and computes per-year margin metrics.
"""

import time
import numpy as np
import pandas as pd
import yfinance as yf


def collect_annual_financials(tickers: list[str], retries: int = 3) -> dict:
    """Fetch annual income statement data for each ticker.

    Supports both yfinance >=0.2.x (``income_stmt``) and older versions
    (``financials``), falling back gracefully between them.

    Parameters
    ----------
    tickers:
        List of ticker symbols.
    retries:
        Retry attempts per ticker with exponential backoff.

    Returns
    -------
    dict[str, pd.DataFrame]
        Maps ticker symbol to annual financials DataFrame (years as index,
        line items as columns). Tickers that fail are omitted.
    """
    annual: dict[str, pd.DataFrame] = {}

    for t in tickers:
        for attempt in range(retries):
            try:
                obj = yf.Ticker(t)

                fin = getattr(obj, "income_stmt", None)
                if fin is None or (hasattr(fin, "empty") and fin.empty):
                    fin = obj.financials

                fin = fin.T
                fin.index = pd.to_datetime(fin.index).year
                annual[t] = fin.sort_index()
                break

            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"  Warning: could not fetch financials for {t}: {e}")

    return annual


def annual_margins(annual: dict, ticker: str) -> pd.DataFrame:
    """Compute annual revenue, operating margin, and net margin for a ticker.

    Checks several known yfinance column name variants for operating income
    in priority order, to handle differences across API versions.

    Parameters
    ----------
    annual:
        Output of collect_annual_financials().
    ticker:
        The ticker symbol to extract data for.

    Returns
    -------
    pd.DataFrame
        Indexed by fiscal year (int), with columns:
          Revenue_M          Total revenue in millions USD.
          Operating_Margin   Operating income / revenue × 100 (%).
          Net_Margin         Net income / revenue × 100 (%).
        Returns an empty DataFrame if no data is available.
    """
    fin = annual.get(ticker)
    if fin is None or fin.empty:
        return pd.DataFrame()

    OP_COLS  = ["Operating Income", "EBIT", "Ebit"]
    NET_COLS = ["Net Income", "Net Income Common Stockholders"]
    REV_COLS = ["Total Revenue", "Revenue"]

    def _first_valid(row: pd.Series, candidates: list[str]) -> float:
        for c in candidates:
            val = row.get(c)
            if val is not None and pd.notna(val):
                return val
        return np.nan

    rows = []
    for yr, row in fin.iterrows():
        rev = _first_valid(row, REV_COLS)
        op  = _first_valid(row, OP_COLS)
        ni  = _first_valid(row, NET_COLS)

        if pd.notna(rev) and rev > 0:
            rows.append({
                "Year":             int(yr),
                "Revenue_M":        round(rev / 1e6, 1),
                "Operating_Margin": round(op / rev * 100, 1) if pd.notna(op) else np.nan,
                "Net_Margin":       round(ni / rev * 100, 1) if pd.notna(ni) else np.nan,
            })

    return pd.DataFrame(rows).set_index("Year")
