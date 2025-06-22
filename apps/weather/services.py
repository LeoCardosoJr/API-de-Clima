import requests
import os

def get_weather_data(city: str) -> dict:
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
