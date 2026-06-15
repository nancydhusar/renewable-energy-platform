import pandas as pd

df = pd.read_parquet("lakehouse/gold/weather/weather_gold.parquet")

print(df.columns.tolist())
print()
print(df[["city", "lat", "lon"]].head())