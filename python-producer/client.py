from kafka import KafkaProducer, KafkaConsumer
import json

KAFKA_BROKERS: str = "localhost:9092" # Require port-forwarding
TWEET_TOPIC: str = "TWEET_INGESTION"
BITCOIN_TOPIC: str = "BITCOIN_INGESTION"
DEFAULT_ENCODING: str = "utf-8"
DEFAULT_CONSUMER: str = "DEFAULT_CONSUMER"


def get_producer() -> KafkaProducer:
    return KafkaProducer(bootstrap_servers=[KAFKA_BROKERS])

def send_msg(value, key: str, topic: str, producer: KafkaProducer) -> None:
    producer.send(
        topic=topic,
        # Added string convertion since it is a hard requirement for the kafka producer
        key=str(key).encode(DEFAULT_ENCODING),
        value=json.dumps(value).encode(DEFAULT_ENCODING),
    )
