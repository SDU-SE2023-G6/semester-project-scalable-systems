import threading
import sys
import time
import queue
import csv
import os
from client import get_producer, TWEET_TOPIC, BITCOIN_TOPIC, send_msg
from data_model_btc import get_bitcoin_price_obj, BitcoinPackageObj, BitcoinPriceObj
from data_model_tweets import get_tweet_obj, TweetPackageObj, TweetObj
from kafka.errors import NoBrokersAvailable

BTC_FILE = os.getenv("BTC_FILE_PATH", "../data/btc.csv") # load file based on env variable or take default value
TWEETS_FILE = os.getenv("TWEETS_FILE_PATH", "../data/tweets.csv")

# Number of seconds from 2016-01-01 to 2019-03-29
total_seconds_dataset = 1.022e8

class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def seconds_to_readable(seconds):
    years, remainder = divmod(seconds, 31536000)
    months, remainder = divmod(remainder, 2592000)
    days, remainder = divmod(remainder, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if years: parts.append(f"{int(years)} years")
    if months: parts.append(f"{int(months)} months")
    if days: parts.append(f"{int(days)} days")
    if hours: parts.append(f"{int(hours)} hours")
    if minutes: parts.append(f"{int(minutes)} minutes")
    if seconds: parts.append(f"{round(seconds, 2)} seconds")
    
    if len(parts) > 1:
        return ", ".join(parts[:-1]) + " and " + parts[-1]
    else:
        return parts[0] if parts else "0 seconds"


def send_btc(btc: BitcoinPriceObj) -> None:
    producer = get_producer()
    po = BitcoinPackageObj(payload=btc)
    send_msg(key=btc.timestamp, value=po.to_dict(), topic=BITCOIN_TOPIC, producer=producer)

def send_tweet(tweet:TweetObj) -> None:
    producer = get_producer()
    po = TweetPackageObj(payload=tweet)
    send_msg(key=tweet.id, value=po.to_dict(), topic=TWEET_TOPIC, producer=producer)

def worker(taskQueue: queue.Queue) -> None:
    while True:
        task:tuple(str, BitcoinPriceObj|TweetObj) = taskQueue.get()
        if task is None:
            taskQueue.task_done()
            break   
        if task[0] == "btc":
            send_btc(task[1])
            pass
        elif task[0] == "tweet":
            send_tweet(task[1])
            pass
        taskQueue.task_done()

# Total target time for the ingestion of the full datasets
def total_target_time_in_seconds(velocity: float) -> float:
    return 3600 / velocity


# Number of seconds happening in emulated time for 1 second of real time
def get_time_multiplier(velocity: float) -> float:
    
    # Number of seconds in the target time
    target_seconds = total_target_time_in_seconds(velocity)

    return total_seconds_dataset / target_seconds

def get_next_btc_entry(csv) -> BitcoinPriceObj | None:
    try:
        row = next(csv)
        if(row[0] == "Timestamp" or row[1] == "NaN"):
            return get_next_btc_entry(csv)
        return get_bitcoin_price_obj(
            timestamp=int(time.mktime(time.strptime(row[0], "%Y-%m-%d %H:%M:%S"))),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume_btc=float(row[5]),
            volume_currency=float(row[6]),
            weighted_price=float(row[7])
        )
    except StopIteration:
        return None

def get_next_tweet_entry(csv) -> TweetObj | None:
    try:
        row = next(csv)
        if(row[0] == "id"):
            return get_next_tweet_entry(csv)
        return get_tweet_obj(
            id=int(float(row[0])),
            user=row[1],
            fullname=row[2],
            url=row[3],
            # Convert format "%Y-%m-%d %H:%M:%S" to timestamp
            timestamp=int(time.mktime(time.strptime(row[4], "%Y-%m-%d %H:%M:%S"))),
            replies=int(float(row[5])),
            likes=int(float(row[6])),
            retweets=int(float(row[7])),
            text=row[8],
        )
    except StopIteration:
        return None


def main():
    velocity = 1.0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        velocity = int(sys.argv[1])
    else:
        print ("No velocity specified, using default velocity of 1")

    print(f"Checking if the uinput files exists...")

    if not os.path.exists(BTC_FILE):
            print("BTC file not found")
            print(os.listdir("./"))
            print(os.listdir("./data"))
            return False
    print("BTC file found.")

    if not os.path.exists(TWEETS_FILE):
            print("TWEETS file not found")
            print(os.listdir("./"))
            return # Exit early because file doesnt exist
    print("TWEETS file found.")
    
    print(f"Will try to complete ingestion in {seconds_to_readable(total_target_time_in_seconds(velocity))}")

    print("Test that producer is working")
    try:
        get_producer();
    except NoBrokersAvailable as e:
        print(f"Failure: {e}")
        return


    numberOfWorkers = 10
    taskQueue = queue.Queue()
    workers = []

    for _ in range(numberOfWorkers):
        t = threading.Thread(target=worker, args=(taskQueue,))
        t.start()
        workers.append(t)

    timeMultiplier = get_time_multiplier(velocity)
    print(f"Time multiplier is {int(timeMultiplier)}")
    timeResolution = 4

    print("Loading btc.csv...", end="")
    try:
        btc_file = open(BTC_FILE, "r", encoding="utf-8-sig")
        btc_csv = csv.reader(btc_file, delimiter=",")
    except FileNotFoundError:
        print(" File not found.")
        exit(1)
    print(" Done.")
    print("Loading tweets.csv...", end="")
    try:
        tweet_file = open(TWEETS_FILE, "r", encoding="utf-8-sig")
        tweet_csv = csv.reader(tweet_file, delimiter=",")
    except FileNotFoundError:
        print(" File not found.")
        exit(1)
    print(" Done.")
    next(btc_csv)
    next(tweet_csv)
    tweet = get_next_tweet_entry(tweet_csv)
    btc = get_next_btc_entry(btc_csv)
    
    print("Starting emulation...")
    startTime = time.time()
    emulatedstartTime = btc.timestamp if btc.timestamp < tweet.timestamp else tweet.timestamp
    emulatedTime = emulatedstartTime
    totalTweetsSent = 0
    totalBtcSent = 0
    try:
        while btc is not None or tweet is not None:
            tweetsSent = 0
            btcSent = 0
            for _ in range(0, timeResolution):
                emulatedTime = emulatedstartTime + (timeMultiplier * (time.time() - startTime))
                while btc is not None and btc.timestamp <= emulatedTime:
                    taskQueue.put(("btc", btc))
                    btc = get_next_btc_entry(btc_csv)
                    totalBtcSent += 1
                while tweet is not None and tweet.timestamp <= emulatedTime:
                    taskQueue.put(("tweet", tweet))
                    tweet = get_next_tweet_entry(tweet_csv)
                    totalTweetsSent += 1
                time.sleep(1/timeResolution)
            print(f"Emulated time: {time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(emulatedTime))} | Sent: {totalBtcSent} btc data, {totalTweetsSent} tweets (Queue: {taskQueue.qsize()}) | Time remaining: {seconds_to_readable(total_target_time_in_seconds(velocity) - (time.time() - startTime))} ({(emulatedTime - emulatedstartTime) / total_seconds_dataset * 100:.2f}%)", end='\r')
    except KeyboardInterrupt:
        print("\n\nKeyboard interruption, stopping...")

    btc_file.close()
    tweet_file.close()
    print("Emulation finished, waiting for workers to finish...")
    for _ in range(numberOfWorkers):
        taskQueue.put(None)
    taskQueue.join()
    print("Workers finished.")
    print("Total time: {} ({:.2f}%)".format(seconds_to_readable(time.time() - startTime), (time.time() - startTime) / total_target_time_in_seconds(velocity) * 100))
    print("Total emulated time: {} ({:.2f}%)".format(seconds_to_readable(emulatedTime - emulatedstartTime), (emulatedTime - emulatedstartTime) / total_seconds_dataset * 100))

    print(f"Total messages sent: {totalBtcSent + totalTweetsSent} (BTC: {totalBtcSent}, Tweets: {totalTweetsSent})")

    exit(0)

if __name__ == "__main__":
    main()
