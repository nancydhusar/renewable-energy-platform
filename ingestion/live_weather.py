import requests
import pandas as pd
import os
from datetime import datetime

# German cities with coordinates
CITIES = CITIES = {
    "Berlin": (52.52, 13.41),
    "Hamburg": (53.55, 10.00),
    "Munich": (48.13, 11.58),
    "Cologne": (50.94, 6.96),
    "Frankfurt": (50.11, 8.68),

    "Stuttgart": (48.78, 9.18),
    "Düsseldorf": (51.23, 6.78),
    "Dortmund": (51.51, 7.46),
    "Essen": (51.46, 7.01),
    "Leipzig": (51.34, 12.37),

    "Bremen": (53.08, 8.80),
    "Dresden": (51.05, 13.74),
    "Hanover": (52.37, 9.73),
    "Nuremberg": (49.45, 11.08),
    "Mannheim": (49.49, 8.47),

    "Karlsruhe": (49.01, 8.40),
    "Wiesbaden": (50.08, 8.24),
    "Augsburg": (48.37, 10.90),
    "Bonn": (50.74, 7.10),
    "Münster": (51.96, 7.63)
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

if os.path.exists(output_file):
    old_df = pd.read_parquet(output_file)

    df = pd.concat([old_df, df])

    df = (
        df.sort_values("ingestion_time")
          .drop_duplicates(
              subset=["city", "event_time"],
              keep="last"
          )
    )

df.to_parquet(output_file, index=False)

print(f"\nSaved file: {output_file}")

# Create folder if not exists
live_parquet_path = "lakehouse/live/live_weather.parquet"
os.makedirs("lakehouse/live_raw", exist_ok=True)

raw_csv_path = "lakehouse/live_raw/live_weather.csv"
df.to_csv(raw_csv_path, index=False)

print(f"Raw CSV saved at: {raw_csv_path}")