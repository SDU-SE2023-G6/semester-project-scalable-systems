from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp, lit, expr, from_json, col, udf, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType

spark = SparkSession.builder \
    .appName("KafkaSparkApp") \
    .config("spark.jars", "/opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.2.0.jar," \
                          "/opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.2.0.jar," \
                          "/opt/bitnami/spark/jars/kafka-clients-3.2.0.jar," \
                          "/opt/bitnami/spark/jars/commons-pool2-2.8.0.jar," \
                          "/opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.2.0.jar,") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


df_tweet = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafka:9093") \
  .option("subscribe", "TWEET_INGESTION") \
  .option("startingOffsets", "earliest")\
  .load()

df_btc = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafka:9093") \
  .option("subscribe", "BTC_INGESTION") \
  .option("startingOffsets", "earliest")\
  .load()


# Define the schema for the JSON data
tweet_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("user", StringType(), True),
    StructField("fullname", StringType(), True),
    StructField("url", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("replies", IntegerType(), True),
    StructField("likes", IntegerType(), True),
    StructField("retweets", IntegerType(), True),
    StructField("text", StringType(), True)
])

# Define the schema for Bitcoin data
btc_schema = StructType([
    StructField("Timestamp", TimestampType(), True),
    StructField("Open", DoubleType(), True),
    StructField("High", DoubleType(), True),
    StructField("Low", DoubleType(), True),
    StructField("Close", DoubleType(), True),
    StructField("Volume_(BTC)", DoubleType(), True),
    StructField("Volume_(Currency)", DoubleType(), True),
    StructField("Weighted_Price", DoubleType(), True)
])

def sentiment_analysis(text):
    ## Create a TextBlob object
    #blob = TextBlob(text)
    #
    ## Get the sentiment polarity (-1 to 1, where -1 is negative, 0 is neutral, and 1 is positive)
    #sentiment_polarity = blob.sentiment.polarity
    #
    ## Classify the sentiment
    #if sentiment_polarity > 0:
    #    sentiment = 'positive'
    #elif sentiment_polarity < 0:
    #    sentiment = 'negative'
    #else:
    #    sentiment = 'neutral'
    #
    #return sentiment    
    return 69
sentiment_analysis_udf = udf(sentiment_analysis, IntegerType())

def parseDataSource(datasource, schema):
    return datasource.select(from_json(col("value").cast("string"), schema).alias("value"))

def explodeDataSource(datasource):
    return datasource.selectExpr("value.*")

def addSentimentColumn(datasource):
    return datasource.withColumn("sentiment", sentiment_analysis_udf("text"))

# Create windows for analysis with 5-minute buckets, keeps last 48 hours of aggregates.
def aggregateTweets(parsedDataSource):
    return parsedDataSource \
        .withWatermark("timestamp", "4 hours") \
        .groupBy(window("timestamp", "5 minutes", "5 minutes")) \
        .agg(sum("likes").alias("total_likes"), avg("sentiment").alias("sentiment"), count("*").alias("total_tweets")) \
        .limit(14400)    
   
# Create windows for analysis with 5-minute buckets, keeps last 48 hours of aggregates.
def aggregateBtc(parsedDataSource):
    return parsedDataSource \
        .withWatermark("Timestamp", "4 hours") \
        .groupBy(window("Timestamp", "5 minutes", "5 minutes")) \
        .agg(avg("Open").alias("average_open"),
             avg("High").alias("average_high"),
             avg("Low").alias("average_low"),
             avg("Close").alias("average_close"),
             avg("Volume_(BTC)").alias("average_volume_btc"),
             avg("Volume_(Currency)").alias("average_volume_currency"),
             avg("Weighted_Price").alias("average_weighted_price"),
             count("*").alias("total_records")) \
        .limit(14400)


def aggregateWindow(parsedDataSource, timeKey):
    return parsedDataSource \
        .withWatermark(timeKey, "4 hours") \
        .groupBy(window(timeKey, "5 minutes", "5 minutes"))
   


# Debug output to console
def startWriteStreamQuery(stream, outputMode="complete"):
    return stream.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 100) \
        .start()

# Write aggregated metrics to Kafka stream as JSON
def startWriteKafkaStream(stream, topic, outputMode, checkpointLocation):
    return stream \
        .selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .outputMode(outputMode) \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9093") \
        .option("topic", topic) \
        .option("checkpointLocation", checkpointLocation) \
        .start()


# Parse and explode data sources
pds_tweet = parseDataSource(df_tweet, tweet_schema)
pds_btc = parseDataSource(df_btc, btc_schema)
pds_tweet = explodeDataSource(pds_tweet)
pds_btc = explodeDataSource(pds_btc)


# Add sentiment column to tweets
pds_tweet = addSentimentColumn(pds_tweet)

# Aggregate tweets and Bitcoin data
agg_tweet = aggregateTweets(pds_tweet)
agg_btc = aggregateBtc(pds_btc)


# Start streaming queries
ws_sentiment = startWriteKafkaStream(pds_tweet, "TWEET_SENTIMENT", "append", "/opt/bitnami/spark/checkpoints/sentiment")
ws_agg_tweet = startWriteKafkaStream(agg_tweet, "TWEET_AGG", "complete", "/opt/bitnami/spark/checkpoints/agg/tweet")
ws_agg_btc = startWriteKafkaStream(agg_btc, "BTC_AGG", "complete", "/opt/bitnami/spark/checkpoints/agg/btc")

ws_sentiment.awaitTermination()
ws_agg_tweet.awaitTermination()
ws_agg_btc.awaitTermination()

