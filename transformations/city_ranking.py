import pandas as pd

df = pd.read_parquet(
    "lakehouse/gold/weather/weather_gold.parquet"
)

city_summary = (
    df.groupby("city")
    .agg({
        "solar_score": "mean",
        "wind_energy_index": "mean",
        "energy_potential": "mean",
        "energy_stability_index": "mean",
        "max_temperature_city": "max"
    })
    .reset_index()
)

city_summary["overall_rank"] = (
    city_summary["energy_potential"]
    .rank(ascending=False)
)

city_summary["solar_rank"] = (
    city_summary["solar_score"]
    .rank(ascending=False)
)

city_summary["wind_rank"] = (
    city_summary["wind_energy_index"]
    .rank(ascending=False)
)

city_summary["stability_rank"] = (
    city_summary["energy_stability_index"]
    .rank(ascending=False)
)

city_summary = city_summary.sort_values(
    "overall_rank"
).reset_index(drop=True)

city_summary.to_csv(
    "lakehouse/gold/weather/city_energy_ranking.csv",
    index=False
)

print(city_summary)