"""Weather forecasts and simple farm advice.

The provider is swappable (WEATHER_PROVIDER in .env):
- OpenMeteoWeatherProvider (default): live forecasts from the free Open-Meteo API
  (https://open-meteo.com), no API key needed. Districts and their coordinates come from
  data/weather.json. Forecasts are cached per district, so repeated questions don't call the API.
- JsonWeatherProvider: the fixed sample forecasts in data/weather.json (tests, offline work).

Open-Meteo's free API is for non-commercial use (up to 10,000 calls a day); commercial use
needs one of their paid plans.
"""
import logging
import threading
import time
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from statistics import mean
from typing import Protocol

import httpx

from app.core.config import get_settings
from app.i18n import LocalizedText
from app.services.data_loader import load_json

logger = logging.getLogger("farmer_assistant.weather")


@dataclass(frozen=True)
class District:
    id: str
    name: LocalizedText


@dataclass(frozen=True)
class DayForecast:
    date: date
    condition: str  # condition code, translated via i18n key cond_<code>
    temp_min_c: float
    temp_max_c: float
    rain_mm: float
    humidity_pct: float
    wind_kmh: float


@dataclass(frozen=True)
class WeatherReport:
    district: District
    days: list[DayForecast]
    advice_keys: list[str]  # i18n keys, translated by the presenter


class WeatherProvider(Protocol):
    def districts(self) -> list[District]: ...
    def forecast(self, district_id: str, days: int) -> list[DayForecast]: ...


class JsonWeatherProvider:
    def __init__(self, filename: str = "weather.json") -> None:
        self._data = load_json(filename)

    def districts(self) -> list[District]:
        return [District(d["id"], d["name"]) for d in self._data["districts"]]

    def forecast(self, district_id: str, days: int) -> list[DayForecast]:
        entry = next((d for d in self._data["districts"] if d["id"] == district_id), None)
        if entry is None:
            return []
        today = date.today()
        return [
            DayForecast(
                date=today + timedelta(days=f["day_offset"]),
                condition=f["condition"],
                temp_min_c=f["temp_min_c"],
                temp_max_c=f["temp_max_c"],
                rain_mm=f["rain_mm"],
                humidity_pct=f["humidity_pct"],
                wind_kmh=f["wind_kmh"],
            )
            for f in sorted(entry["forecast"], key=lambda x: x["day_offset"])[:days]
        ]


# WMO weather interpretation codes (used by Open-Meteo) -> our condition codes (i18n cond_<code>).
_WMO_CONDITIONS: dict[int, str] = {
    0: "sunny", 1: "sunny", 2: "partly_cloudy", 3: "cloudy",
    45: "fog", 48: "fog",
    51: "drizzle", 53: "drizzle", 55: "drizzle", 56: "drizzle", 57: "drizzle",
    61: "light_rain", 66: "light_rain", 80: "light_rain",
    63: "rain", 81: "rain",
    65: "heavy_rain", 67: "heavy_rain", 82: "heavy_rain",
    71: "snow", 73: "snow", 75: "snow", 77: "snow", 85: "snow", 86: "snow",
    95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm",
}


def wmo_condition(code: int | None) -> str:
    return _WMO_CONDITIONS.get(code, "cloudy") if code is not None else "cloudy"


class OpenMeteoWeatherProvider:
    """Live daily forecasts from Open-Meteo for the districts listed in data/weather.json."""

    DAILY = "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"

    def __init__(
        self,
        url: str = "https://api.open-meteo.com/v1/forecast",
        cache_minutes: int = 60,
        timeout_seconds: float = 10,
        filename: str = "weather.json",
        http: httpx.Client | None = None,
    ) -> None:
        self.url, self.cache_seconds, self.timeout = url, cache_minutes * 60, timeout_seconds
        self._districts = load_json(filename)["districts"]
        self._http = http
        self._cache: dict[tuple[str, int], tuple[float, list[DayForecast]]] = {}
        self._lock = threading.Lock()

    def districts(self) -> list[District]:
        return [District(d["id"], d["name"]) for d in self._districts]

    def forecast(self, district_id: str, days: int) -> list[DayForecast]:
        entry = next((d for d in self._districts if d["id"] == district_id), None)
        if entry is None:
            return []
        key = (district_id, days)
        with self._lock:
            cached = self._cache.get(key)
        from_today = bool(cached) and cached[1][0].date == date.today()
        if from_today and time.monotonic() - cached[0] < self.cache_seconds:
            return cached[1]
        try:
            forecast = self._fetch(entry["latitude"], entry["longitude"], days)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            logger.exception("Open-Meteo request failed for %s", district_id)
            # A slightly old forecast from today is better than none; never show yesterday's.
            return cached[1] if from_today else []
        if forecast:
            with self._lock:
                self._cache[key] = (time.monotonic(), forecast)
        return forecast

    def _fetch(self, latitude: float, longitude: float, days: int) -> list[DayForecast]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": self.DAILY,
            "hourly": "relative_humidity_2m",  # averaged per day below
            "timezone": "Asia/Karachi",
            "forecast_days": days,
            "wind_speed_unit": "kmh",
        }
        client = self._http or httpx
        response = client.get(self.url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return parse_open_meteo(response.json())


def parse_open_meteo(data: dict) -> list[DayForecast]:
    """Open-Meteo JSON (daily values + hourly humidity) -> one DayForecast per day."""
    daily, hourly = data["daily"], data.get("hourly") or {}
    humidity_by_day: dict[str, list[float]] = {}
    for stamp, value in zip(hourly.get("time", []), hourly.get("relative_humidity_2m", []), strict=False):
        if value is not None:
            humidity_by_day.setdefault(stamp[:10], []).append(value)

    def number(name: str, i: int) -> float:
        value = daily[name][i]
        return float(value) if value is not None else 0.0

    days = []
    for i, day in enumerate(daily["time"]):
        humidity = humidity_by_day.get(day)
        days.append(
            DayForecast(
                date=date.fromisoformat(day),
                condition=wmo_condition(daily["weather_code"][i]),
                temp_min_c=number("temperature_2m_min", i),
                temp_max_c=number("temperature_2m_max", i),
                rain_mm=number("precipitation_sum", i),
                humidity_pct=mean(humidity) if humidity else 0.0,
                wind_kmh=number("wind_speed_10m_max", i),
            )
        )
    return days


@lru_cache
def default_weather_provider() -> WeatherProvider:
    """One shared provider per process, so its forecast cache lasts across requests."""
    settings = get_settings()
    if settings.weather_provider == "json":
        return JsonWeatherProvider()
    return OpenMeteoWeatherProvider(
        url=settings.open_meteo_url,
        cache_minutes=settings.weather_cache_minutes,
        timeout_seconds=settings.weather_timeout_seconds,
    )


def farm_advice(days: list[DayForecast]) -> list[str]:
    """Rule-based advice. Returns up to two i18n keys, most important first."""
    advice: list[str] = []
    if any(d.rain_mm >= 5 for d in days):
        advice.append("advice_rain")
    if any(d.temp_max_c >= 38 for d in days):
        advice.append("advice_heat")
    if any(d.temp_min_c <= 4 for d in days):
        advice.append("advice_frost")
    if any(d.wind_kmh >= 20 for d in days):
        advice.append("advice_wind")
    if any(d.humidity_pct >= 65 or "fog" in d.condition.lower() for d in days):
        advice.append("advice_humid")
    return advice[:2] or ["advice_default"]


class WeatherService:
    FORECAST_DAYS = 3

    def __init__(self, provider: WeatherProvider | None = None) -> None:
        self.provider = provider or default_weather_provider()

    def districts(self) -> list[District]:
        return self.provider.districts()

    def get_report(self, district_id: str) -> WeatherReport | None:
        district = next((d for d in self.districts() if d.id == district_id), None)
        if district is None:
            return None
        days = self.provider.forecast(district_id, self.FORECAST_DAYS)
        if not days:
            return None
        return WeatherReport(district=district, days=days, advice_keys=farm_advice(days))
