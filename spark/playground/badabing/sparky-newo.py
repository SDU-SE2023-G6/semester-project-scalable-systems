import threading
from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp, lit, expr

# Initialize Spark session
spark = SparkSession.builder.appName("TweetAnalysis") \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1') \
    .getOrCreate()


def createNetCatDataSource():
    # Create a DataFrame representing the Netcat data source
    # How to use kafka instead https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
    return spark.readStream.format("socket") \
        .option("host", "localhost") \
        .option("port", 9999) \
        .load()

def createKafkaDataSource(hosts, topic):
    return spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", hosts) \
    .option("subscribe", topic) \
    .load()


def parseDataSource(datasource):
    # Parse the CSV data and select required columns, converting the timestamp
    return datasource.selectExpr("split(value, ';') as data") \
        .selectExpr("cast(data[0] as int) as id", "data[1] as user",
                    "to_timestamp(from_unixtime(data[2]), 'yyyy-MM-dd HH:mm:ss') as timestamp",
                    "cast(data[3] as int) as likes", "data[4] as text")

def aggregateWindow(parsedDataSource):
    # Create windows for analysis with 5-minute buckets, keeps last 48 hours of aggs.
    return parsedDataSource \
        .withWatermark("timestamp", "4 hours") \
        .groupBy(window("timestamp", "5 minutes", "5 minutes")) \
        .agg(sum("likes").alias("total_likes"), count("*").alias("total_tweets")) \
        .limit(14400)       



def startWriteKafkaStreamQuery(stream, hosts, topic):
    # Write key-value data from a DataFrame to a specific Kafka topic specified in an option
    return stream \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", hosts) \
        .option("topic", topic) \
        .start()    



def startWriteStreamQuery(stream):
    return aggregatedMetricsWindow.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 100) \
        .start()



hosts = "localhost:22181"

rawDataSource = createKafkaDataSource(hosts, "kin")
parsedDataSource = parseDataSource(rawDataSource)
aggregatedMetricsWindow = aggregateWindow(parsedDataSource)

# Debug log
#query = consoleWriteStreamQuery(aggregatedMetricsWindow)

# Kafka
query = startWriteKafkaStreamQuery(aggregatedMetricsWindow, hosts, "kout")

# Wait for the stream to end
query.awaitTermination()
