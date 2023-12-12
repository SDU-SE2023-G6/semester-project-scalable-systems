import threading
from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp, lit, expr

# Initialize Spark session
spark = SparkSession.builder.appName("TweetAnalysis").getOrCreate()

# Create a DataFrame representing the Netcat data source
lines = spark.readStream.format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# Parse the CSV data and select required columns, converting the timestamp
tweets = lines.selectExpr("split(value, ';') as data") \
    .selectExpr("cast(data[0] as int) as id", "data[1] as user",
                "to_timestamp(from_unixtime(data[2]), 'yyyy-MM-dd HH:mm:ss') as timestamp",
                "cast(data[3] as int) as likes", "data[4] as text")

# Define a rolling window expression for 5 minutes
rolling_window_5min = expr("window(timestamp, '5 minutes', '5 minutes')")

# Define a rolling window expression for 30 minutes
rolling_window_30min = expr("window(timestamp, '30 minutes', '30 minutes')")

# Define a rolling window expression for 1 hour
rolling_window_1hour = expr("window(timestamp, '1 hour', '1 hour')")

# Create windows for analysis with rolling boundaries
windowed_tweets_5min = tweets \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(rolling_window_5min) \
    .agg(sum("likes").alias("total_likes"), count("*").alias("total_tweets")) \
    .withColumn("bucket", lit("5 minutes"))

windowed_tweets_30min = tweets \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(rolling_window_30min) \
    .agg(sum("likes").alias("total_likes"), count("*").alias("total_tweets")) \
    .withColumn("bucket", lit("30 minutes"))

windowed_tweets_1hour = tweets \
    .withWatermark("timestamp", "2 hours") \
    .groupBy(rolling_window_1hour) \
    .agg(sum("likes").alias("total_likes"), count("*").alias("total_tweets")) \
    .withColumn("bucket", lit("1 hour"))

# Union the results from different time windows
windowed_tweets = windowed_tweets_5min.union(windowed_tweets_30min).union(windowed_tweets_1hour)

# Filter out older windows to keep only the latest two windows
latest_windowed_tweets = windowed_tweets.dropDuplicates(["bucket"]).sort("window").limit(2)

# Create a query for the combined result with "update" output mode and top 100 rows
query = latest_windowed_tweets.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .option("numRows", 100) \
    .start()

# Wait for the stream to end
query.awaitTermination()
