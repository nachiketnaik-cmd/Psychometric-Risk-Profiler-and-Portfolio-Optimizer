# Psychometric Risk Profiler and Portfolio Optimizer

A Python tool that asks an investor 5 simple questions, figures out their risk appetite, and then builds an optimal equity-bond portfolio using Markowitz Mean-Variance Optimization. The output includes asset weights and the portfolio's Sharpe Ratio.

---

## What it does

1. Runs a 5-question psychometric quiz to score the investor on a scale of 5–15
2. Maps the score to one of three risk profiles — Conservative, Moderate, or Aggressive
3. Each profile has a target equity-to-bond split (e.g. Moderate = 55% equity / 45% bonds)
4. Downloads 3 years of historical price data for 4 Indian equity stocks and a liquid bond ETF
5. Uses Scipy's optimizer to find the asset weights that maximize the Sharpe Ratio, while respecting the equity-bond constraint from the risk profile
6. Prints the final weights, expected annual return, volatility, and Sharpe Ratio

---

## Risk Profile Mapping

| Score (out of 15) | Profile     | Equity | Bonds |
|-------------------|-------------|--------|-------|
| 5 – 7             | Conservative | 25%   | 75%   |
| 8 – 11            | Moderate     | 55%   | 45%   |
| 12 – 15           | Aggressive   | 80%   | 20%   |

---

## Portfolio Universe

| Ticker         | Type   |
|----------------|--------|
| RELIANCE.NS    | Equity |
| TCS.NS         | Equity |
| HDFCBANK.NS    | Equity |
| INFY.NS        | Equity |
| LIQUIDBEES.NS  | Bond Proxy |

---

## Installation

```bash
pip install numpy pandas yfinance scipy
```

---

## Usage

```bash
python portfolio_v2.py
```

You will be prompted with 5 questions. After answering, the script fetches live data and prints your optimized portfolio.

---

## Sample Output

```
Your score: 11/15
Risk Profile: Moderate (55% equity / 45% bonds)

Fetching market data...

--- Results for Moderate Portfolio ---

Asset                  Weight
------------------------------
RELIANCE.NS            16.2%
TCS.NS                 14.8%
HDFCBANK.NS            12.6%
INFY.NS                11.4%
LIQUIDBEES.NS          45.0%
------------------------------

Expected Annual Return :  9.43%
Annual Volatility      : 11.27%
Sharpe Ratio           :  0.836
```

---

## How the Optimization Works

The optimizer minimizes the negative Sharpe Ratio (which is the same as maximizing it) subject to two constraints:

- All weights sum to 1
- The sum of equity weights equals the target from the risk profile

The risk-free rate is assumed to be 0 for simplicity. Weights are bounded between 1% and 60% per equity stock, and up to 99% for the bond ETF.

---

## Files

```
portfolio_v2.py   — main script
README.md         — this file
```

---

## Dependencies

- `numpy` — matrix operations for return and covariance calculations
- `pandas` — data handling
- `yfinance` — fetches historical price data from Yahoo Finance
- `scipy` — SLSQP optimizer for finding optimal weights
