import threading
import sys
import time
from client import get_producer, TWEET_TOPIC, BITCOIN_TOPIC, send_msg
from data_model_btc import generate_btc_sample
from data_model_tweets import generate_tweet_sample


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def produce_msg() -> None:
    producer = get_producer()
    
    key, value = generate_btc_sample()
    send_msg(key=str(key), value=value, topic=BITCOIN_TOPIC, producer=producer)
    key, value = generate_tweet_sample()
    send_msg(key=str(key), value=value, topic=TWEET_TOPIC, producer=producer)

def main():
    velocity = 1
    pushPattern = False
    try: 
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            velocity = int(sys.argv[1])
        else:
            print ("No velocity specified, using default velocity of 1")
            print ("Usage: random-producer.py <velocity> -push")
        for arg in sys.argv:
            if arg == "-push":
                pushPattern = True
    except IndexError:
        print ("Usage: random-producer.py <velocity> -push")
        exit(1)
    # Veloctiy is the number of messages per second

    timers = []
    for _ in range(0, velocity):
        timers.append(RepeatTimer(1.0, produce_msg))

    try:
        for timer in timers:
            timer.start()
            if not pushPattern:
                time.sleep(1/velocity)
        while True:
            pass

    except KeyboardInterrupt:
        print("Exiting...")
        pass
    finally:
        for timer in timers:
            timer.cancel()


if __name__ == "__main__":
    main()