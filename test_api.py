import requests
import json

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "hourly": "temperature_2m,rain,weather_code",
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json()

with open("data/raw_weather.json", "w") as file:
    json.dump(data, file, indent=2)

print("Weather data ingested successfully")