import pandas as pd
import numpy as np
import random

def attribute_index_random(qs, ms, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    # Load pre-saved market caps
    market_caps_dict = pd.read_csv("data/market_caps.csv", index_col=0)["MarketCap"].to_dict()

    correlations_dict = {}
    returns = pd.read_csv("data/returns.csv", index_col=0)
    sp100_returns = pd.read_csv("data/sp100returns.csv")
    combined = sp100_returns[['Portfolio_Return']].rename(columns={'Portfolio_Return': 'SP100'})

    binary_df = pd.read_csv("data/ticker_attributes.csv").set_index("Ticker")
    all_features = binary_df.columns.tolist()
    all_sp100_tickers = list(returns.columns)

    for q in qs:
        for m in ms:
            split_point = int(0.7 * len(returns))
            out_sample = returns.iloc[split_point:].copy()
            n_rows = len(out_sample)
            period_length = n_rows // m
            periods = np.repeat(np.arange(1, m + 1), period_length)
            if n_rows % m != 0:
                periods = np.append(periods, [m] * (n_rows - len(periods)))
            out_sample['period'] = periods
            out_sample_tall = out_sample.reset_index().melt(
                id_vars=["Date", "period"], var_name="Ticker", value_name="Return"
            )

            all_portfolio_returns = []

            for i in range(1, m + 1):
                selected = random.sample(all_sp100_tickers, q)

                # Use preloaded market cap data
                market_caps = {ticker: market_caps_dict.get(ticker, 0) for ticker in selected}
                total_cap = sum(market_caps.values())
                weights = {t: market_caps[t] / total_cap if total_cap > 0 else 1.0/q for t in selected}

                full_weights = {t: weights.get(t, 0.0) for t in all_sp100_tickers}

                period_weights = pd.DataFrame({
                    'Ticker': list(full_weights.keys()),
                    'Weight': list(full_weights.values()),
                    'period': i
                })
                period_weights = period_weights[period_weights['Weight'] > 0]
                all_portfolio_returns.append(period_weights)

            if all_portfolio_returns:
                weights_df = pd.concat(all_portfolio_returns)
                portfolio = pd.merge(out_sample_tall, weights_df, on=['period', 'Ticker'], how='inner')
                portfolio['Weighted_Return'] = portfolio['Return'] * portfolio['Weight']
                portfolio_return = portfolio.groupby('Date')['Weighted_Return'].sum().reset_index()
                portfolio_return = portfolio_return.rename(columns={'Weighted_Return': 'Portfolio_Return'})
                label = f"({q},{m})"
                combined[label] = portfolio_return['Portfolio_Return']
                correlation = sp100_returns['Portfolio_Return'].corr(portfolio_return['Portfolio_Return'])
                correlations_dict[(q,m)] = correlation

    return correlations_dict, combined
