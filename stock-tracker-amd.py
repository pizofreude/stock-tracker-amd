import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz

class AutomatedAMDTracker:
    def __init__(self, targets=[1.2, 1.5, 2.2]):
        self.targets = sorted(targets)
        self.symbol = "AMD"
        try:
            self.df = pd.read_csv('amd_stock_tracking.csv')
            print("Loaded existing tracking data")
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['date', 'starting_price', 'ending_price',
                                           'daily_change_pct', 'targets_reached'])
            print("Created new tracking dataframe")

    def is_market_open(self):
        """
        Handling Market Hours: Check if the market is currently open
        """
        et_tz = pytz.timezone('US/Eastern')
        now = datetime.now(et_tz)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False
        
        # Check if it's between 9:30 AM and 4:00 PM ET
        market_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_start <= now <= market_end


    def fetch_daily_data(self):
        # Get today's date
        today = datetime.now()

        # Check if the market is open
        if not self.is_market_open():
            print("Market is currently closed. Fetching most recent available data.")
            
            # Start looking for data from yesterday
            look_back_date = today - timedelta(days=1)
            
            # Keep looking back until we find data (max 10 days to avoid infinite loop)
            for _ in range(10):
                # Format the date as a string
                date_str = look_back_date.strftime('%Y-%m-%d')
                
                # Try to fetch data for this date
                stock = yf.Ticker(self.symbol)
                history = stock.history(start=date_str, end=date_str)
                
                # If we found data, return it
                if not history.empty:
                    print(f"Found data for {date_str}")
                    return history, None
                
                # If no data, look one day further back
                look_back_date -= timedelta(days=1)
            
            # If we didn't find any data after 10 days, return an error
            return None, "No data available for the past 10 days"

        else:
            # Market is open, fetch today's data
            today_str = today.strftime('%Y-%m-%d')
            stock = yf.Ticker(self.symbol)
            history = stock.history(start=today_str, end=today_str)

            if history.empty:
                return None, "No data available for today"

            return history, None


    def update_tracking(self):
        history, error = self.fetch_daily_data()

        if error:
            print(f"Error fetching data: {error}")
            return error

        # if len(history) == 0:
        #     print("No new data to process")
        #     return "No new data to process"
        if history is None or len(history) == 0:
            print("No new data to process")
            return "No new data to process"


        latest_data = history.iloc[-1]
        date = latest_data.name.strftime('%Y-%m-%d')

        # Check if we already have data for this date
        if date in self.df['date'].values:
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
        if len(self.df) == 0:
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
        print(result)
        print("\n" + tracker.get_summary())
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the daily tracking
if __name__ == "__main__":
    run_daily_tracking()