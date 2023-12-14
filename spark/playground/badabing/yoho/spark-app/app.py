from pyspark.sql import SparkSession

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



df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
  .writeStream \
  .outputMode("append") \
  .format("console") \
  .start() \
  .awaitTermination()
