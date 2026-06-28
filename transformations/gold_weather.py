import pandas as pd
import os

# -----------------------------
# PATHS
# -----------------------------
SILVER_PATH = "lakehouse/silver/weather/weather_silver.parquet"
GOLD_PATH = "lakehouse/gold/weather/"

os.makedirs(GOLD_PATH, exist_ok=True)

# -----------------------------
# LOAD SILVER DATA
# -----------------------------
df = pd.read_parquet(SILVER_PATH)

print("Silver records:", len(df))

# -----------------------------
# BASIC CLEANING (VERY IMPORTANT)
# -----------------------------
df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")

df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
df["windspeed"] = pd.to_numeric(df["windspeed"], errors="coerce")
df["winddirection"] = pd.to_numeric(df["winddirection"], errors="coerce")

df["is_day"] = df["is_day"].fillna(0)
df["weathercode"] = df["weathercode"].fillna(0)
df["cloud_cover"] = df["cloud_cover"].fillna(0)

# remove invalid timestamps
df = df.dropna(subset=["event_time"])

# -----------------------------
# TIME FEATURES
# -----------------------------
df["hour"] = df["event_time"].dt.hour
df["day_of_week"] = df["event_time"].dt.dayofweek
df["month"] = df["event_time"].dt.month

# -----------------------------
# SEASON FEATURE
# -----------------------------
def get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

df["season"] = df["month"].apply(get_season)

# -----------------------------
# SOLAR SCORE (VECTORISED)
# -----------------------------
df["solar_score"] = 0

df.loc[df["is_day"] == 1, "solar_score"] += 40
df.loc[df["weathercode"].isin([0, 1]), "solar_score"] += 30
df.loc[df["weathercode"].isin([2, 3]), "solar_score"] -= 20

df["solar_score"] += df["temperature"] * 1.2
df["solar_score"] = df["solar_score"].fillna(0)
df["solar_score"] = df["solar_score"].clip(0, 100)

# -----------------------------
# WIND FEATURES
# -----------------------------
df["wind_energy_index"] = df["windspeed"] ** 3

# avoid divide-by-zero
max_wind = df["wind_energy_index"].max()
df["wind_energy_norm"] = df["wind_energy_index"] / max_wind if max_wind else 0

df["wind_category"] = df["windspeed"].apply(
    lambda x: "low" if x < 10 else "medium" if x < 25 else "high"
)

df["is_windy"] = df["windspeed"] > 20

# -----------------------------
# ENERGY POTENTIAL (FINAL KPI)
# -----------------------------
df["energy_potential"] = (
    df["solar_score"] * 0.5 +
    df["wind_energy_norm"] * 50
)

# -----------------------------
# ROLLING FEATURES (TIME SERIES)
# IMPORTANT: grouped by city
# -----------------------------
df = df.sort_values(["city", "event_time"])

# -----------------------------
# ROLLING FEATURES
# -----------------------------
df["temp_6h_avg"] = (
    df.groupby("city")["temperature"]
    .rolling(6, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)
df["wind_24h_avg"] = (
    df.groupby("city")["windspeed"]
    .rolling(24, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)


# -----------------------------
# ADD MAX TEMPERATURE PER CITY (NEW IMPORTANT FEATURE)
# -----------------------------
df["max_temperature_city"] = df.groupby("city")["temperature"].transform("max")


# -----------------------------
# ENERGY STABILITY INDEX
# -----------------------------
df["energy_stability_index"] = (
    (df["solar_score"] * 0.5) +
    (df["wind_energy_index"] * 0.3) +
    ((100 - df["cloud_cover"]) * 0.2)
)

df["energy_stability_index"] = df["energy_stability_index"].fillna(0)

# -----------------------------
# FINAL CLEANUP
# -----------------------------
df = df.drop_duplicates(subset=["city", "event_time"], keep="last")

# -----------------------------
# SAVE GOLD DATA
# -----------------------------
output_file = f"{GOLD_PATH}weather_gold.parquet"
df.to_parquet(output_file, index=False)

print("Saved GOLD dataset:", output_file)
print("Final records:", len(df))