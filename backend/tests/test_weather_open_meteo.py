"""Open-Meteo weather provider, with a mocked HTTP transport (no real API calls)."""
from datetime import date, timedelta

import httpx

from app.domain.messages import InboundKind, InboundMessage
from app.i18n import CATALOGUES
from app.services.conversation_service import ConversationService
from app.services.weather_service import (
    _WMO_CONDITIONS,
    OpenMeteoWeatherProvider,
    WeatherService,
    parse_open_meteo,
    wmo_condition,
)


def fake_response(days=3, codes=(0, 63, 45), rain=(0.0, 12.4, 0.0)):
    start = date.today()
    day_list = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    hours = [f"{d}T{h:02d}:00" for d in day_list for h in range(24)]
    return {
        "daily": {
            "time": day_list,
            "weather_code": list(codes[:days]),
            "temperature_2m_max": [29.4, 26.1, 24.8][:days],
            "temperature_2m_min": [14.2, 15.9, 12.0][:days],
            "precipitation_sum": list(rain[:days]),
            "wind_speed_10m_max": [9.0, 22.5, 7.1][:days],
        },
        "hourly": {"time": hours, "relative_humidity_2m": [50] * len(hours)},
    }


class Recorder:
    def __init__(self, status=200, body=None):
        self.calls, self.status, self.body = [], status, body

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if self.status != 200:
            return httpx.Response(self.status, json={"error": True, "reason": "test"})
        return httpx.Response(200, json=self.body or fake_response())


def provider(recorder, cache_minutes=60):
    return OpenMeteoWeatherProvider(cache_minutes=cache_minutes, http=httpx.Client(transport=httpx.MockTransport(recorder)))


def test_parse_open_meteo_daily_values():
    days = parse_open_meteo(fake_response())
    assert [d.condition for d in days] == ["sunny", "rain", "fog"]
    assert days[1].rain_mm == 12.4 and days[1].wind_kmh == 22.5
    assert days[0].temp_min_c == 14.2 and days[0].temp_max_c == 29.4
    assert days[0].humidity_pct == 50 and days[0].date == date.today()


def test_request_uses_district_coordinates():
    rec = Recorder()
    provider(rec).forecast("sukkur", 3)
    params = rec.calls[0].url.params
    assert params["latitude"] == "27.7052" and params["longitude"] == "68.8574"
    assert params["forecast_days"] == "3" and params["timezone"] == "Asia/Karachi"


def test_forecasts_are_cached():
    rec = Recorder()
    p = provider(rec)
    p.forecast("sukkur", 3)
    p.forecast("sukkur", 3)
    assert len(rec.calls) == 1
    p.forecast("ghotki", 3)
    assert len(rec.calls) == 2


def test_api_failure_returns_no_forecast():
    assert provider(Recorder(status=500)).forecast("sukkur", 3) == []


def test_api_failure_reuses_todays_cached_forecast():
    rec = Recorder()
    p = provider(rec, cache_minutes=0)  # always refresh
    first = p.forecast("sukkur", 3)
    rec.status = 503
    assert p.forecast("sukkur", 3) == first


def test_report_with_live_data_gives_rain_advice():
    report = WeatherService(provider(Recorder())).get_report("khairpur")
    assert report is not None and len(report.days) == 3
    assert "advice_rain" in report.advice_keys and "advice_wind" in report.advice_keys


def test_unknown_district_never_calls_the_api():
    rec = Recorder()
    assert WeatherService(provider(rec)).get_report("lahore") is None
    assert rec.calls == []


def test_every_condition_has_wording():
    codes = {*_WMO_CONDITIONS.values(), wmo_condition(None), wmo_condition(12345)}
    for lang, catalogue in CATALOGUES.items():
        missing = [c for c in codes if f"cond_{c}" not in catalogue]
        assert not missing, (lang, missing)


def test_farmer_is_told_when_weather_is_unavailable(db):
    service = WeatherService(provider(Recorder(status=500)))

    def say(**kw):
        kind = InboundKind.OPTION if kw.get("option_id") else InboundKind.TEXT
        msg = InboundMessage(channel="web", external_ref="weather-farmer", kind=kind, **kw)
        return ConversationService(db, weather=service).handle(msg)

    say(text="hi")
    say(option_id="lang:en")
    say(option_id="district:sukkur")
    say(option_id="consent:both")
    r = say(option_id="menu:weather")
    assert "not available" in r.messages[0].text
    assert [o.id for o in r.messages[0].options] == ["nav:home"]
