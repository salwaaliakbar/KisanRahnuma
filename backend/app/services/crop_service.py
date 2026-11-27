"""Crop rates, seasonal trend and expected price range.

JsonCropRateProvider serves dummy data now. Later, current rates can come from the
team's Google Sheet and expected ranges from a SARIMA/Prophet model behind the same interface.
"""
from dataclasses import dataclass
from typing import Protocol

from app.i18n import LocalizedText
from app.services.data_loader import load_json
from app.services.weather_service import District


@dataclass(frozen=True)
class Crop:
    id: str
    name: LocalizedText
    unit: LocalizedText


@dataclass(frozen=True)
class SeasonalTrend:
    summer_avg: float
    winter_avg: float
    note: LocalizedText


@dataclass(frozen=True)
class PriceRange:
    season: LocalizedText
    low: float
    high: float
    basis: LocalizedText


@dataclass(frozen=True)
class CropRateReport:
    crop: Crop
    district: District
    rate: float
    source: LocalizedText
    date: str
    trend: SeasonalTrend
    expected: PriceRange


class CropRateProvider(Protocol):
    def crops(self) -> list[Crop]: ...
    def districts(self) -> list[District]: ...
    def report(self, crop_id: str, district_id: str) -> CropRateReport | None: ...


class JsonCropRateProvider:
    def __init__(self, filename: str = "crop_rates.json") -> None:
        self._data = load_json(filename)

    def crops(self) -> list[Crop]:
        return [Crop(c["id"], c["name"], c["unit"]) for c in self._data["crops"]]

    def districts(self) -> list[District]:
        return [District(d["id"], d["name"]) for d in self._data["districts"]]

    def report(self, crop_id: str, district_id: str) -> CropRateReport | None:
        raw = next((c for c in self._data["crops"] if c["id"] == crop_id), None)
        district = next((d for d in self.districts() if d.id == district_id), None)
        if raw is None or district is None or district_id not in raw["rates"]:
            return None
        rate = raw["rates"][district_id]
        return CropRateReport(
            crop=Crop(raw["id"], raw["name"], raw["unit"]),
            district=district,
            rate=rate["rate"],
            source=rate["source"],
            date=rate["date"],
            trend=SeasonalTrend(**raw["trend"]),
            expected=PriceRange(**raw["expected"]),
        )


class CropService:
    def __init__(self, provider: CropRateProvider | None = None) -> None:
        self.provider = provider or JsonCropRateProvider()

    def crops(self) -> list[Crop]:
        return self.provider.crops()

    def districts(self) -> list[District]:
        return self.provider.districts()

    def get_crop(self, crop_id: str) -> Crop | None:
        return next((c for c in self.crops() if c.id == crop_id), None)

    def get_report(self, crop_id: str, district_id: str) -> CropRateReport | None:
        return self.provider.report(crop_id, district_id)
