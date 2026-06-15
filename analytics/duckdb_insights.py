import duckdb
import pandas as pd

GOLD_PATH = "lakehouse/gold/weather/weather_gold.parquet"

df = duckdb.query(f"""
    SELECT *
    FROM read_parquet('{GOLD_PATH}')
""").df()

print("Total records:", len(df))

# -----------------------------
# 1. CITY RANKING
# -----------------------------
city_rank = duckdb.query("""
    SELECT city,
           AVG(energy_potential) AS avg_energy
    FROM df
    GROUP BY city
    ORDER BY avg_energy DESC
""").df()

print("\n🌍 City Energy Ranking")
print(city_rank)

# -----------------------------
# 2. SOLAR vs WIND
# -----------------------------
solar_wind = duckdb.query("""
    SELECT city,
           AVG(solar_score) AS solar,
           AVG(wind_energy_index) AS wind
    FROM df
    GROUP BY city
""").df()

print("\n☀️ Solar vs 🌬 Wind Comparison")
print(solar_wind)

# -----------------------------
# 3. SEASONAL ANALYSIS
# -----------------------------
seasonal = duckdb.query("""
    SELECT season,
           AVG(energy_potential) AS energy
    FROM df
    GROUP BY season
    ORDER BY energy DESC
""").df()

print("\n🍂 Seasonal Energy Pattern")
print(seasonal)

# -----------------------------
# 4. HOURLY PATTERN
# -----------------------------
hourly = duckdb.query("""
    SELECT hour,
           AVG(energy_potential) AS energy
    FROM df
    GROUP BY hour
    ORDER BY hour
""").df()

print("\n⏰ Hourly Energy Pattern")
print(hourly)