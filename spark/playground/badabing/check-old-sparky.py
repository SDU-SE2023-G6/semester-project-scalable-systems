from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, TimestampType

# Initialize Spark session
spark = SparkSession.builder.appName("TweetAnalysis").getOrCreate()

# Define the schema for the CSV data
tweet_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("user", StringType(), True),
    StructField("timestamp", LongType(), True),
    StructField("likes", IntegerType(), True),
    StructField("text", StringType(), True)
])

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
    .groupBy(window("timestamp", "5 minutes", "5 minutes"), "likes") \
    .agg(sum("likes").alias("total_likes"), count("id").alias("tweet_count"))

# Display the results with expanded window column in the console
query = windowed_tweets.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

    
query.awaitTermination()
