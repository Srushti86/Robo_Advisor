import yfinance as yf
import pandas as pd
import os

# NSE-listed large cap stocks across major sectors (India)
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "NESTLEIND.NS", "POWERGRID.NS",
]
BENCHMARK = "^NSEI"  # Nifty 50 index
ALL_TICKERS = TICKERS + [BENCHMARK]

def fetch_and_cache(force: bool = False) -> pd.DataFrame:
    """Download 5 years of daily adjusted close prices and cache to parquet."""
    path = "data/prices.parquet"
    os.makedirs("data", exist_ok=True)

    if os.path.exists(path) and not force:
        return pd.read_parquet(path)

    data = yf.download(ALL_TICKERS, period="5y", auto_adjust=True)["Close"]
    data = data.dropna(how="all")
    data.to_parquet(path)
    return data

def fetch_metadata() -> pd.DataFrame:
    """Pull sector and market-cap metadata for each ticker (excludes benchmark)."""
    rows = []
    for t in TICKERS:
        try:
            info = yf.Ticker(t).info
            rows.append({
                "ticker": t,
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap", None),
            })
        except Exception as e:
            print(f"Warning: could not fetch metadata for {t}: {e}")
            rows.append({"ticker": t, "sector": "Unknown", "market_cap": None})

    meta = pd.DataFrame(rows)
    meta.to_csv("data/meta.csv", index=False)
    return meta

if __name__ == "__main__":
    print("Fetching prices...")
    prices = fetch_and_cache(force=True)
    print(prices.tail())

    print("\nFetching metadata...")
    meta = fetch_metadata()
    print(meta.head())

    print("\nDone. Cached to data/prices.parquet and data/meta.csv")