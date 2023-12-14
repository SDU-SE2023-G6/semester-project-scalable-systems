import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Create the Twitter data as a DataFrame
twitter_data = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'user': ['user1', 'user2', 'user3', 'user4', 'user5'],
    'fullname': ['John Doe', 'Jane Smith', 'Robert Brown', 'Sarah White', 'Michael Lee'],
    'url': ['example1.com', 'example2.com', 'example3.com', 'example4.com', 'example5.com'],
    'timestamp': [1382397600, 1382401200, 1382404800, 1382408400, 1382412000],
    'replies': [5, 8, 3, 6, 4],
    'likes': [20, 15, 30, 25, 18],
    'retweets': [10, 5, 12, 8, 7],
    'text': ['Sample text', 'Another text', 'More text', 'New text', 'Last text']
})

# Create the Bitcoin price data as a DataFrame
bitcoin_data = pd.DataFrame({
    'Timestamp': [1325317920, 1325321520, 1325325120, 1325328720, 1325332320],
    'Open': [4.39, 4.40, 4.41, 4.42, 4.44],
    'High': [4.39, 4.42, 4.43, 4.45, 4.48],
    'Low': [4.39, 4.37, 4.38, 4.41, 4.42],
    'Close': [4.39, 4.41, 4.42, 4.44, 4.47],
    'Volume_(BTC)': [0.45558087, 0.21000000, 0.21200000, 0.28900000, 0.40100000],
    'Volume_(Currency)': [2.0000000193, 0.8976000000, 0.9332600000, 1.2856800000, 1.7832000000],
    'Weighted_Price': [4.39, 4.40, 4.41, 4.42, 4.45]
})

# Calculate correlations within each dataset
twitter_correlation = twitter_data.corr()
bitcoin_correlation = bitcoin_data.corr()

# Calculate correlation between timestamp and likes in both datasets
timestamp_likes_correlation = pd.concat([twitter_data['timestamp'], twitter_data['likes'], bitcoin_data['Timestamp'], bitcoin_data['Close']], axis=1).corr()

# Visualize correlations
plt.figure(figsize=(12, 5))
plt.subplot(131)
sns.heatmap(twitter_correlation, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Twitter Data Correlation Matrix')

plt.subplot(132)
sns.heatmap(bitcoin_correlation, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Bitcoin Price Data Correlation Matrix')

plt.subplot(133)
sns.heatmap(timestamp_likes_correlation, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Between Timestamp and Likes')
plt.tight_layout()

plt.show()
