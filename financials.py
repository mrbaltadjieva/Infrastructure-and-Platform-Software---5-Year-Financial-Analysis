"""
data/fundamentals.py
====================
Fetches a snapshot of current fundamental metrics for each ticker
from yfinance's .info dict (TTM figures + latest balance-sheet data).
"""

import time
import numpy as np
import pandas as pd
import yfinance as yf


def _fetch_ticker_info(ticker: str, retries: int = 3) -> dict:
    """Return the yfinance info dict for a single ticker, with retry/backoff.

    Parameters
    ----------
    ticker:
        A single Yahoo Finance ticker symbol, e.g. "PRGS".
    retries:
        Number of attempts before returning an empty dict.

    Returns
    -------
    dict
        The raw yfinance .info mapping, or {} if all attempts fail.
    """
    for attempt in range(retries):
        try:
            return yf.Ticker(ticker).info
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Warning: could not fetch info for {ticker}: {e}")
    return {}


def collect_fundamentals(tickers: dict[str, str]) -> pd.DataFrame:
    """Collect a snapshot of current fundamental metrics for each ticker.

    Missing numeric fields are stored as NaN (not 0) so that downstream
    charts can distinguish genuine zero values from absent data.

    Columns returned
    ----------------
    Market_Cap_B     Market capitalisation in billions USD.
    Revenue_M        Total revenue (TTM) in millions USD.
    Revenue_Growth   Year-over-year revenue growth as a percentage.
    Profit_Margin    Net profit margin as a percentage.
    Operating_Margin Operating margin as a percentage.
    FCF_M            Free cash flow (TTM) in millions USD.
    Beta             5-year monthly beta vs. S&P 500.
    PE_Ratio         Trailing price-to-earnings ratio.
    EV_Revenue       Enterprise value divided by trailing revenue.

    Parameters
    ----------
    tickers:
        Mapping of ticker symbol to company name (e.g. the TICKERS constant).

    Returns
    -------
    pd.DataFrame
        One row per ticker, indexed by ticker symbol.
    """
    def _pct(val) -> float:
        return round(val * 100, 1) if val is not None else np.nan

    def _b(val) -> float:
        return round(val / 1e9, 2) if val is not None else np.nan

    def _m(val) -> float:
        return round(val / 1e6, 1) if val is not None else np.nan

    def _r(val, n: int = 1) -> float:
        return round(val, n) if val is not None else np.nan

    rows = []
    for ticker, name in tickers.items():
        info = _fetch_ticker_info(ticker)
        rows.append({
            "Ticker":           ticker,
            "Name":             name,
            "Market_Cap_B":     _b(info.get("marketCap")),
            "Revenue_M":        _m(info.get("totalRevenue")),
            "Revenue_Growth":   _pct(info.get("revenueGrowth")),
            "Profit_Margin":    _pct(info.get("profitMargins")),
            "Operating_Margin": _pct(info.get("operatingMargins")),
            "FCF_M":            _m(info.get("freeCashflow")),
            "Beta":             _r(info.get("beta"), 2),
            "PE_Ratio":         _r(info.get("trailingPE"), 1),
            "EV_Revenue":       _r(info.get("enterpriseToRevenue"), 1),
        })

    return pd.DataFrame(rows).set_index("Ticker")
