from kafka import KafkaProducer
import logging
logging.basicConfig(level=logging.INFO)

producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('INGESTION', b'Message from PyCharm')
producer.send('INGESTION', key=b'message-two', value=b'This is Kafka-Python')
producer.flush()

