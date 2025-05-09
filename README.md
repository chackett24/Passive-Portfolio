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
# How to Use This Repository

To run experiments:

- Navigate to one of the three main Jupyter notebooks:
  - `max_corr.ipynb`: First method tested
  - `attribution.ipynb`: Second method
  - `method3.ipynb`: Third method
- Modify the variables at the top of the notebook to set your desired testing parameters (e.g., number of assets, rebalancing frequency).
- Run all cells to execute the full pipeline.

To change the historical data range used in all methods, open `get_data.py` and update the `start` and `end` dates. This will apply globally across the repository.

# Repository Structure
```
├── ampl/                # AMPL model (.mod) and data (.dat) files
├── data/                # Cached CSVs to avoid repeated data downloads
├── Images/              # Matplotlib-generated plots and visual outputs
├── max_corr.ipynb       # Notebook for first method (correlation-based)
├── attribution.ipynb    # Notebook for second method (attribution-based)
├── method3.ipynb        # Notebook for third method
├── get_data.py          # Script for downloading and preprocessing historical data
```
## License

This project is intended for academic and research use only.
