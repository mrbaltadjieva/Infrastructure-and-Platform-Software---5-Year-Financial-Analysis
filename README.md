# Financial Dashboard

Interactive 5-year competitive analysis dashboard for a configurable set of
publicly traded companies. Built with [yfinance](https://github.com/ranaroussi/yfinance)
and [Plotly](https://plotly.com/python/).

## Dashboard panels

| Row | Panel | Description |
|-----|-------|-------------|
| 1 | Price performance | All tickers indexed to 100 at the start of the 5-year window |
| 2 | Revenue (TTM) | Trailing twelve-month revenue in $M, sorted ascending |
| 2 | Margins | Operating margin vs net margin (%) side by side |
| 2 | FCF vs growth | Bubble scatter — FCF on y, revenue growth on x, bubble = market cap |
| 3 | Deep dive × 2 | Annual revenue bars + operating/net margin lines (dual axis) |
| 3 | EV/Revenue | Enterprise value / revenue multiple, sorted ascending |

## Quickstart

```bash
pip install -r requirements.txt
python main.py
```

The dashboard is saved as `financial_dashboard.html` and opened automatically
in your default browser. A CSV snapshot of fundamentals is written to
`fundamentals_snapshot.csv`.

## Configuration

All settings live in **`config.py`**:

| Variable | Purpose |
|----------|---------|
| `TICKERS` | Dict of `{symbol: display_name}` — add/remove companies here |
| `COLORS` | Hex colour per ticker, used consistently across every chart |
| `DEEP_DIVE_TICKERS` | Which two tickers get the annual deep-dive panels in row 3 |
| `OUTPUT_PATH` | Where the HTML file is saved (default: next to `main.py`) |
| `CSV_PATH` | Where the fundamentals CSV is saved (default: next to `main.py`) |

## Project structure

```
.
├── main.py                  # Entry point
├── config.py                # Tickers, colours, paths
├── requirements.txt
├── data/
│   ├── prices.py            # Price download + indexing
│   ├── fundamentals.py      # TTM fundamentals snapshot
│   └── financials.py        # Annual income statements + margin calcs
└── charts/
    ├── dashboard.py         # Assembles the full figure
    ├── helpers.py           # safe_get, bubble_size utilities
    ├── row1.py              # Price performance chart
    ├── row2.py              # Revenue, margin, FCF scatter
    └── row3.py              # Deep dives + EV/Revenue
```

## Notes

- Data is sourced from Yahoo Finance via yfinance. Availability and accuracy
  depend on Yahoo's data feeds.
- All numeric fields default to `NaN` (not `0`) when data is unavailable,
  so charts clearly distinguish missing data from genuine zero values.
- The HTML output embeds the full Plotly JS bundle and works fully offline.
