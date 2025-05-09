# Passive Portfolio/Index Creation

This project investigates systematic methods for constructing simplified index-tracking portfolios. The goal is to create efficient, low-dimensional portfolios that closely approximate the behavior of broader market benchmarks, such as the S&P 100, while reducing the number of constituent assets.

We explore multiple techniques for selecting representative subsets of stocks based on market characteristics such as correlation, and attribute percentages. Each method is evaluated using out-of-sample testing across various rebalancing frequencies and portfolio sizes to assess performance and robustness.

## Project Structure

- **Data Collection**: Uses Yahoo Finance to gather historical weekly adjusted close prices for S&P 100 stocks (2020–2023).
- **Portfolio Construction**: Solves optimization problems to select subsets of assets based on maximum correlation coverage.
- **Weighting**: Selected stocks are weighted properly based on multiple methods.
- **Sensitivity Analysis**: Evaluates the performance of different portfolio sizes and rebalancing frequencies.
- **Performance Metrics**: Tracks portfolio returns, and correlations to the full index.

## AMPL Setup

This project uses [AMPL](https://ampl.com/) for solving the portfolio optimization models, integrated through the `amplpy` Python package.

Visit the [AMPL Academic Portal](https://portal.ampl.com/user/ampl/amplce/academic) for setup instructions.

This setup is required to run the optimization models from within the Python scripts provided in this repository.

## Requirements

- Python 3.8+
- `pandas`, `numpy`, `matplotlib`, `yfinance`
- `amplpy` with AMPL solver setup

```bash
pip install pandas numpy matplotlib yfinance amplpy
```

## License

This project is intended for academic and research use only.
