from kafka import KafkaProducer
import random
import time

# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: str(v).encode('utf-8')  # Assuming your data is convertible to string
)

# Generate random data for id, user, likes, and text
def generate_random_data():
    id = random.randint(1, 1000)
    user = f"user_{random.randint(1, 100)}"
    likes = random.randint(0, 100)
    text = f"Lorem ipsum text {random.randint(1, 1000)}"
    return id, user, likes, text

# Generate timestamps within the last 5 minutes
def generate_timestamp():
    current_time = int(time.time())
    five_minutes_ago = current_time - 300*20  # 300 seconds = 5 minutes
    return random.randint(five_minutes_ago, current_time)

# Define the number of records you want to generate
num_records = 20000

# Kafka topic to publish to
kafka_topic = 'test'

# Generate CSV data and publish it to Kafka
for _ in range(num_records):
    id, user, likes, text = generate_random_data()
    timestamp = generate_timestamp()
    
    # Construct a message using your data fields
    #message = {
    #    "id": id,
    #    "user": user,
    #    "timestamp": timestamp,
    #    "likes": likes,
    #    "text": text
    #}
    message = f"{id};{user};{timestamp};{likes};{text}"
    
    # Publish the message to Kafka
    producer.send(kafka_topic, value=message)
    
    # Sleep for a short duration to simulate real-time generation
    time.sleep(0.1)

print(f"{num_records} records generated and published to Kafka topic '{kafka_topic}'.")

# Close the Kafka producer
producer.close()
