import requests
import csv
from datetime import datetime, timedelta


def fetch_weather_data(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily":[
            "temperature_2m_max", 
            "temperature_2m_min", 
            "precipitation_sum",
            "wind_speed_10m_max",
            "shortwave_radiation_sum",
            "et0_fao_evapotranspiration"
            ],
        "timezone": "Africa/Nairobi"
    }
    
    print(f"Fetching archive data from {start_date} to {end_date}...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Get the raw json response
    raw_data = response.json()
    daily_data = raw_data["daily"]
    
    
    filename = f"nairobi_weather_backfill_{start_date}_to_{end_date}.csv"
    
    with open (filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'date', 'temp_max_c', 'temp_min_c', 'precipitation_mm', 
            'wind_speed_max_kmh', 'solar_radiation_mj_m2', 'evapotranspiration_mm'
            ])
        num_days = len(daily_data["time"])
        for i in range(num_days):
            writer.writerow([
                daily_data["time"][i],
                daily_data["temperature_2m_max"][i],
                daily_data["temperature_2m_min"][i],
                daily_data["precipitation_sum"][i],
                daily_data["wind_speed_10m_max"][i],
                daily_data["shortwave_radiation_sum"][i],
                daily_data["et0_fao_evapotranspiration"][i]
            ])
         
        
    print(f"Success! {num_days} rows of historical data saved to {filename}")
    
if __name__ == "__main__":
    # 20 year backfil parameters for deep climate analysis
    end_date_str = "2026-08-05"
    start_date_str = "2006-08-05"
    
    fetch_weather_data(-1.2921, 36.8219, start_date_str, end_date_str)