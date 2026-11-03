# Robo-Advisor Portfolio Tool

Live demo : https://srushti-roboadvisor.streamlit.app/

## What it does
Takes a short risk questionnaire and generates an optimized portfolio allocation using mean-variance optimization on real Indian market data (NSE large cap stocks), with backtested performance metrics against the Nifty 50 index.

## Methodology 
- Mean-variance optimization (Markowitz) via PyPortfolioOpt
- Ledoit-Wolf shrinkage covariance estimation for stability
- Constraints : max 25% per position, max 35% per sector
- Backtested against the Nifty 50 (^NSEI) over a 5-year historical window 
- User risk profiles and portfolio recommendations persisted in a MySQL database (hosted on Railway)

## Tech stack
Python • yfinance • pandas • PyPortfolioOpt • Streamlit • Plotly • MySQL  

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
