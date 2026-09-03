import streamlit as st
import pandas as pd
import plotly.express as px
import os

from src.risk_profile import(
    score_to_bucket, HORIZON_OPTIONS, HORIZON_POINTS,
    DRAWDOWN_OPTIONS, DRAWDOWN_POINTS, GOAL_OPTIONS, GOAL_POINTS
)
from src.optimizer import optimize, load_returns
from src.metrics import (
    portfolio_returns, sharpe_ratio, sortino_ratio, max_drawdown,
    annualized_vol, annualized_return, diversification_score,
    backtest_vs_benchmark,
)
from src.db import get_or_create_user, save_risk_profile, save_recommendation, get_user_history

st.set_page_config(page_title="Robo Advisor", layout="wide")

# Regenerate cached data on first run if missing (needed for cloud deploys
# that don't commit data/ to the repo)
if not os.path.exists("data/prices.parquet"):
    from src.data import fetch_and_cache, fetch_metadata
    with st.spinner("First-time setup: downloading market data..."):
        fetch_and_cache(force=True)
        fetch_metadata()

st.title("Portfolio Recommendation Engine")
st.caption("Risk based portfolio allocation using mean-variance optimization on real market data")

# --- Identify the user (simple username, no auth- good enough for a demo) ---
st.sidebar.header("Your Profile")
username = st.sidebar.text_input("Enter a username to save your results", value="guest")

st.header("1. Risk Questionnaire")
q1 = st.radio("What is your investment time horizon?", HORIZON_OPTIONS)
q2 = st.radio("If your portfolio dropped 20 percent in a month, you would:", DRAWDOWN_OPTIONS)
q3 = st.radio("What is your primary investment goal?", GOAL_OPTIONS)

answers = {
    "q1": HORIZON_POINTS[HORIZON_OPTIONS.index(q1)],
    "q2": DRAWDOWN_POINTS[DRAWDOWN_OPTIONS.index(q2)],
    "q3": GOAL_POINTS[GOAL_OPTIONS.index(q3)],
}

if st.button("Generate My Portfolio", type="primary"):
    score, bucket = score_to_bucket(answers)
    st.success(f"Risk Score: {score}/100 - **{bucket}**")

    with st.spinner("Optimizing portfolio..."):
        weights = optimize(bucket)
        weights = {k: v for k, v in weights.items() if v > 0.001}

    st.header("2. Recommended Allocation")
    col1, col2 = st.columns([1, 1])

    with col1:
        fig = px.pie(
            names=list(weights.keys()),
            values=list(weights.values()),
            title="Portfolio Weights",
        )
        st.plotly_chart(fig, width="stretch")

    prices = load_returns()
    rets = portfolio_returns(weights, prices)

    sharpe = sharpe_ratio(rets)
    sortino = sortino_ratio(rets)
    vol = annualized_vol(rets)
    dd = max_drawdown(rets)
    div_score = diversification_score(weights, prices)

    with col2:
        st.subheader("Portfolio Metrics")
        m1, m2 = st.columns(2)
        m1.metric("Sharpe Ratio", f"{sharpe_ratio(rets):.2f}")
        m1.metric("Sortino Ratio", f"{sortino_ratio(rets):.2f}")
        m2.metric("Annualized Return", f"{annualized_return(rets):.1%}")
        m2.metric("Annualized Volatility", f"{annualized_vol(rets):.1%}")
        st.metric("Max Drawdown", f"{max_drawdown(rets):.1%}")
        st.metric("Diversification Score", f"{diversification_score(weights, prices):.2f}")

    st.header("3. Backtest vs Nifty 50")
    nifty = pd.read_parquet("data/prices.parquet")["^NSEI"]
    port_cum, nifty_cum = backtest_vs_benchmark(weights, prices, nifty)
    chart_df = pd.DataFrame({"Portfolio": port_cum, "Nifty 50": nifty_cum})
    st.line_chart(chart_df)

    # --- Save to MySQL ---
    try:
        user_id = get_or_create_user(username)
        risk_profile_id = save_risk_profile(user_id, score, bucket)
        save_recommendation(
            risk_profile_id,
            weights,
            {
                "sharpe": sharpe,
                "sortino": sortino,
                "volatility": vol,
                "max_drawdown": dd,
                "diversification": div_score,
            },
        )
        st.toast("Saved to your portfolio history", icon="✅")
    except Exception as e:
        st.warning(f"Could not save to database: {e}")
        
    with st.expander("How this works"):
        st.write("""
        Allocations are generated via **mean-variance optimization** (Markowitz)
        using **Ledoit-Wolf shrinkage** on the covariance matrix for more stable
        estimates than raw sample covariance, constrained to a maximum 25% per 
        position and 35% per sector
        
        Your risk bucket determines where on the efficient frontier the 
        portfolio sits:
        - **Conservative** → minimum volatility portfolio
        - **Aggressive** → maximum Sharpe ratio portfolio
        - **Moderate** → a blended target between the two
        
        The backtest applies the optimized weights over the historical window
        and compares cumulative growth against a buy-and-hold Nifty 50 benchmark
        over the same period.
        """)
else:
    st.info("Answer the questions above and click **Generate My Portfolio** to see your results.")

# --- Past portfolios section ---
st.header("4. My Past Portfolios")
if username:
    try:
        history = get_user_history(username)
        if not history:
            st.write("No saved portfolios yet - generate one above.")
        else:
            for row in history:
                date_str = row["recommendation_date"].strftime("%b %d, %Y %T: %M %p") \
                    if row["recommendation_date"] else "N/A"
                with st.expander(f"{row['bucket']} portfolio - {date_str} (Sharpe: {row['sharpe_ratio']:.2f})"
                                 if row["sharpe_ratio"] else f"{row['bucket']} portfolio - {date_str}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Risk Score:** {row['score']}/100")
                    c1.write(f"**Sharpe Ratio:** {row['sharpe_ratio']:.2f}" if row["sharpe_ratio"] else "")
                    c1.write(f"**Volatility:** {row['annualized_volatility']:.1%}" if row["annualized_volatility"] else "")
                    c2.write(f"**Max Drawdown:** {row['max_drawdown']:.1%}" if row["max_drawdown"] else "")
                    c2.write(f"**Diversification:** {row['diversification_score']:.2f}" if row["diversification_score"] else "")
                    if row.get("weights"):
                        st.write("**Allocation:**")
                        st.json(row["weights"])
    except Exception as e:
        st.warning(f"Could not load history: {e}")