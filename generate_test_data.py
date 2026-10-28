import pandas as pd
import datetime
import random

# Generate last 10 days of dates
dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(10)]
dates.reverse()

# Generate dummy prices around a hypothetical average (e.g., 1,000,000 UGX)
# Add some random fluctuation to make it look real
prices = [950000, 980000, 1200000, 1150000, 1000000, 950000, 920000, 1300000, 1250000, 990000]

data = {
    'Date': dates,
    'Price_UGX': prices
}

df = pd.DataFrame(data)
df.to_csv('test_price_history.csv', index=False)
print("Dummy data generated in test_price_history.csv")
print(df)