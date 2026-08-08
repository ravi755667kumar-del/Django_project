import requests

from django.core.cache import cache
from django.conf import settings

# ==========================
# Configuration
# ==========================

API_KEY = settings.WEATHER_API_KEY

CITY = "Thoothukudi"      # Change to your city

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

CACHE_KEY = "current_weather"

CACHE_TIMEOUT = 60 * 30      # 30 Minutes


# ==========================
# Get Weather
# ==========================

def get_weather():

    # Check cache first
    cached_weather = cache.get(CACHE_KEY)

    if cached_weather:
        print("Weather loaded from Cache")

        return cached_weather

    # API Parameters
    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric"
    }

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        weather = data["weather"][0]["main"]

        temperature = data["main"]["temp"]

        humidity = data["main"]["humidity"]

        city = data["name"]

        # Convert weather into recommendation category

        if weather in ["Rain", "Drizzle", "Thunderstorm"]:
            category = "Rain"

        elif weather == "Clear":
            category = "Hot"

        elif weather in ["Clouds"]:
            category = "Normal"

        elif weather in ["Mist", "Fog", "Haze"]:
            category = "Cold"

        else:
            category = "Normal"

        result = {

            "city": city,

            "weather": weather,

            "category": category,

            "temperature": temperature,

            "humidity": humidity

        }

        # Save into cache

        cache.set(
            CACHE_KEY,
            result,
            CACHE_TIMEOUT
        )

        print("Weather loaded from API")

        return result

    except Exception as e:

        print(e)


        return {

            "city": CITY,

            "weather": "Unknown",

            "category": "Normal",

            "temperature": 0,

            "humidity": 0

        }


# ==========================
# Testing
# ==========================

if __name__ == "__main__":

    weather = get_weather()

    print(weather)