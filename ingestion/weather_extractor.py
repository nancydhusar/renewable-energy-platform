import requests
from datetime import datetime, UTC

def fetch_weather():

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=52.52"
        "&longitude=13.41"
        "&current_weather=true"
    )

    response = requests.get(url)

    weather = response.json()["current_weather"]

    return {
        "city": "Berlin",
        "event_time": weather["time"],
        "temperature": weather["temperature"],
        "windspeed": weather["windspeed"],
        "winddirection": weather["winddirection"],
        "is_day": weather["is_day"],
        "weathercode": weather["weathercode"],
        "ingestion_time": datetime.now(UTC).isoformat()
    }

print(fetch_weather())