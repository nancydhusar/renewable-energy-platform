import duckdb

con = duckdb.connect("weather.db")

con.execute("""
CREATE OR REPLACE TABLE weather_gold AS
SELECT *
FROM read_parquet(
    'lakehouse/gold/weather/weather_gold.parquet'
)
""")

daily_summary = con.execute("""
SELECT
    DATE(event_time) AS weather_date,
    AVG(temperature) AS avg_temperature,
    MAX(windspeed) AS max_windspeed,
    AVG(solar_score) AS avg_solar_score,
    AVG(wind_energy_index) AS avg_wind_energy
FROM weather_gold
GROUP BY 1
ORDER BY 1
""").df()

print(daily_summary)