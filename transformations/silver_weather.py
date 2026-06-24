import duckdb
import pandas as pd
import os
import sys

# -----------------------------
# IMPORT PATH FIX
# -----------------------------
sys.path.append(os.path.abspath("."))

from quality_checks.validate_weather import validate_weather_data

# -----------------------------
# PATH
# -----------------------------
SILVER_PATH = "lakehouse/silver/weather/"
os.makedirs(SILVER_PATH, exist_ok=True)

# -----------------------------
# LOAD DATA (LIVE + HISTORICAL)
# -----------------------------
df = duckdb.query("""
    SELECT
        city,
        CAST(event_time AS TIMESTAMP) AS event_time,
        lat,
        lon,
        temperature,
        windspeed,
        winddirection,
        is_day,
        weathercode,
        humidity,
        cloud_cover,
        surface_pressure
    FROM read_parquet([
        'lakehouse/weather/**/*.parquet',
        'lakehouse/weather_historical/*.parquet',
        'lakehouse/live/live_weather.parquet'
    ], union_by_name=true)
""").df()

print("Raw records loaded:", len(df))

# -----------------------------
# STANDARD COLUMNS
# -----------------------------
COMMON_COLUMNS = [
    "city",
    "event_time",
    "lat",
    "lon",
    "temperature",
    "windspeed",
    "winddirection",
    "is_day",
    "weathercode",
    "humidity",
    "cloud_cover",
    "surface_pressure"
]

# -----------------------------
# ENSURE ALL COLUMNS EXIST
# -----------------------------
for col in COMMON_COLUMNS:
    if col not in df.columns:
        df[col] = None

df = df[COMMON_COLUMNS]

# -----------------------------
# SAFE TYPE CONVERSION
# -----------------------------
df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce", utc=True)

df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
df["windspeed"] = pd.to_numeric(df["windspeed"], errors="coerce")
df["winddirection"] = pd.to_numeric(df["winddirection"], errors="coerce")

# -----------------------------
# FILL OPTIONAL COLUMNS
# -----------------------------
df["is_day"] = df["is_day"].fillna(0)
df["weathercode"] = df["weathercode"].fillna(0)
df["humidity"] = df["humidity"].fillna(0)
df["cloud_cover"] = df["cloud_cover"].fillna(0)
df["surface_pressure"] = df["surface_pressure"].fillna(0)

df["lat"] = df["lat"].fillna(0)
df["lon"] = df["lon"].fillna(0)
df["winddirection"] = df["winddirection"].fillna(0)

print(df.columns)
print(df.head(10))
print(df["event_time"].isna().sum())

# -----------------------------
# REMOVE ONLY TRULY INVALID ROWS
# -----------------------------
df = df.dropna(subset=["city", "event_time"])


# -----------------------------
# VALIDATION (NON-DESTRUCTIVE)
# -----------------------------
validate_weather_data(df)

print("Before dropna shape:", df.shape)
print("NaT event_time:", df["event_time"].isna().sum())


# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
df = df.drop_duplicates(subset=["city", "event_time"], keep="last")

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
df["is_windy"] = df["windspeed"] > 20

df["wind_category"] = df["windspeed"].apply(
    lambda x: "low" if x < 10 else "medium" if x < 25 else "high"
)

# -----------------------------
# SORT
# -----------------------------
df = df.sort_values(by=["city", "event_time"])

print("Clean records:", len(df))

# -----------------------------
# SAVE SILVER LAYER
# -----------------------------
output_file = f"{SILVER_PATH}weather_silver.parquet"
df.to_parquet(output_file, index=False)

print("Saved Silver dataset at:", output_file)