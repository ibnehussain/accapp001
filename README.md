# accapp001 Weather Dashboard

`accapp001` is a small Flask weather app with a single-page dashboard (`index.html`) and a backend API (`app.py`) that serves current weather data.

## Features

- Search weather by city from the browser UI.
- `GET /weather` API endpoint for weather data.
- Mock mode support for local testing without an API key.
- Error handling for missing input, missing API key, timeouts, and service failures.

## Tech Stack

- Python 3
- Flask
- Requests

## Project Structure

- `app.py` – Flask backend and weather API integration.
- `index.html` – Frontend dashboard UI.

## Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

   ```bash
   pip install flask requests
   ```

3. (Optional for real API mode) Set your OpenWeatherMap API key:

   ```bash
   export OWM_API_KEY="your_key_here"
   ```

4. (Optional) Force mock mode:

   ```bash
   export MOCK_MODE=true
   ```

## Run the App

From the project root directory:

```bash
python app.py
```

The app runs on `http://127.0.0.1:5000`.

## API Usage

### `GET /weather?city=<city>`

Example:

```bash
curl "http://127.0.0.1:5000/weather?city=London"
```

Example response shape:

```json
{
  "city": "London",
  "country": "GB",
  "temp": 14.3,
  "feels_like": 12.8,
  "humidity": 78,
  "description": "overcast clouds",
  "icon": "04d",
  "wind_speed": 5.1,
  "pressure": 1012,
  "visibility": 9.2,
  "clouds": 90
}
```

`visibility` is returned in kilometers (km). OpenWeatherMap provides visibility in meters, and this app converts it to km before returning the response.

## Notes

- If `OWM_API_KEY` is not set, the app automatically runs in mock mode.
- In mock mode, supported cities include: London, New York, Tokyo, Paris, Sydney, Dubai, Berlin, Mumbai, Toronto, and Cairo.
