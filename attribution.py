#version with access to all sp100 tickers

import pandas as pd
import numpy as np
import yfinance as yf
from amplpy import AMPL

def attribute_index(qs, ms):
    correlations_dict = {}
    returns = pd.read_csv("data/returns.csv", index_col=0)
    sp100_returns = pd.read_csv("data/sp100returns.csv")
    combined = sp100_returns[['Portfolio_Return']].rename(columns={'Portfolio_Return': 'SP100'})

    binary_df = pd.read_csv("data/ticker_attributes.csv").set_index("Ticker")
    all_features = binary_df.columns.tolist()

    # Get full SP100 ticker list
    all_sp100_tickers = list(returns.columns)

    # Define fixed attribute targets 
    fixed_target_dict = {
        "SmallCap": .1,
        "MidCap": .1,
        "LargeCap": 1.0,
        "Tech": 0.6,
        "Finance": 0.8,
        "Healthcare": 0.3,
        "Consumer": 0.15,
        "Utilities": .2,
        "Energy": 0.2,
        "Industrial": 0.1,
        "Domestic": .99,
        "International": .5
    }

    for q in qs:
        for m in ms:
            #print(f"\n>>> Processing q={q}, m={m}")
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

            is_windows = []
            for i in range(1, m + 1):
                start_date = out_sample[out_sample['period'] == i].index[0]
                is_window = returns.loc[:start_date].iloc[-split_point:]
                is_windows.append(is_window)

            all_portfolio_returns = []

            for i in range(m):
                window_returns = is_windows[i]
                correlations = window_returns.corr()
                tickers = list(correlations.columns)

                # Step 1: run max_corr to select q tickers
                with open("data.txt", "w") as f:
                    f.write("set STOCKS := " + " ".join(tickers) + " ;\n\n")
                    f.write("param q := " + str(q) + " ;\n\n")
                    f.write("param r:\n    " + " ".join(tickers) + " :=\n")
                    for t1 in tickers:
                        row = " ".join(f"{correlations.loc[t1, t2]:.4f}" for t2 in tickers)
                        f.write(f"{t1} {row}\n")
                    f.write(";\n")

                ampl = AMPL()
                ampl.set_option('display_output', 0)
                ampl.set_option('solver_msg', 0)
                ampl.setOption("solver", "gurobi")
                ampl.read("max_corr.txt")
                ampl.readData("data.txt")
                ampl.solve()

                y = ampl.getVariable("y").getValues().to_pandas()
                selected = y[y["y.val"] == 1].index.tolist()

                if not selected:
                    print(f"(q={q}, m={m}) period {i+1}: No tickers selected — skipping.")
                    continue

                # Market cap weights on selected tickers
                market_caps = {}
                for ticker in selected:
                    try:
                        info = yf.Ticker(ticker).info
                        market_caps[ticker] = info.get('marketCap', 0)
                    except:
                        market_caps[ticker] = 0
                total_cap = sum(market_caps.values())
                weights = {t: market_caps[t] / total_cap if total_cap > 0 else 0 for t in selected}

                # Apply weights to all SP100 tickers (0 if not selected)
                full_weights = {t: weights.get(t, 0.0) for t in all_sp100_tickers}

                # Available features in the full SP100 set
                available = [feat for feat in all_features if binary_df.loc[all_sp100_tickers, feat].sum() > 0]
                target_dict = {feat: fixed_target_dict[feat] for feat in available if feat in fixed_target_dict}

                # Write full SP100 attribution file
                with open("attributes.dat", "w") as f:
                    f.write("set STOCKS := " + " ".join(all_sp100_tickers) + " ;\n\n")
                    f.write("set FEATURES := " + " ".join(available) + " ;\n\n")

                    f.write("param x_orig :=\n")
                    for t in all_sp100_tickers:
                        f.write(f"  {t} {full_weights[t]:.6f}\n")
                    f.write(";\n\n")

                    f.write("param a : " + " ".join(available) + " :=\n")
                    for t in all_sp100_tickers:
                        row = " ".join(str(int(binary_df.loc[t, feat])) for feat in available)
                        f.write(f"{t} {row}\n")
                    f.write(";\n\n")

                    f.write("param f :=\n")
                    for feat in available:
                        f.write(f"  {feat} {target_dict[feat]:.6f}\n")
                    f.write(";\n")

                ampl = AMPL()
                ampl.set_option('display_output', 0)
                ampl.set_option('solver_msg', 0)
                ampl.setOption("solver", "gurobi")
                ampl.read("attributes.mod.txt")
                ampl.readData("attributes.dat")
                ampl.solve()

                x = ampl.getVariable("x").getValues().to_pandas()
                nonzero = x[x["x.val"] > 0].reset_index()
                nonzero = nonzero.rename(columns={nonzero.columns[0]: "Ticker", nonzero.columns[1]: "x.val"})
                nonzero["Weight"] = nonzero["x.val"]
                nonzero["period"] = i + 1
                all_portfolio_returns.append(nonzero)

                #print(f"(q={q}, m={m}) period {i+1}: solution found with {len(nonzero)} non-zero weights")
                #print(nonzero[["Ticker", "Weight"]].sort_values(by="Weight", ascending=False).to_string(index=False))

            if all_portfolio_returns:
                weights_df = pd.concat(all_portfolio_returns)
                portfolio = pd.merge(out_sample_tall, weights_df, on=['period', 'Ticker'], how='inner')
                portfolio['Weighted_Return'] = portfolio['Return'] * portfolio['Weight']
                portfolio_return = portfolio.groupby('Date')['Weighted_Return'].sum().reset_index()
                portfolio_return = portfolio_return.rename(columns={'Weighted_Return': 'Portfolio_Return'})
                label = "(" + str(q) +"," + str(m) + ")"
                combined[label] = portfolio_return['Portfolio_Return']
                correlation = sp100_returns['Portfolio_Return'].corr(portfolio_return['Portfolio_Return'])
                correlations_dict[(q,m)] = correlation

    return correlations_dict, combined
