import pandas as pd
import numpy as np

def portfolio_returns(weights: dict, prices: pd.DataFrame) -> pd.Series:
    """Compute daily portfolio returns given weights and a price DataFrame."""
    rets = prices.pct_change().dropna()
    w = pd.Series(weights)
    common = [t for t in w.index if t in rets.columns]
    return (rets[common] * w[common]).sum(axis=1)

def sharpe_ratio(port_rets: pd.Series, rf: float = 0.02) -> float:
    excess = port_rets - rf / 252
    if excess.std() == 0:
        return 0.0
    return (excess.mean() / excess.std()) * np.sqrt(252)

def sortino_ratio(port_rets: pd.Series, rf: float = 0.02) -> float:
    downside = port_rets[port_rets < 0]
    if len(downside) == 0 or downside.std() == 0:
        return 0.0
    excess = port_rets.mean() - rf / 252
    return (excess / downside.std()) * np.sqrt(252)

def max_drawdown(port_rets: pd.Series) -> float:
    cum = (1 + port_rets).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    return dd.min()

def annualized_vol(port_rets: pd.Series) -> float:
    return port_rets.std() * np.sqrt(252)

def annualized_return(port_rets: pd.Series) -> float:
    cum = (1 + port_rets).cumprod()
    n_years = len(port_rets) / 252
    return cum.iloc[-1] ** (1 / n_years) - 1

def diversification_score(weights: dict, prices: pd.DataFrame) -> float:
    """1 minus average pairwise correlation among held positions."""
    tickers = [t for t in weights.keys() if weights[t] > 0.001]
    if len(tickers) < 2:
        return 0.0
    rets = prices.pct_change().dropna()
    corr = rets[tickers].corr()
    n = len(tickers)
    avg_corr = (corr.values.sum() - n) / (n * n - n)
    return 1 - avg_corr

def backtest_vs_benchmark(weights: dict, prices: pd.DataFrame, spy_prices: pd.Series):
    """Return cumulative return series for the portfolio and SPY over the same window."""
    port_rets = portfolio_returns(weights, prices)
    port_cum = (1 + port_rets).cumprod()
    spy_rets = spy_prices.pct_change().dropna()
    spy_rets = spy_rets.reindex(port_rets.index).dropna()
    spy_cum = (1 + spy_rets).cumprod()
    return port_cum, spy_cum

if __name__ == "__main__":
    from optimizer import optimize, load_returns

    weights = optimize("Moderate")
    prices = load_returns()
    rets = portfolio_returns(weights, prices)

    print(f"Sharpe Ratio:         {sharpe_ratio(rets):.3f}")
    print(f"Sortino Ratio:        {sortino_ratio(rets):.3f}")
    print(f"Annualized Return:    {annualized_return(rets):.2%}")
    print(f"Annualized Vol:       {annualized_vol(rets):.2%}")
    print(f"Max Drawdown:         {max_drawdown(rets):.2%}")
    print(f"Diversification:      {diversification_score(weights, prices):.3f}")