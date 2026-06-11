import os
import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".")

# Set your OpenWeatherMap API key in the environment:
#   $env:OWM_API_KEY = "your_key_here"   (PowerShell)
#   export OWM_API_KEY="your_key_here"   (bash)
OWM_API_KEY = os.environ.get("OWM_API_KEY", "")
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---------------------------------------------------------------------------
# Realistic mock data — used when OWM_API_KEY is not set or MOCK_MODE=true
# ---------------------------------------------------------------------------
MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true" or not OWM_API_KEY

MOCK_WEATHER = {
    "london": {
        "city": "London", "country": "GB",
        "temp": 14.3, "feels_like": 12.8, "humidity": 78,
        "description": "overcast clouds", "icon": "04d",
        "wind_speed": 5.1, "pressure": 1012, "visibility": 9.2, "clouds": 90,
    },
    "new york": {
        "city": "New York", "country": "US",
        "temp": 22.7, "feels_like": 23.1, "humidity": 62,
        "description": "few clouds", "icon": "02d",
        "wind_speed": 4.6, "pressure": 1018, "visibility": 10.0, "clouds": 20,
    },
    "tokyo": {
        "city": "Tokyo", "country": "JP",
        "temp": 28.5, "feels_like": 31.2, "humidity": 83,
        "description": "light rain", "icon": "10d",
        "wind_speed": 3.2, "pressure": 1008, "visibility": 6.5, "clouds": 75,
    },
    "paris": {
        "city": "Paris", "country": "FR",
        "temp": 18.9, "feels_like": 18.1, "humidity": 65,
        "description": "scattered clouds", "icon": "03d",
        "wind_speed": 4.0, "pressure": 1015, "visibility": 10.0, "clouds": 40,
    },
    "sydney": {
        "city": "Sydney", "country": "AU",
        "temp": 17.2, "feels_like": 16.4, "humidity": 70,
        "description": "moderate rain", "icon": "10d",
        "wind_speed": 6.7, "pressure": 1009, "visibility": 7.0, "clouds": 85,
    },
    "dubai": {
        "city": "Dubai", "country": "AE",
        "temp": 40.1, "feels_like": 43.5, "humidity": 38,
        "description": "clear sky", "icon": "01d",
        "wind_speed": 3.8, "pressure": 1002, "visibility": 10.0, "clouds": 0,
    },
    "berlin": {
        "city": "Berlin", "country": "DE",
        "temp": 16.0, "feels_like": 15.2, "humidity": 72,
        "description": "broken clouds", "icon": "04d",
        "wind_speed": 4.9, "pressure": 1014, "visibility": 9.8, "clouds": 60,
    },
    "mumbai": {
        "city": "Mumbai", "country": "IN",
        "temp": 32.4, "feels_like": 38.0, "humidity": 88,
        "description": "thunderstorm", "icon": "11d",
        "wind_speed": 7.2, "pressure": 1005, "visibility": 4.0, "clouds": 95,
    },
    "toronto": {
        "city": "Toronto", "country": "CA",
        "temp": 8.6, "feels_like": 5.9, "humidity": 55,
        "description": "light snow", "icon": "13d",
        "wind_speed": 6.1, "pressure": 1022, "visibility": 5.5, "clouds": 80,
    },
    "cairo": {
        "city": "Cairo", "country": "EG",
        "temp": 35.7, "feels_like": 34.3, "humidity": 25,
        "description": "clear sky", "icon": "01d",
        "wind_speed": 2.5, "pressure": 1010, "visibility": 10.0, "clouds": 0,
    },
}


@app.route("/")
def index():
    """Serve the weather dashboard HTML page."""
    return send_from_directory(".", "index.html")


@app.route("/weather")
def weather():
    """
    GET /weather?city=<city name>

    Fetches current weather from OpenWeatherMap and returns a flat JSON object:
    {
        city, country, temp, feels_like, humidity,
        description, icon, wind_speed, pressure,
        visibility (km), clouds
    }
    Returns { error: "..." } with an appropriate HTTP status on failure.
    """
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Please provide a city name."}), 400

    # ── Mock mode: return realistic dummy data without hitting the API ──
    if MOCK_MODE:
        mock = MOCK_WEATHER.get(city.lower())
        if mock:
            return jsonify(mock)
        return jsonify({"error": f'No mock data for "{city}". Try: London, New York, Tokyo, Paris, Sydney, Dubai, Berlin, Mumbai, Toronto, Cairo.'}), 404

    if not OWM_API_KEY:
        return jsonify({"error": "Server is missing the OWM_API_KEY environment variable."}), 500

    try:
        resp = requests.get(
            OWM_URL,
            params={"q": city, "appid": OWM_API_KEY, "units": "metric"},
            timeout=8,
        )
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not reach the weather service. Check your internet connection."}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "The weather service timed out. Please try again."}), 504

    if resp.status_code == 404:
        return jsonify({"error": f'City "{city}" not found. Check the spelling and try again.'}), 404
    if resp.status_code == 401:
        return jsonify({"error": "Invalid API key. Update OWM_API_KEY on the server."}), 401
    if not resp.ok:
        return jsonify({"error": f"Weather service error ({resp.status_code})."}), 502

    raw = resp.json()

    data = {
        "city":        raw["name"],
        "country":     raw["sys"]["country"],
        "temp":        raw["main"]["temp"],
        "feels_like":  raw["main"]["feels_like"],
        "humidity":    raw["main"]["humidity"],
        "description": raw["weather"][0]["description"],
        "icon":        raw["weather"][0]["icon"],
        "wind_speed":  raw["wind"]["speed"],
        "pressure":    raw["main"]["pressure"],
        "visibility":  round(raw.get("visibility", 0) / 1000, 1),
        "clouds":      raw["clouds"]["all"],
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
