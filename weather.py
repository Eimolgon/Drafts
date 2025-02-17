import pandas as pd
from meteostat import Daily, Stations
from datetime import datetime
import openpyxl

# Define the location (Delft, Netherlands)
CITY_NAME = "Delft"
START_DATE = datetime(2024, 11, 1)
END_DATE = datetime(2025, 2, 28)

# Find the closest weather station to Delft
stations = Stations()
stations = stations.nearby(52.0116, 4.3571)  # Delft's latitude and longitude
station = stations.fetch(1)  # Fetch the nearest station
station_id = station.index[0]  # Get the station ID

# Fetch daily historical data
data = Daily(station_id, start=START_DATE, end=END_DATE)
data = data.fetch()

# Select the wind data
df = data[['wdir', 'wspd']]  # Wind direction (°) and wind speed (km/h)

# Duplicate the data for 08:00 and 17:00
df_morning = df.copy()
df_morning["Time"] = "08:00"

df_evening = df.copy()
df_evening["Time"] = "17:00"

# Combine both times
df_final = pd.concat([df_morning, df_evening])
df_final = df_final.reset_index()
df_final.columns = ["Date", "Wind Direction (°)", "Wind Speed (km/h)", "Time"]

# Save to Excel
output_file = "Delft_Wind_Data.xlsx"
df_final.to_excel(output_file, index=False)

print(f"Wind data saved to {output_file}")

