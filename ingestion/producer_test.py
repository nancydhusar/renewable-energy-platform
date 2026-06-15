import kafka
from kafka import KafkaProducer
import requests
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

LAT = 52.52
LON = 13.41

def fetch_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
    response = requests.get(url)
    data = response.json()["current_weather"]
    
    return {
        "city": "Berlin",
        "temperature": data["temperature"],
        "windspeed": data["windspeed"],
        "winddirection": data["winddirection"],
        "timestamp": data["time"]
    }

while True:
    message = fetch_weather()
    producer.send("weather_data", value=message)

    print("Sent:", message)
    time.sleep(5)