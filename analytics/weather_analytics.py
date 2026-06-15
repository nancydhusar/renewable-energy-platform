import duckdb
import pandas as pd

GOLD_PATH = "lakehouse/gold/weather/weather_gold.parquet"

# -----------------------------
# LOAD GOLD DATA INTO DUCKDB
# -----------------------------
con = duckdb.connect()

df = con.execute(f"""
    SELECT *
    FROM read_parquet('{GOLD_PATH}')
""").df()

print("Records:", len(df))

# -----------------------------
# 1. SEASONAL ANALYSIS
# -----------------------------
seasonal = con.execute("""
    SELECT season,
           AVG(solar_score) AS avg_solar,
           AVG(wind_energy_index) AS avg_wind,
           AVG(energy_potential) AS avg_energy
    FROM df
    GROUP BY season
    ORDER BY avg_energy DESC
""").df()

print("\n🌦 Seasonal Energy Insights")
print(seasonal)

# -----------------------------
# 2. HOURLY WIND PATTERN
# -----------------------------
hourly_wind = con.execute("""
    SELECT hour,
           AVG(windspeed) AS avg_wind
    FROM df
    GROUP BY hour
    ORDER BY avg_wind DESC
""").df()

print("\n🌬 Hourly Wind Pattern")
print(hourly_wind)

# -----------------------------
# 3. DAILY ENERGY TREND
# -----------------------------
df["day"] = pd.to_datetime(df["event_time"]).dt.date

daily = con.execute("""
    SELECT day,
           AVG(energy_potential) AS daily_energy
    FROM df
    GROUP BY day
    ORDER BY day
""").df()

print("\n⚡ Daily Energy Trend")
print(daily.head())

# -----------------------------
# 4. CITY COMPARISON
# -----------------------------
city = con.execute("""
    SELECT city,
           AVG(energy_potential) AS energy_score
    FROM df
    GROUP BY city
""").df()

print("\n🌍 City Comparison")
print(city)