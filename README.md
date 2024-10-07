# Stock Tracker AMD
A Python-based tool for automated tracking of AMD stock price movements against predefined percentage targets.
Note: This project is not a financial advice tool. Always consult a financial professional before making investment decisions. It's a purely educational project.

## Overview

This project automatically fetches daily AMD stock data and tracks when the stock reaches specific percentage increase targets (1.2%, 1.5%, and 2.2%). It maintains a historical record of price movements and provides summary statistics.

## Features

- Automated data collection using Yahoo Finance API
- Tracks multiple percentage increase targets
- Maintains historical data in CSV format
- Provides summary statistics of target achievements
- Easy to customize for different targets or time periods

## Requirements

- Python 3.6+
- pandas
- yfinance

## Installation

```bash
git clone <https://github.com/yourusername/amd-target-tracker.git>
cd amd-target-tracker
pip install -r requirements.txt

```

## Usage

Run the script daily to track AMD stock movements:

```bash
python amd_tracker.py

```

## Sample Output

```
Recorded data for 2024-10-02: 1.8% change

Summary of 30 trading days:
Reached 1.2% target: 12 days (40.0% of the time)
Reached 1.5% target: 8 days (26.7% of the time)
Reached 2.2% target: 3 days (10.0% of the time)

```

## License

[Apacher License 2.0](LICENSE)

## Contributing

Contributions, issues, and feature requests are welcome.