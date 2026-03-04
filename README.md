# Psychometric Risk Profiler and Portfolio Optimizer

A Python tool that asks an investor 5 questions, figures out their risk appetite, and builds an optimal equity-bond portfolio using Markowitz Mean-Variance Optimization. It then plots the full efficient frontier and marks exactly where your portfolio sits on it.

---

## What it does

1. Runs a 5-question psychometric quiz and scores the investor from 5–15
2. Maps the score to Conservative, Moderate, or Aggressive
3. Each profile has a fixed equity-to-bond split and its own stock universe
4. Downloads 3 years of historical data from Yahoo Finance
5. Finds the portfolio weights that maximize the Sharpe Ratio within the equity-bond constraint
6. Plots the efficient frontier with 2000 random portfolios and marks your portfolio in red
7. Prints the final weights, expected return, volatility, and Sharpe Ratio

---

## Risk Profiles and Stock Universe

| Profile      | Equity | Bonds | Stocks used |
|--------------|--------|-------|-------------|
| Conservative  | 25%   | 75%   | HDFCBANK, TCS, NESTLEIND, INFY |
| Moderate      | 55%   | 45%   | RELIANCE, TCS, HDFCBANK, INFY  |
| Aggressive    | 80%   | 20%   | ZOMATO, MOTILALOFS, ADANIENT, TATAMOTORS |

Aggressive investors get high-beta names. Conservative investors get stable large-caps. The bond proxy used across all profiles is LIQUIDBEES (liquid ETF on NSE).

---

## Score Mapping

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

Answer the 5 questions. The script fetches data, optimizes, prints results, and opens the efficient frontier chart. The chart is also saved as `efficient_frontier.png`.

---

## Output

**Terminal:**
```
Your score: 13/15
Risk Profile: Aggressive (80% equity / 20% bonds)

--- Results for Aggressive Portfolio ---

Asset                  Weight
------------------------------
ZOMATO.NS              22.4%
MOTILALOFS.NS          18.7%
ADANIENT.NS            21.6%
TATAMOTORS.NS          17.3%
LIQUIDBEES.NS          20.0%
------------------------------

Expected Annual Return : 18.43%
Annual Volatility      : 23.11%
Sharpe Ratio           : 0.797
```

**Chart:**
- Blue dots — 2000 randomly generated portfolios
- Black curve — the efficient frontier (best possible return for each level of risk)
- Red dot — your optimized portfolio

---

## How the Optimization Works

The optimizer maximizes the Sharpe Ratio (return / volatility) subject to:
- All weights sum to 1
- Equity weights sum to exactly the profile target (e.g. 0.80 for Aggressive)

Bounds are 1%–60% per equity stock and up to 99% for the bond ETF. Risk-free rate is set to 6% per annum (standard India benchmark).

The efficient frontier is built by scanning a range of target returns and finding the minimum-volatility portfolio at each point.

---

## Files

```
portfolio_v3.py        — main script
efficient_frontier.png — output chart (generated on run)
README.md              — this file
```

---

## Dependencies

- `numpy` — matrix math for returns and covariance
- `pandas` — data wrangling
- `yfinance` — pulls historical price data from Yahoo Finance
- `scipy` — SLSQP optimizer
- `matplotlib` — efficient frontier plot
