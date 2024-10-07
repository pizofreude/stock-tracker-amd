import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class AutomatedAMDTracker:
    def __init__(self, targets=[1.2, 1.5, 2.2]):
        self.targets = sorted(targets)
        self.symbol = "AMD"
        try:
            self.df = pd.read_csv('amd_stock_tracking.csv')
            logging.info("Loaded existing tracking data")
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['date', 'starting_price', 'ending_price',
                                           'daily_change_pct', 'targets_reached'])
            logging.info("Created new tracking dataframe")

    def fetch_daily_data(self):
        today = datetime.now()
        previous_trading_day = today - timedelta(days=1)

        # Find the last trading day
        while previous_trading_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
            previous_trading_day -= timedelta(days=1)

        today_str = today.strftime('%Y-%m-%d')
        previous_trading_day_str = previous_trading_day.strftime('%Y-%m-%d')

        stock = yf.Ticker(self.symbol)
        history = stock.history(start=previous_trading_day_str, end=today_str)

        if history.empty:
            return None, "No data available for the specified date range"

        return history, None

    def update_tracking(self):
        history, error = self.fetch_daily_data()

        if error:
            logging.error(f"Error fetching data: {error}")
            return error

        if history.empty:
            logging.info("No new data to process")
            return "No new data to process"

        latest_data = history.iloc[-1]
        date = latest_data.name.strftime('%Y-%m-%d')

        # Check for existing date
        if date in self.df['date'].str.strip().values:
            return f"Data for {date} already recorded"

        start_price = latest_data['Open']
        end_price = latest_data['Close']
        change_pct = ((end_price - start_price) / start_price) * 100

        # Check which targets were reached
        targets_reached = [target for target in self.targets if change_pct >= target]
        targets_reached_str = ', '.join(map(str, targets_reached)) if targets_reached else 'None'

        # Add new row to dataframe
        new_row = pd.DataFrame({
            'date': [date],
            'starting_price': [round(start_price, 2)],
            'ending_price': [round(end_price, 2)],
            'daily_change_pct': [round(change_pct, 2)],
            'targets_reached': [targets_reached_str]
        })

        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.df.to_csv('amd_stock_tracking.csv', index=False)

        return f"Recorded data for {date}: {change_pct:.2f}% change"

    def get_summary(self):
        if self.df.empty:
            return "No data recorded yet."

        total_days = len(self.df)
        days_reached_targets = {
            target: len(self.df[self.df['daily_change_pct'] >= target])
            for target in self.targets
        }

        summary = f"Summary of {total_days} trading days:\n"
        summary += "-" * 50 + "\n"
        summary += f"{'Target':>10} | {'Days Reached':>12} | {'Percentage':>10}\n"
        summary += "-" * 50 + "\n"
        for target, days in days_reached_targets.items():
            percentage = (days / total_days) * 100 if total_days > 0 else 0
            summary += f"{target:>10}% | {days:>12} | {percentage:>9.1f}%\n"
        summary += "-" * 50

        return summary


def run_daily_tracking():
    tracker = AutomatedAMDTracker()
    try:
        result = tracker.update_tracking()
        logging.info(result)
        logging.info("\n" + tracker.get_summary())
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


# Run the daily tracking
if __name__ == "__main__":
    run_daily_tracking()
