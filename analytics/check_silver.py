import pandas as pd

df = pd.read_parquet(
    "lakehouse/silver/weather/weather_silver.parquet"
)

print(df.columns.tolist())