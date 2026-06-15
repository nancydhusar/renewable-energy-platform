import requests
import pandas as pd
import os

# -----------------------------
# GERMANY CITIES CONFIG
# -----------------------------
CITIES = [
    {"city": "Berlin", "lat": 52.52, "lon": 13.41},
    {"city": "Hamburg", "lat": 53.55, "lon": 10.00},
    {"city": "Munich", "lat": 48.13, "lon": 11.58},
    {"city": "Cologne", "lat": 50.94, "lon": 6.96},
    {"city": "Frankfurt", "lat": 50.11, "lon": 8.68}
]

START_DATE = "2026-03-01"
END_DATE = "2026-05-31"

all_dfs = []

# -----------------------------
# FETCH DATA FOR EACH CITY
# -----------------------------
for c in CITIES:
    print(f"Fetching data for {c['city']}...")

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={c['lat']}"
        f"&longitude={c['lon']}"
        f"&start_date={START_DATE}"
        f"&end_date={END_DATE}"
        "&hourly="
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "cloud_cover,"
        "surface_pressure,"
        "wind_speed_10m,"
        "wind_direction_10m"
    )

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    hourly = data["hourly"]

    df = pd.DataFrame({
        "event_time": hourly["time"],
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "precipitation": hourly["precipitation"],
        "cloud_cover": hourly["cloud_cover"],
        "surface_pressure": hourly["surface_pressure"],
        "windspeed": hourly["wind_speed_10m"],
        "winddirection": hourly["wind_direction_10m"],
    })

    df["lat"] = c["lat"]
    df["lon"] = c["lon"]

    df["city"] = c["city"]

    all_dfs.append(df)

# -----------------------------
# COMBINE ALL CITIES
# -----------------------------
df = pd.concat(all_dfs, ignore_index=True)

# -----------------------------
# CLEANING
# -----------------------------
df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")

# -----------------------------
# OUTPUT INFO
# -----------------------------
print("\n Rows per city:")
print(df["city"].value_counts())

print(f"\nTotal rows fetched: {len(df)}")
print(df.head())

# -----------------------------
# SAVE DATASET
# -----------------------------
os.makedirs("lakehouse/weather_historical", exist_ok=True)

output_file = "lakehouse/weather_historical/germany_weather_history.parquet"

df.to_parquet(output_file, index=False)

print(f"\nSaved file: {output_file}")