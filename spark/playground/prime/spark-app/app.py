from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum, count, to_timestamp, lit, expr

spark = SparkSession.builder \
    .appName("KafkaSparkApp") \
    .config("spark.jars", "/opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.2.0.jar," \
                          "/opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.2.0.jar," \
                          "/opt/bitnami/spark/jars/kafka-clients-3.2.0.jar," \
                          "/opt/bitnami/spark/jars/commons-pool2-2.8.0.jar," \
                          "/opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.2.0.jar,") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafka:9093") \
  .option("subscribe", "test") \
  .load()


# Parse the CSV data and select required columns, converting the timestamp
def parseDataSource(datasource):
    return datasource.selectExpr("split(value, ';') as data") \
        .selectExpr("cast(data[0] as int) as id", "data[1] as user",
                    "to_timestamp(from_unixtime(data[2]), 'yyyy-MM-dd HH:mm:ss') as timestamp",
                    "cast(data[3] as int) as likes", "data[4] as text")

# Create windows for analysis with 5-minute buckets, keeps last 48 hours of aggregates.
def aggregateWindow(parsedDataSource):
    return parsedDataSource \
        .withWatermark("timestamp", "4 hours") \
        .groupBy(window("timestamp", "5 minutes", "5 minutes")) \
        .agg(sum("likes").alias("total_likes"), count("*").alias("total_tweets")) \
        .limit(14400)       


# Debug output to console, replace with Kafka/Other stream output
def startWriteStreamQuery(stream):
    return aggregatedMetricsWindow.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 100) \
        .start()


parsedDataSource = parseDataSource(df)
aggregatedMetricsWindow = aggregateWindow(parsedDataSource)

startWriteStreamQuery(aggregatedMetricsWindow).awaitTermination()
