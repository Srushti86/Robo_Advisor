# Robo-Advisor Portfolio Tool

Live demo :

## What it does
takes a short risk questionnaire and generates an optimized portfolio allocation using mean-variance opitimization on real market data, with backtested performance metrics against the S&P 500.

## Methodology 
- Mean-variance optimization (Markowitz) via PyPortfolioOpt
- Leodoit-Wolf shrinkage covariance estimation for stability
- Constraints : max 25% per position, max 35% per sector
- Backtested against SPY over a 5-year historical window 

## Tech stack
Python • yfinance • pandas • PyPortfolioOpt • Streamlit • Plotly

## Running locally 
```
pip install -r requirements.txt
python src/data.py
streamlit run app.py
```

## Future improvements
- Factor-based expected return models
- Transaction cost and tax-aware rebalancing 
- User-uploaded custom ticker universes
- SQL-backed persistent user sessions