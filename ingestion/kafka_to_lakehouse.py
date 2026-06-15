import json
import os
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime

consumer = KafkaConsumer(
    "weather_data",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

BASE_PATH = "lakehouse/weather/"

def write_to_lake(record):

    event_time = record["event_time"]
    date = event_time.split("T")[0]

    year, month, day = date.split("-")

    folder = f"{BASE_PATH}year={year}/month={month}/day={day}/"
    os.makedirs(folder, exist_ok=True)

    df = pd.DataFrame([record])

    file_name = f"{folder}weather_{datetime.now().timestamp()}.parquet"

    df.to_parquet(file_name, index=False)

    print("Saved:", file_name)

print("🚀 Kafka → Lakehouse Consumer Started")

for message in consumer:
    record = message.value
    write_to_lake(record)