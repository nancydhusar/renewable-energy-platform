import json
import time
from kafka import KafkaProducer
from weather_extractor import fetch_weather

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

while True:

    weather_record = fetch_weather()

    producer.send(
        "weather_data",
        value=weather_record
    )

    producer.flush()

    print("Sent:", weather_record)

    time.sleep(30)