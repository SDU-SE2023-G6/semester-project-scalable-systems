import threading
from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp

# Initialize Spark session
spark = SparkSession.builder.appName("TweetAnalysis").getOrCreate()

# Define the schema for the CSV data
# (Assuming you have already defined StructType and other necessary imports)

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

# Create sliding windows for analysis with 5-minute, 30-minute, and 1-hour buckets
windowed_tweets_5min = tweets \
    .withWatermark("timestamp", "5 minutes") \
    .groupBy(window("timestamp", "5 minutes", "5 minutes")) \
    .agg(sum("likes").alias("total_likes_5min"), count("id").alias("total_tweets_5min"))

windowed_tweets_30min = tweets \
    .withWatermark("timestamp", "30 minutes") \
    .groupBy(window("timestamp", "30 minutes", "5 minutes")) \
    .agg(sum("likes").alias("total_likes_30min"), count("id").alias("total_tweets_30min"))

windowed_tweets_1hour = tweets \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(window("timestamp", "1 hour", "5 minutes")) \
    .agg(sum("likes").alias("total_likes_1hour"), count("id").alias("total_tweets_1hour"))

# Create queries for each time bucket
query_5min = windowed_tweets_5min.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query_30min = windowed_tweets_30min.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query_1hour = windowed_tweets_1hour.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

# Wait for streams to end
spark.streams.awaitAnyTermination()
