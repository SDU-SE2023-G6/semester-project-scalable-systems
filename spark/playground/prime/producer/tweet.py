from kafka import KafkaProducer
import random
import time
from datetime import datetime, timedelta


# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: str(v).encode('utf-8')  # Assuming your data is convertible to string
)

# Generate random data for id, user, likes, and text
def generate_random_data():
    id = str(random.randint(1, 1000))
    user = f"user_{random.randint(1, 100)}"
    fullname = f"Fullname {user}"
    url = "url"
    timestamp = generate_timestamp()
    replies = 0
    likes = random.randint(0, 100)
    retweets = 0
    text = f"Lorem ipsum text {random.randint(1, 1000)}"

    return {
        "id": id,
        "user": user,
        "fullname": fullname,
        "url": url,
        "timestamp": timestamp,
        "replies": replies,
        "likes": likes,
        "retweets": retweets,
        "text": text
    }
# Generate timestamps within the last 15 minutes
def generate_timestamp():
    current_time = datetime.utcnow()
    fifteen_minutes_ago = current_time - timedelta(minutes=15)
    random_timestamp = fifteen_minutes_ago + timedelta(seconds=random.randint(0, 900))  # 900 seconds = 15 minutes
    return random_timestamp.strftime("%Y-%m-%d %H:%M:%S+00")


# Define the number of records you want to generate
num_records = 20000

# Kafka topic to publish to
kafka_topic = 'TWEET_INGESTION'

# Generate JSON data and publish it to Kafka
for _ in range(num_records):
    message = generate_random_data()
    
    # Publish the message to Kafka
    producer.send(kafka_topic, value=message)
    
    # Sleep for a short duration to simulate real-time generation
    time.sleep(0.1)

print(f"{num_records} records generated and published to Kafka topic '{kafka_topic}'.")

# Close the Kafka producer
producer.close()
