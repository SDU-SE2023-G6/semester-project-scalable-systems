from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp, lit, expr, from_json, col, udf, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType


spark = SparkSession.builder.appName("PySparkBtcTweet").getOrCreate()

spark_conf = spark.sparkContext.getConf().getAll()

kafka_address = "kafka:9093"
if "kafkaAddress" in spark_conf:
    kafka_address = spark_conf["kafkaAddress"]
checkpoint_btc_agg = "/opt/bitnami/spark/checkpoints/agg/btc"
if "checkpointBtcAgg" in spark_conf:
    checkpoint_btc_agg = spark_conf["checkpointBtcAgg"]
checkpoint_tweet_agg = "/opt/bitnami/spark/checkpoints/agg/tweet"
if "checkpointTweetAgg" in spark_conf:
    checkpoint_tweet_agg = spark_conf["checkpointTweetAgg"]
checkpoint_sentiment = "/opt/bitnami/spark/checkpoints/sentiment"
if "checkpointSentiment" in spark_conf:
    checkpoint_sentiment = spark_conf["checkpointSentiment"]

# above didnt work xd
kafka_address = "strimzi-kafka-bootstrap.kafka:9092"
checkpoint_sentiment = "s3a://spark-data/cp_sentiment"
checkpoint_tweet_agg = "s3a://spark-data/cp_agg_tweet"
checkpoint_btc_agg = "s3a://spark-data/cp_agg_btc"


print("Kafka address: " + kafka_address)
print("BTC checkpoint: " + checkpoint_btc_agg)
print("Tweet checkpoint: " + checkpoint_tweet_agg)
print("Sentiment checkpoint: " + checkpoint_sentiment)

spark.sparkContext.setLogLevel("WARN")


df_tweet = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_address) \
  .option("subscribe", "TWEET_INGESTION") \
  .option("startingOffsets", "earliest")\
  .load()

df_btc = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_address) \
  .option("subscribe", "BITCOIN_INGESTION") \
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
    StructField("timestamp", TimestampType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume_btc", DoubleType(), True),
    StructField("volume_currency", DoubleType(), True),
    StructField("weighted_price", DoubleType(), True)
])

payload_schema = StructType([
    StructField("payload", StringType(), True)
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
    return datasource\
        .select(from_json(col("value").cast("string"), payload_schema).alias("value"))\
        .select(from_json(col("value.payload").cast("string"), schema).alias("value"))\
        .select("value.*")

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
        .withWatermark("timestamp", "4 hours") \
        .groupBy(window("timestamp", "5 minutes", "5 minutes")) \
        .agg(avg("open").alias("avg_open"),
             avg("high").alias("avg_high"),
             avg("low").alias("avg_low"),
             avg("close").alias("avg_close"),
             avg("volume_btc").alias("avg_volume_btc"),
             avg("volume_currency").alias("avg_volume_currency"),
             avg("weighted_price").alias("avg_weighted_price"),
             count("*").alias("total_records")) \
        .limit(14400)


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
        .option("kafka.bootstrap.servers", kafka_address) \
        .option("topic", topic) \
        .option("checkpointLocation", checkpointLocation) \
        .start()


# Parse data sources
pds_tweet = parseDataSource(df_tweet, tweet_schema)
pds_btc = parseDataSource(df_btc, btc_schema)


# Add sentiment column to tweets
pds_tweet = addSentimentColumn(pds_tweet)

# Aggregate tweets and Bitcoin data
agg_tweet = aggregateTweets(pds_tweet)
agg_btc = aggregateBtc(pds_btc)

# Print schema for debugging
pds_tweet.printSchema()
agg_tweet.printSchema()
agg_btc.printSchema()

# Start streaming queries
ws_sentiment = startWriteKafkaStream(pds_tweet, "TWEET_SENTIMENT", "append", checkpoint_sentiment)
ws_agg_tweet = startWriteKafkaStream(agg_tweet, "TWEET_AGGREGATE", "complete", checkpoint_tweet_agg)
ws_agg_btc = startWriteKafkaStream(agg_btc, "BITCOIN_AGGREGATE", "complete", checkpoint_btc_agg)

ws_sentiment.awaitTermination()
ws_agg_tweet.awaitTermination()
ws_agg_btc.awaitTermination()

