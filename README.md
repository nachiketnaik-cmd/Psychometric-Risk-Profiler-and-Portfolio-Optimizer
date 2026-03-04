# Psychometric Risk Profiler and Markowitz Portfolio Optimizer

A Python tool that scores an investor's risk appetite through 5 questions and then builds an optimized equity-bond portfolio using Markowitz Mean-Variance Optimization. The output includes optimal asset weights, expected return, volatility, Sharpe Ratio, and a full efficient frontier chart.

---

## What it does

1. Runs a 5-question psychometric quiz, scoring the investor from 5 to 15
2. Maps the score to Conservative, Moderate, or Aggressive
3. Each profile has a fixed equity-to-bond split and its own stock universe
4. Downloads 3 years of historical price data from Yahoo Finance
5. Simulates a bond with 6% annual return and 2% volatility (avoids yfinance data issues with Indian gilt ETFs)
6. Finds the portfolio weights that maximize the Sharpe Ratio, constrained to the profile's equity-bond split
7. Plots the full Markowitz efficient frontier — both arms of the hyperbola — with 5500 random portfolios colored by Sharpe Ratio, and marks your portfolio on it
8. Saves the chart as `efficient_frontier.png`

---

## Risk Profiles and Stock Universe

| Profile      | Equity | Bonds | Stocks |
|--------------|--------|-------|--------|
| Conservative  | 25%   | 75%   | HDFCBANK, TCS, NESTLEIND, INFY |
| Moderate      | 55%   | 45%   | RELIANCE, TCS, HDFCBANK, INFY |
| Aggressive    | 80%   | 20%   | ETERNAL (Zomato), MOTILALOFS, ADANIENT, BAJFINANCE |

Aggressive investors get high-beta names. Conservative investors get defensive large-caps. The bond across all profiles is a simulated instrument returning 6% annually with 2% volatility — seeded so results are reproducible.

---

## Score to Profile Mapping

| Score (out of 15) | Profile      |
|-------------------|--------------|
| 5 – 7             | Conservative |
| 8 – 11            | Moderate     |
| 12 – 15           | Aggressive   |

---

## Installation

```bash
pip install numpy pandas yfinance scipy matplotlib
```

---

## Usage

```bash
python portfolio_v3.py
```

Answer the 5 questions. The script fetches data, runs the optimizer, prints the results in the terminal, and opens the efficient frontier chart.

---

## Terminal Output

```
Your score: 13/15
Risk Profile: Aggressive (80% equity / 20% bonds)

--- Results for Aggressive Portfolio ---

Asset                  Weight
------------------------------
ETERNAL.NS              21.3%
MOTILALOFS.NS           19.8%
ADANIENT.NS             22.6%
BAJFINANCE.NS           16.3%
BOND_6PCT               20.0%
------------------------------

Expected Annual Return : 39.40%
Annual Volatility      : 23.23%
Sharpe Ratio           : 1.442
```

---

## The Efficient Frontier Chart

The chart plots 5500 random portfolios as dots colored by their Sharpe Ratio (viridis colormap, scale fixed from -0.01 to 1.50). The red curve is the analytical Markowitz frontier, split into two arms:

- **Solid red line** — efficient frontier (upper arm). Rational investors pick here — maximum return for a given level of risk
- **Dashed red line** — inefficient frontier (lower arm). Same risk, lower return. Arises from short-selling high-return stocks while holding low-return assets
- **Orange dot** — minimum variance portfolio, the tip of the hyperbola where the two arms meet
- **Yellow star** — your optimized portfolio

The 5500 random portfolios are a mix of 3500 long-only (Dirichlet weights) and 2000 short-selling portfolios. The long-only batch fills the upper feasible region; the short-selling batch populates the lower/negative return zone that would otherwise be empty.

---

## How the Optimization Works

The optimizer uses Scipy's SLSQP method to maximize the Sharpe Ratio subject to two constraints:

- All weights sum to 1
- Equity weights sum to exactly the profile's target (e.g. 0.80 for Aggressive)

Bounds are 1%–60% per equity stock and 1%–99% for the bond.

The efficient frontier itself is computed analytically using the closed-form Merton (1972) solution:

```
σ²(μ) = (C·μ² − 2A·μ + B) / D
```

where A, B, C, D are scalar quantities derived from the inverse covariance matrix and mean return vector. This gives the exact hyperbola with no optimizer needed — instantaneous and numerically stable.

Risk-free rate is fixed at **6% per annum**, the standard Indian benchmark.

---

## Files

```
portfolio_v3.py          — main script
efficient_frontier.png   — output chart (generated on run)
README.md                — this file
```

---

## Dependencies

| Library | Purpose |
|---------|---------|
| `numpy` | Matrix math — covariance, dot products, inverse |
| `pandas` | Data handling for price series |
| `yfinance` | Fetches 3-year historical price data from Yahoo Finance |
| `scipy` | SLSQP optimizer for Sharpe maximization |
| `matplotlib` | Efficient frontier chart and colorbar |
