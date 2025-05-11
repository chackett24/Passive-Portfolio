import yfinance as yf
import pandas as pd
import numpy as np
from amplpy import AMPL

def max_corr_index(qs, ms):
    correlations_dict = {}
    returns = pd.read_csv("data/returns.csv", index_col=0)
    sp100_returns = pd.read_csv('data/sp100returns.csv')
    combined = sp100_returns[['Portfolio_Return']].rename(columns={'Portfolio_Return': 'SP100'})
    for m in ms:
        # Prepare out-of-sample data
        split_point = int(0.7 * len(returns))
        out_sample = returns.iloc[split_point:].copy()
        n_rows = len(out_sample)
        period_length = n_rows // m
        periods = np.repeat(np.arange(1, m + 1), period_length)
        remainder = n_rows - len(periods)
        if remainder > 0:
            periods = np.append(periods, [m] * remainder)
        out_sample['period'] = periods
        out_sample_tall = out_sample.reset_index().melt(id_vars=["Date", "period"], var_name="Ticker", value_name="Return")
        

        # IS windows
        is_windows = []
        for i in range(1, m + 1):    
            start_date = out_sample[out_sample['period'] == i].index[0]
            is_window = returns.loc[:start_date].iloc[-split_point:]
            is_windows.append(is_window)

        for q in qs:
            results = []
            for i in range(m):
                window_returns = is_windows[i]
                correlations = window_returns.corr()

                with open("data.txt", "w") as f:
                    f.write("set STOCKS := " + " ".join(correlations.columns) + " ;\n\n")
                    f.write("param q := " + str(q) + " ;\n\n")
                    f.write("param r:\n    " + " ".join(correlations.columns) + " :=\n")
                    for t1 in correlations.columns:
                        row = " ".join(f"{correlations.loc[t1, t2]:.4f}" for t2 in correlations.columns)
                        f.write(f"{t1} {row}\n")
                    f.write(";\n")

                ampl = AMPL()
                ampl.setOption('solver', 'gurobi')
                ampl.set_option('display_output', 0)
                ampl.set_option('solver_msg', 0)
                ampl.read("max_corr.txt")
                ampl.read_data("data.txt")
                ampl.solve()
                y = ampl.get_variable("y").get_values().to_pandas()
                selected = y[y["y.val"] == 1]
                results.append(selected.index.tolist())

            # WEIGHTS HERE
            periods_all, tickers_all, weights_all = [], [], []
            for i in range(m):
                market_caps = {}
                for ticker in results[i]:
                    try:
                        info = yf.Ticker(ticker).info
                        market_caps[ticker] = info.get('marketCap', 0)
                    except Exception as e:
                        market_caps[ticker] = 0
                total_market_value = sum(market_caps.values())
                for ticker in results[i]:
                    cap = market_caps[ticker]
                    weight = cap / total_market_value if total_market_value > 0 else 0
                    periods_all.append(i + 1)
                    tickers_all.append(ticker)
                    weights_all.append(weight)

            weights_df = pd.DataFrame({
                'period': periods_all,
                'Ticker': tickers_all,
                'Weight': weights_all
            })
            # WEIGHTS END HERE

            portfolio = pd.merge(out_sample_tall, weights_df, on=['period', 'Ticker'], how='inner')
            portfolio['Weighted_Return'] = portfolio['Return'] * portfolio['Weight']
            portfolio_return = portfolio.groupby('Date')['Weighted_Return'].sum().reset_index()
            portfolio_return = portfolio_return.rename(columns={'Weighted_Return': 'Portfolio_Return'})
            label = "(" + str(q) +"," + str(m) + ")"
            combined[label] = portfolio_return['Portfolio_Return']
            correlation = sp100_returns['Portfolio_Return'].corr(portfolio_return['Portfolio_Return'])
            correlations_dict[(q,m)] = correlation

    return correlations_dict, combined