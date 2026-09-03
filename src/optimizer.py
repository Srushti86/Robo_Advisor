import pandas as pd
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

def load_returns() -> pd.DataFrame:
    """Load cached prices, excluding the Nifty 50 benchmark column."""
    prices = pd.read_parquet("data/prices.parquet")
    prices = prices.drop(columns=["^NSEI"], errors="ignore")
    return prices.dropna(axis=1, how="any")  #drop tickers with gaps

def _build_frontier(prices: pd.DataFrame):
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.25))

    try:
        meta = pd.read_csv("data/meta.csv").set_index("ticker")["sector"].to_dict()
        sectors = {t: meta.get(t, "Unknown") for t in prices.columns}
        unique_sectors = set(sectors.values())
        sector_upper = {s: 0.35 for s in unique_sectors}
        sector_lower = {s: 0.0 for s in unique_sectors}
        ef.add_sector_constraints(sectors, sector_lower, sector_upper)
    except FileNotFoundError:
        pass  # metadata optional; skip sector constraints if missing

    return ef, mu, S

def optimize(bucket: str) -> dict:
    """
    Return a cleaned weight dict for the given risk bucket.
    bucket: "Conservatie" | "Moderate" | "Aggressive"
    """
    prices = load_returns()

    if bucket == "Conservative":
        ef, _, _ = _build_frontier(prices)
        ef.min_volatility()

    elif bucket == "Aggressive":
        ef, _, _ = _build_frontier(prices)
        ef.max_sharpe()

    else: # Moderate blended target between min-vol and max-sharpe
        min_vol_ef, _, _ = _build_frontier(prices)
        min_vol_ef.min_volatility()
        min_vol = min_vol_ef.portfolio_performance()[1]

        ef, _, _ = _build_frontier(prices)
        ef.efficient_risk(target_volatility=min_vol * 1.5)

    return ef.clean_weights()

if __name__ == "__main__":
    for bucket in ["Conservative", "Moderate", "Aggressive"]:
        weights = optimize(bucket)
        nonzero = {k: v for k, v in weights.items() if v > 0.001}
        print(f"\n{bucket}:")
        for ticker, w in sorted(nonzero.items(), key=lambda x: -x[1]):
            print(f"{ticker}: {w:.2%}")