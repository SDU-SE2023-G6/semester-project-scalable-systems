from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp

# Initialize Spark session
spark = SparkSession.builder \
    .appName("TweetAnalysis") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .config("spark.sql.streaming.minBatchesToRetain", 2) \
    .getOrCreate()

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

# Create windows for analysis
windowed_tweets = tweets \
    .withWatermark("timestamp", "15 minutes") \
    .groupBy(window("timestamp", "5 minutes", "5 minutes")) \
    .agg(sum("likes").alias("total_likes"), count("id").alias("total_tweets"))

# Display the results with expanded window column in the console
query = windowed_tweets.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
