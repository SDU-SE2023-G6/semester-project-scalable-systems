# Spark - Kafka Prime Example

Information on how to run example. Ensure you have `python` and `kafka-python` installed.

1. Start services: `docker compose up d`
2. Start Kafka producer: `python producer/producer.py`
3. Start Spark Stream: `docker exec -it prime_spark /opt/bitnami/spark/bin/spark-submit /opt/bitnami/spark/work/app.py`
4. See what Spark sends to Kafka: `docker exec -it prime_kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic aggregated_metrics_topic --from-beginning`

