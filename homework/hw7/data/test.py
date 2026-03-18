import pandas as pd

df = pd.read_parquet("./green_tripdata_2025-10.parquet")
print(df.columns)