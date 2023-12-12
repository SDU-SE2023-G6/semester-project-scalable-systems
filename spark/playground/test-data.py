import random
import time
import csv

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

# Generate data and write it to a CSV file
with open('data.csv', 'w', newline='') as csvfile:
    fieldnames = ["id", "user", "timestamp", "likes", "text"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
    #writer.writeheader()

    for _ in range(num_records):
        id, user, likes, text = generate_random_data()
        timestamp = generate_timestamp()
        writer.writerow({"id": id, "user": user, "timestamp": timestamp, "likes": likes, "text": text})

print(f"{num_records} records generated and saved to data.csv.")
