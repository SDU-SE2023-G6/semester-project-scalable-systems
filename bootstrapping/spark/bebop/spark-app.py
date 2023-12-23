import sys

print("Python Version:", sys.version)

from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp, lit, expr, from_json, col, udf, avg, unix_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType, FloatType
from textblob import TextBlob

spark = SparkSession.builder.appName("PySparkBtcTweet").getOrCreate()


kafka_address = "strimzi-kafka-bootstrap.kafka:9092"
checkpoint_sentiment = "s3a://spark-data/cp_sentiment"
print("Kafka address: " + kafka_address)
print("Sentiment checkpoint: " + checkpoint_sentiment)

spark.sparkContext.setLogLevel("WARN")


df_tweet = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_address) \
  .option("subscribe", "TWEET_INGESTION") \
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


payload_schema = StructType([
    StructField("payload", StringType(), True)
])


def parseDataSource(datasource, schema):
    return datasource \
        .select(from_json(col("value").cast("string"), payload_schema).alias("value")) \
        .select(from_json(col("value.payload").cast("string"), schema).alias("value")) \
        .select("value.*")



def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity
sentiment_analysis_udf = udf(sentiment_analysis, StructType([
    StructField("sentiment_polarity", FloatType(), True),
    StructField("sentiment_subjectivity", FloatType(), True)
]))


def addSentimentColumn(datasource):
    return datasource \
        .withColumn("sentiment", sentiment_analysis_udf("text")) \
        .select("*", "sentiment.*") \
        .drop("sentiment")

def replaceTimestampWithUnix(datasource):
    return datasource.withColumn("timestamp", unix_timestamp("timestamp"))


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

pds_tweet = replaceTimestampWithUnix(pds_tweet)

# Add sentiment column to tweets
pds_tweet = addSentimentColumn(pds_tweet)

# Print schema for debugging
pds_tweet.printSchema()

# Start streaming queries
ws_sentiment = startWriteKafkaStream(pds_tweet, "TWEET_SENTIMENT", "append", checkpoint_sentiment)

ws_sentiment.awaitTermination()

