import logging
import requests
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
mcp = FastMCP("Weather Service")

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}
RAIN_CODES = [51, 53, 55, 61, 63, 65, 80, 81, 82]

def geocode_city(city: str):
    geo_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1}
    try:
        resp = requests.get(geo_url, params=params, timeout=5, headers={"User-Agent": "jarvis-weather/1.0"})
        geo_data = resp.json()
        if geo_data:
            lat = float(geo_data[0]["lat"])
            lon = float(geo_data[0]["lon"])
            return lat, lon
        else:
            logger.error(f"Geocoding found no results for city '{city}'")
            return None
    except Exception as e:
        logger.error(f"Geocoding failed for city '{city}': {e}")
        return None

@mcp.tool()
def get_weather_info(location) -> dict:
    """
    Get weather info for a (lat, lon) tuple or city name string.
    Returns a dict with a formatted message and details.
    """
    if isinstance(location, tuple) and len(location) == 2:
        lat, lon = location
    elif isinstance(location, str):
        geo = geocode_city(location)
        if not geo:
            return {"success": False, "message": f"Could not find location '{location}'."}
        lat, lon = geo
    else:
        return {"success": False, "message": "Invalid location format."}

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        if not current:
            return {"success": False, "message": "No weather data found", "details": data}
        temp = current.get("temperature")
        wind = current.get("windspeed")
        weather_code = current.get("weathercode")
        is_day = current.get("is_day")
        weather_desc = WEATHER_CODE_MAP.get(weather_code, f"Unknown (code {weather_code})")
        rain_status = "Yes" if weather_code in RAIN_CODES else "No"
        day_status = "Day" if is_day == 1 else "Night"
        weather_str = (
            f"Current temperature: {temp}°C, Wind speed: {wind} km/h. "
            f"Weather: {weather_desc}. "
            f"Is it raining? {rain_status}. "
            f"Time of day: {day_status}."
        )
        return {
            "success": True,
            "message": weather_str,
            "details": current
        }
    except Exception as e:
        logger.error(f"Error fetching weather: {str(e)}")
        return {"success": False, "message": f"Failed to fetch weather: {str(e)}"}

if __name__ == "__main__":
    mcp.run()
