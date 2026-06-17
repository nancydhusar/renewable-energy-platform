import duckdb
import pandas as pd
import os
from quality_checks.validate_weather import validate_weather_data
import sys

sys.path.append(os.path.abspath("."))

RAW_PATHS = [
    "lakehouse/weather/**/*.parquet",
    "lakehouse/weather_historical/*.parquet"
]
SILVER_PATH = "lakehouse/silver/weather/"

os.makedirs(SILVER_PATH, exist_ok=True)

# ------------------------------
# Run Validation Checks
# ------------------------------
df = duckdb.query("""
    SELECT *
    FROM read_parquet([
        'lakehouse/weather/**/*.parquet',
        'lakehouse/weather_historical/*.parquet'
    ], union_by_name=true)
""").df()

# -----------------------------
# VALIDATION STEP (NEW)
# -----------------------------
validate_weather_data(df)


# Load raw data
df = duckdb.query("""
    SELECT *
    FROM read_parquet([
        'lakehouse/weather/**/*.parquet',
        'lakehouse/weather_historical/*.parquet'
    ], union_by_name=true)
""").df()

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

for col in ["lat","lon"]:
    if col not in df.columns:
        df[col] = None

df = df[COMMON_COLUMNS]
# -----------------------------
# 1. TYPE CLEANING
# -----------------------------
df["temperature"] = df["temperature"].astype(float)
df["windspeed"] = df["windspeed"].astype(float)
df["winddirection"] = df["winddirection"].astype(int)

# -----------------------------
# 2. TIMESTAMP STANDARDIZATION
# -----------------------------
df["event_time"] = pd.to_datetime(df["event_time"], format="mixed")

# -----------------------------
# 3. REMOVE DUPLICATES
# -----------------------------
df = df.drop_duplicates(subset=["city", "event_time"])

# -----------------------------
# 4. FEATURE ENGINEERING (LIGHT SILVER LOGIC)
# -----------------------------

df["is_windy"] = df["windspeed"] > 20

df["wind_category"] = df["windspeed"].apply(
    lambda x: "low" if x < 10 else "medium" if x < 25 else "high"
)

# -----------------------------
# 5. SORT DATA
# -----------------------------
df = df.sort_values(by=["city", "event_time"])
df = df.drop_duplicates(subset=["city", "event_time"], keep="last")
print("Clean records:", len(df))

# -----------------------------
# 6. SAVE SILVER DATA
# -----------------------------
output_file = f"{SILVER_PATH}weather_silver.parquet"
df.to_parquet(output_file, index=False)

print("Saved Silver dataset at:", output_file)