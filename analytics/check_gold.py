#import pandas as pd

#df = pd.read_parquet("lakehouse/gold/weather/weather_gold.parquet")

#print(df.columns.tolist())
#print()
#print(df[["city", "lat", "lon"]].head())

#--------------------------------------------
#--------------------------------------------
#CHECKING FILE 

import pandas as pd

df = pd.read_parquet(
    "lakehouse/gold/weather/weather_gold.parquet"
)
df.to_csv(
    "lakehouse/gold/weather/weather_gold.csv",
    index=False
)

print(df.head())
print(df.columns)

#--------------------------------------------
#--------------------------------------------
#HIGHEST TEMP FILE 

