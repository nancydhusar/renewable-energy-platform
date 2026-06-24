import requests
import pandas as pd
import os
from datetime import datetime

# German cities with coordinates
CITIES = {
    "Berlin": (52.52, 13.41),
    "Hamburg": (53.55, 10.00),
    "Munich": (48.13, 11.58),
    "Cologne": (50.94, 6.96),
    "Frankfurt": (50.11, 8.68)
}

all_weather = []

for city, (lat, lon) in CITIES.items():

    print(f"Fetching live weather for {city}...")

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "wind_speed_10m,"
        "wind_direction_10m,"
        "cloud_cover,"
        "surface_pressure"
    )

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()["current"]

    row = {
        "city": city,
        "event_time": data["time"],
        "temperature": data["temperature_2m"],
        "humidity": data["relative_humidity_2m"],
        "windspeed": data["wind_speed_10m"],
        "winddirection": data["wind_direction_10m"],
        "cloud_cover": data["cloud_cover"],
        "surface_pressure": data["surface_pressure"],
        "lat": lat,
        "lon": lon,
        "ingestion_time": datetime.utcnow()
    }

    all_weather.append(row)

# Create dataframe
df = pd.DataFrame(all_weather)

# Convert timestamp
df["event_time"] = pd.to_datetime(df["event_time"])

print("\nLive Weather Data")
print(df.head())

# Create folder if not exists
os.makedirs("lakehouse/live", exist_ok=True)

# Save parquet
output_file = "lakehouse/live/live_weather.parquet"

df.to_parquet(output_file, index=False)

print(f"\nSaved file: {output_file}")

# Create folder if not exists
live_parquet_path = "lakehouse/live/live_weather.parquet"
os.makedirs("lakehouse/live_raw", exist_ok=True)

raw_csv_path = "lakehouse/live_raw/live_weather.csv"
df.to_csv(raw_csv_path, index=False)

print(f"Raw CSV saved at: {raw_csv_path}")