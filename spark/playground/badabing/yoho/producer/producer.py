from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers='localhost:9092')

for i in range(10):
    message = f"Message {i}"
    producer.send('test', value=message.encode('utf-8'))
    time.sleep(1)

producer.close()
