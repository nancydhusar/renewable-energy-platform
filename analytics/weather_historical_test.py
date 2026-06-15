#import pandas as pd

#df = pd.read_parquet(
#    "lakehouse/weather_historical/germany_weather_history.parquet"
#)

#print(df.shape)
#print(df.columns.tolist())

import pandas as pd

df = pd.read_parquet(
    "lakehouse/weather_historical/germany_weather_history.parquet"
)

print(df.columns.tolist())