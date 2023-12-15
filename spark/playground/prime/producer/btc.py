from kafka import KafkaProducer
import random
import time
from datetime import datetime, timedelta

# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: str(v).encode('utf-8')  # Assuming your data is convertible to string
)

# Generate random data for Bitcoin price
def generate_bitcoin_data():
    timestamp = generate_timestamp()
    open_price = round(random.uniform(4.0, 5.0), 2)
    high_price = round(open_price + random.uniform(0.1, 1.0), 2)
    low_price = round(open_price - random.uniform(0.1, 1.0), 2)
    close_price = round(random.uniform(low_price, high_price), 2)
    volume_btc = round(random.uniform(0.1, 1.0), 8)
    volume_currency = round(volume_btc * close_price, 10)
    weighted_price = round(random.uniform(open_price, close_price), 2)

    return {
        "Timestamp": timestamp,
        "Open": open_price,
        "High": high_price,
        "Low": low_price,
        "Close": close_price,
        "Volume_(BTC)": volume_btc,
        "Volume_(Currency)": volume_currency,
        "Weighted_Price": weighted_price
    }

# Generate timestamps within the last 15 minutes
def generate_timestamp():
    current_time = datetime.utcnow()
    fifteen_minutes_ago = current_time - timedelta(minutes=15)
    random_timestamp = fifteen_minutes_ago + timedelta(seconds=random.randint(0, 900))  # 900 seconds = 15 minutes
    return int(random_timestamp.timestamp())

# Define the number of records you want to generate
num_records = 20000

# Kafka topic to publish to
kafka_topic = 'BTC_INGESTION'

# Generate JSON data and publish it to Kafka
for _ in range(num_records):
    message = generate_bitcoin_data()
    
    # Publish the message to Kafka
    producer.send(kafka_topic, value=message)
    
    # Sleep for a short duration to simulate real-time generation
    time.sleep(0.1)

print(f"{num_records} records generated and published to Kafka topic '{kafka_topic}'.")

# Close the Kafka producer
producer.close()
