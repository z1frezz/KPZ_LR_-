import pandas as pd
from datetime import datetime

file_name = 'filename.csv'
data_columns = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']

try:
  data = pd.read_csv(file_name, index_col=0)
except FileNotFoundError:
  data = pd.DataFrame(columns=data_columns)

current_time = datetime.now()

new_data = pd.DataFrame([[current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second]], columns=data_columns)

# Use concat to combine DataFrames
data = pd.concat([data, new_data], ignore_index=True)

data.to_csv(file_name)

print(file_name)
