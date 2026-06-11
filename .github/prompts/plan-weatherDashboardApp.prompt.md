# Weather Dashboard App — Plan

## Functional Requirements

### User Interface
- Display current weather conditions (temperature, humidity, wind speed, weather description, icon)
- Show a multi-day forecast (5–7 days)
- Allow users to search for weather by city name or ZIP/postal code
- Display location name, country, and local time
- Toggle between Celsius and Fahrenheit
- Show hourly forecast for the current day
- Display UV index, visibility, precipitation, and "feels like" temperature

### Backend (Flask)
- Expose a REST API endpoint (`GET /api/weather?city=`) to fetch weather data
- Integrate with OpenWeatherMap API
- Cache API responses to reduce redundant third-party calls
- Return structured JSON responses to the frontend
- Handle invalid city names and API errors gracefully with appropriate HTTP status codes

### Data & State
- Save recent searches (last 5 cities) in browser `localStorage`
- Allow users to save/pin favourite locations
- Auto-detect user location via browser Geolocation API (with permission)

---

## Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | API response < 500ms; frontend initial render < 2s; 10-min server-side cache TTL |
| **Reliability** | Graceful degradation with stale data + warning when OWM is unavailable |
| **Security** | API key in `.env` only; Flask proxies all OWM calls; input validation on backend |
| **Usability** | Fully responsive (mobile/tablet/desktop); WCAG AA accessible; loading indicators |
| **Maintainability** | Separate HTML/CSS/JS files; Flask Blueprints if app grows; env-based config |
| **Scalability** | Stateless Flask API; swappable cache backend (e.g., Redis) |
| **Compatibility** | Modern browsers (last 2 versions); Python 3.10+ / Flask 3.x |

---

## User Stories

### US-01: Search Weather by City
> *As a traveller, I want to search for current weather by city name so that I can check conditions at my destination before I leave.*

**Acceptance Criteria:**
- A search input and button are visible on the dashboard
- Entering a valid city name displays current temperature, humidity, wind speed, and a weather icon
- Entering an invalid city name shows a clear error message ("City not found")
- The searched city is added to the recent searches list

---

### US-02: View Multi-Day Forecast
> *As a trip planner, I want to see a 5-day weather forecast so that I can decide the best days for outdoor activities.*

**Acceptance Criteria:**
- After searching a city, a 5-day forecast section is displayed below current weather
- Each day shows date, weather icon, high/low temperatures, and a short description
- Forecast updates whenever a new city is searched

---

### US-03: Switch Temperature Units
> *As a user accustomed to Fahrenheit, I want to toggle between Celsius and Fahrenheit so that I can read temperatures in my preferred unit.*

**Acceptance Criteria:**
- A toggle button (°C / °F) is always visible on the dashboard
- Clicking the toggle instantly converts all displayed temperatures without a new API call
- The selected unit persists across searches within the same session

---

### US-04: Auto-Detect My Location
> *As a casual user, I want the app to automatically show my local weather when I open it so that I don't have to type my city every time.*

**Acceptance Criteria:**
- On first load, the browser prompts the user for location permission
- If permission is granted, current weather and forecast for the user's location are loaded automatically
- If permission is denied, a default prompt ("Search for a city") is shown instead
- The detected location name is displayed in the results

---

## Architecture

### Component Responsibilities

| Layer | Technology | Responsibility |
|---|---|---|
| **UI** | HTML + CSS | Layout, weather cards, search input, unit toggle |
| **Logic** | JavaScript (app.js) | Fetch calls, DOM updates, unit conversion, localStorage |
| **API** | Flask (Python) | Route handling, caching, error formatting, API key proxy |
| **Cache** | Flask-Caching | Reduce OWM calls; 10-min TTL per city |
| **External** | OpenWeatherMap | Source of truth for weather + forecast data |

### Data Flow

1. User types a city name and clicks Search (or browser Geolocation fires on page load)
2. `app.js` sends `GET /api/weather?city=London` to the Flask backend
3. Flask checks the cache for "London"
   - **Cache HIT** → return stored JSON immediately
   - **Cache MISS** → call `api.openweathermap.org/data/2.5/forecast?q=London&appid=API_KEY`, store result in cache (TTL 10 min), then return
4. Flask returns a structured JSON response (or `{ "error": "..." }` with an appropriate HTTP status)
5. `app.js` parses the JSON and updates the DOM (current weather card + 5-day forecast strip)
6. `app.js` saves "London" to `localStorage` recent searches

### Key Design Decisions
- **API key never reaches the browser** — Flask acts as a proxy; the key lives in `.env` only
- **Cache sits inside Flask** — a cache hit never touches OWM, reducing latency and API quota usage
- **Frontend does unit conversion** — °C/°F toggle happens in JS without a new API call
- **Error boundaries at Flask** — OWM errors are caught and returned as clean JSON with HTTP status codes

---

## Suggested Project Structure

```
weather-dashboard/
├── backend/
│   ├── app.py            # Flask app factory + route registration
│   ├── routes.py         # /api/weather endpoint (Blueprint)
│   ├── weather.py        # OWM API client + response normaliser
│   ├── cache.py          # Flask-Caching setup
│   └── .env              # API_KEY (never committed)
├── frontend/
│   ├── index.html        # App shell
│   ├── style.css         # Responsive styles
│   └── app.js            # Fetch, DOM update, localStorage, unit toggle
├── requirements.txt
└── .gitignore            # Must include .env
```
