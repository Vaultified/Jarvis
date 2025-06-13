import logging
import requests
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, CallToolResult
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)
mcp = FastMCP("Weather Service")

# Weather code mapping (Open-Meteo)
WEATHER_CODES = {
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
    99: "Thunderstorm with heavy hail"
}

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def geocode_city(city: str) -> Union[Dict[str, float], None]:
    try:
        params = {
            "q": city,
            "format": "json",
            "limit": 1
        }
        resp = requests.get(GEOCODE_URL, params=params, headers={"User-Agent": "MCP-Weather-Agent"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data and len(data) > 0:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"])
            }
        return None
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None


def get_weather(lat: float, lon: float) -> Union[Dict[str, Any], None]:
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
        resp = requests.get(WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "current_weather" in data:
            return data["current_weather"]
        return None
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None


def format_weather_response(weather: Dict[str, Any], location: str = "") -> str:
    code = weather.get("weathercode")
    desc = WEATHER_CODES.get(code, "Unknown")
    temp = weather.get("temperature")
    wind = weather.get("windspeed")
    loc_str = f" in {location}" if location else ""
    return f"Current weather{loc_str}: {desc}, {temp}°C, wind {wind} km/h."


@mcp.tool()
def get_weather_info(location: Union[str, tuple]) -> CallToolResult:
    """
    Get weather information for a location.
    
    Args:
        location: Either a city name (str) or a tuple of (latitude, longitude)
        
    Returns:
        CallToolResult containing the weather information
    """
    try:
        if isinstance(location, tuple) and len(location) == 2:
            lat, lon = location
            weather = get_weather(lat, lon)
            if weather:
                message = format_weather_response(weather, f"{lat},{lon}")
                return CallToolResult(
                    content=[TextContent(type="text", text=message, uri=None, mimeType=None)],
                    isError=False
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Could not fetch weather for the given coordinates.", uri=None, mimeType=None)],
                    isError=True
                )
        elif isinstance(location, str):
            geo = geocode_city(location)
            if not geo:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Could not find location '{location}'.", uri=None, mimeType=None)],
                    isError=True
                )
            weather = get_weather(geo["lat"], geo["lon"])
            if weather:
                message = format_weather_response(weather, location.title())
                return CallToolResult(
                    content=[TextContent(type="text", text=message, uri=None, mimeType=None)],
                    isError=False
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Could not fetch weather for '{location}'.", uri=None, mimeType=None)],
                    isError=True
                )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="Invalid location format.", uri=None, mimeType=None)],
                isError=True
            )
    except Exception as e:
        logger.error(f"Weather MCP error: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Weather service error: {str(e)}", uri=None, mimeType=None)],
            isError=True
        )

if __name__ == "__main__":
    mcp.run()
