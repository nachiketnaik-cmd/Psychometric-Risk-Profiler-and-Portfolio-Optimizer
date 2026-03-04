import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# 5 questions, each scored 1-3. total score: 5 to 15

def questionnaire():
    print("\nAnswer the following 5 questions to determine your risk profile.")
    print("Enter 1, 2, or 3 for each question.\n")

    score = 0

    print("Q1. If your portfolio dropped 20% in a month, what would you do?")
    print("  1. Sell everything")
    print("  2. Hold and wait")
    print("  3. Buy more")
    score += int(input("Answer: "))

    print("\nQ2. What is your investment horizon?")
    print("  1. Less than 2 years")
    print("  2. 2 to 5 years")
    print("  3. More than 5 years")
    score += int(input("Answer: "))

    print("\nQ3. What is your main investment goal?")
    print("  1. Preserve capital")
    print("  2. Steady growth")
    print("  3. Maximum returns")
    score += int(input("Answer: "))

    print("\nQ4. How much of your savings are you investing?")
    print("  1. Less than 10%")
    print("  2. 10% to 30%")
    print("  3. More than 30%")
    score += int(input("Answer: "))

    print("\nQ5. How familiar are you with stock market investing?")
    print("  1. Not at all")
    print("  2. Some experience")
    print("  3. Quite experienced")
    score += int(input("Answer: "))

    return score


def get_risk_profile(score):
    if score <= 7:
        return "Conservative", 0.25, 0.75
    elif score <= 11:
        return "Moderate", 0.55, 0.45
    else:
        return "Aggressive", 0.80, 0.20


# conservative and moderate get stable large-caps
# aggressive gets high-beta names — zomato, motilal, adani, tata motors
EQUITY = {
    "Conservative": ["HDFCBANK.NS", "TCS.NS",        "NESTLEIND.NS",  "INFY.NS"],
    "Moderate":     ["RELIANCE.NS", "TCS.NS",         "HDFCBANK.NS",   "INFY.NS"],
    "Aggressive":   ["ETERNAL.NS",  "MOTILALOFS.NS",  "ADANIENT.NS",   "BAJFINANCE.NS"]
}

# bond is simulated as 6% annual return with low vol (2%)
# avoids yfinance data issues with Indian bond/gilt ETFs entirely
BOND_TICKER = "BOND_6PCT"

RF = 0.06   # risk-free rate — 6% per annum (standard India benchmark)


def fetch_returns(equity_tickers):
    data = yf.download(equity_tickers, period="3y", auto_adjust=True, progress=False)["Close"]
    data = data.dropna()
    eq_returns = data.pct_change().dropna()

    # simulate bond daily returns: mean = 6%/252, tiny noise to keep cov matrix stable
    n_days = len(eq_returns)
    np.random.seed(42)
    bond_daily = (RF / 252) + np.random.normal(0, 0.02 / np.sqrt(252), n_days)
    eq_returns[BOND_TICKER] = bond_daily

    return eq_returns


def portfolio_stats(w, mean_ret, cov):
    ret = w @ mean_ret
    vol = np.sqrt(w @ cov @ w)
    return ret, vol


def markowitz(returns, target_equity_weight):
    mean_ret = returns.mean() * 252
    cov      = returns.cov() * 252
    n        = len(mean_ret)

    def neg_sharpe(w):
        ret, vol = portfolio_stats(w, mean_ret.values, cov.values)
        return -((ret - RF) / vol)

    constraints = [
        {"type": "eq", "fun": lambda w: w.sum() - 1},
        {"type": "eq", "fun": lambda w: w[:-1].sum() - target_equity_weight}
    ]
    bounds = [(0.01, 0.60)] * (n - 1) + [(0.01, 0.99)]
    w0     = np.array([target_equity_weight / (n - 1)] * (n - 1) + [1 - target_equity_weight])

    result = minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    return result.x, mean_ret.values, cov.values


def efficient_frontier(mean_ret, cov):
    n       = len(mean_ret)
    cov_inv = np.linalg.inv(cov)
    ones    = np.ones(n)

    A = float(ones     @ cov_inv @ mean_ret)
    B = float(mean_ret @ cov_inv @ mean_ret)
    C = float(ones     @ cov_inv @ ones)
    D = B * C - A ** 2

    min_vol_ret = A / C
    min_vol_vol = np.sqrt(1.0 / C)

    # upper arm: returns FROM the tip going UP
    upper_targets = np.linspace(min_vol_ret, min_vol_ret + 0.40, 400)
    upper_vols    = np.sqrt((C * upper_targets**2 - 2*A*upper_targets + B) / D)

    # lower arm: returns FROM the tip going DOWN
    lower_targets = np.linspace(min_vol_ret, min_vol_ret - 0.30, 400)
    lower_vols    = np.sqrt((C * lower_targets**2 - 2*A*lower_targets + B) / D)

    return upper_vols, upper_targets, lower_vols, lower_targets, min_vol_vol, min_vol_ret


def plot_frontier(tickers, weights, mean_ret, cov, profile):
    print("\nBuilding efficient frontier...")

    upper_vols, upper_rets, lower_vols, lower_rets, min_vol_vol, min_vol_ret = efficient_frontier(mean_ret, cov)

    # user's portfolio
    p_ret, p_vol = portfolio_stats(weights, mean_ret, cov)
    p_sharpe     = (p_ret - RF) / p_vol

    # random portfolios — mix of long-only AND mild shorting
    # long-only fills the upper cloud, shorting fills the negative return zone
    n = len(mean_ret)
    rand_vols, rand_rets, rand_sharpes = [], [], []
    np.random.seed(0)

    # 3500 long-only portfolios — fills the upper feasible region
    for _ in range(3500):
        w = np.random.dirichlet(np.ones(n))
        r, v = portfolio_stats(w, mean_ret, cov)
        rand_vols.append(v)
        rand_rets.append(r)
        rand_sharpes.append((r - RF) / v)

    # 2000 short-selling portfolios — fills the lower/negative return zone
    attempts = 0
    short_count = 0
    while short_count < 2000 and attempts < 40000:
        attempts += 1
        w = np.random.randn(n) * 0.35
        w = w / w.sum()
        if np.any(np.abs(w) > 1.5):
            continue
        r, v = portfolio_stats(w, mean_ret, cov)
        if 0 < v < 0.65:
            rand_vols.append(v)
            rand_rets.append(r)
            rand_sharpes.append((r - RF) / v)
            short_count += 1

    rand_vols    = np.array(rand_vols)
    rand_rets    = np.array(rand_rets)
    rand_sharpes = np.array(rand_sharpes)

    # fixed colorbar range as requested
    vmin, vmax = -0.01, 1.5

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor("#f0f0f0")
    ax.set_facecolor("#f0f0f0")

    sc = ax.scatter(rand_vols, rand_rets, c=rand_sharpes, cmap="viridis",
                    s=18, alpha=0.6, zorder=2, vmin=vmin, vmax=vmax)

    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Sharpe Ratio", fontsize=11)
    cbar.set_ticks([-0.01, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50])

    # upper arm — solid (efficient)
    ax.plot(upper_vols, upper_rets, color="red", lw=2,
            linestyle="-", zorder=3, label="Efficient frontier")

    # lower arm — dashed (inefficient)
    ax.plot(lower_vols, lower_rets, color="red", lw=1.5,
            linestyle="--", zorder=3, label="Inefficient frontier")

    # minimum variance tip
    ax.scatter(min_vol_vol, min_vol_ret, s=100, color="orange", zorder=5,
               label=f"Min variance  ({min_vol_ret*100:.1f}% ret,  {min_vol_vol*100:.1f}% vol)")

    # user portfolio — bright yellow star so it reads as "high Sharpe" visually
    ax.scatter(p_vol, p_ret, s=350, color="yellow", edgecolors="black",
               linewidths=1.5, zorder=6, marker="*",
               label=f"Your portfolio ({profile})   Sharpe: {p_sharpe:.2f}")

    ax.set_xlabel("Volatility", fontsize=12)
    ax.set_ylabel("Return", fontsize=12)
    ax.set_title("Markowitz Efficient Frontier", fontsize=14)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.2f}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.2f}"))

    ax.legend(fontsize=9, loc="upper left", labelspacing=1.2,
              handletextpad=1.0, borderpad=1.0, framealpha=0.85)
    ax.grid(True, alpha=0.4, color="white")

    plt.tight_layout()
    plt.savefig("efficient_frontier.png", dpi=150)
    print("Chart saved as efficient_frontier.png")
    plt.show()


def print_results(tickers, weights, mean_ret, cov, profile):
    p_ret, p_vol = portfolio_stats(weights, mean_ret, cov)
    sharpe       = (p_ret - RF) / p_vol

    print(f"\n--- Results for {profile} Portfolio ---\n")
    print(f"{'Asset':<20} {'Weight':>8}")
    print("-" * 30)
    for t, w in zip(tickers, weights):
        print(f"{t:<20} {w*100:>7.1f}%")
    print("-" * 30)
    print(f"\nExpected Annual Return : {p_ret*100:.2f}%")
    print(f"Annual Volatility      : {p_vol*100:.2f}%")
    print(f"Sharpe Ratio           : {sharpe:.3f}")


def main():
    score                 = questionnaire()
    profile, eq_w, bond_w = get_risk_profile(score)

    print(f"\nYour score: {score}/15")
    print(f"Risk Profile: {profile} ({eq_w*100:.0f}% equity / {bond_w*100:.0f}% bonds)")

    print("\nFetching market data...")
    equity_tickers = EQUITY[profile]
    returns        = fetch_returns(equity_tickers)
    tickers        = equity_tickers + [BOND_TICKER]

    weights, mean_ret, cov = markowitz(returns, eq_w)
    print_results(tickers, weights, mean_ret, cov, profile)
    plot_frontier(tickers, weights, mean_ret, cov, profile)


main()