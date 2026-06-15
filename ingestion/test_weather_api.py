import requests
import json

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=52.52"
    "&longitude=13.41"
    "&current_weather=true"
)

response = requests.get(url)

print(response.status_code)

data = response.json()

print(json.dumps(data, indent=2))