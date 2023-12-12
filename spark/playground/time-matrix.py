import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns

# Generate timestamps for several days at 1-second intervals
start_date = '2023-10-22 00:00:00'
end_date = '2023-10-25 00:00:00'
time_interval = '1S'
timestamps = pd.date_range(start=start_date, end=end_date, freq=time_interval)

# Create a larger dataset for Bitcoin price data with unique timestamps
bitcoin_data = pd.DataFrame({
    'Timestamp': timestamps,
    'Open': np.random.uniform(4.35, 4.50, len(timestamps)),
    'High': np.random.uniform(4.35, 4.50, len(timestamps)),
    'Low': np.random.uniform(4.35, 4.50, len(timestamps)),
    'Close': np.random.uniform(4.35, 4.50, len(timestamps)),
    'Volume_(BTC)': np.random.uniform(0.1, 0.5, len(timestamps)),
    'Volume_(Currency)': np.random.uniform(0.5, 2.5, len(timestamps)),
    'Weighted_Price': np.random.uniform(4.35, 4.50, len(timestamps))
})

# Create a larger dataset for Twitter data with non-unique timestamps
twitter_data = pd.DataFrame({
    'id': range(1, len(timestamps) + 1),
    'user': ['user' + str(random.randint(1, 100)) for _ in range(len(timestamps))],
    'fullname': ['Fullname' + str(random.randint(1, 100)) for _ in range(len(timestamps))],
    'url': ['url' + str(random.randint(1, 100)) + '.com' for _ in range(len(timestamps))],
    'timestamp': timestamps,
    'replies': np.random.randint(1, 20, len(timestamps)),
    'likes': np.random.randint(10, 50, len(timestamps)),
    'retweets': np.random.randint(5, 25, len(timestamps)),
    'text': ['Sample text ' + str(random.randint(1, 100)) for _ in range(len(timestamps))]
})

# Combine Bitcoin and Twitter data
combined_data = pd.merge(bitcoin_data, twitter_data, left_on='Timestamp', right_on='timestamp', how='inner')

# Group data by timestamp into different timeframes (5 minutes, 1 hour, and daily)
timeframes = ['5Min', '1H', 'D']
twitter_data_resampled = {}
bitcoin_data_resampled = {}
combined_data_resampled = {}

for timeframe in timeframes:
    twitter_data_resampled[timeframe] = twitter_data.set_index('timestamp').resample(timeframe).mean()
    bitcoin_data_resampled[timeframe] = bitcoin_data.set_index('Timestamp').resample(timeframe).mean()
    combined_data_resampled[timeframe] = combined_data.set_index('Timestamp').resample(timeframe).mean()

# Calculate correlations for each timeframe
correlation_matrices = {}

for timeframe in timeframes:
    twitter_correlation = twitter_data_resampled[timeframe].corr()
    bitcoin_correlation = bitcoin_data_resampled[timeframe].corr()
    combined_correlation = combined_data_resampled[timeframe].corr()
    correlation_matrices[timeframe] = {
        'Twitter Data': twitter_correlation,
        'Bitcoin Data': bitcoin_correlation,
        'Bitcoin & Twitter Data': combined_correlation
    }

# Visualize correlation matrices for each timeframe
plt.figure(figsize=(18, 15))

for i, timeframe in enumerate(timeframes):
    for j, dataset in enumerate(['Twitter Data', 'Bitcoin Data', 'Bitcoin & Twitter Data']):
        plt.subplot(len(timeframes), len(timeframes), i * len(timeframes) + j + 1)
        sns.heatmap(correlation_matrices[timeframe][dataset], annot=True, cmap='coolwarm', linewidths=0.5)
        plt.title(f'{dataset} Correlation Matrix ({timeframe})')

plt.tight_layout()
plt.show()
