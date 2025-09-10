from __future__ import annotations

from datetime import date
from typing import List, Dict

import httpx


async def fetch_open_meteo_daily(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
) -> List[Dict]:
    """Fetch daily climate summaries from Open-Meteo (no API key required).

    Returns list of records with columns: ds, tmax, tmin, precipitation.
    """
    base = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
        ],
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(base, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    times = daily.get("time", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])

    records: List[Dict] = []
    for i in range(len(times)):
        # Garantir que os valores sejam numéricos válidos, usando 0 como fallback
        tmax_val = tmax[i] if tmax and i < len(tmax) else 0
        tmin_val = tmin[i] if tmin and i < len(tmin) else 0
        precip_val = precip[i] if precip and i < len(precip) else 0

        try:
            tmax_float = float(tmax_val) if tmax_val is not None else 0.0
            tmin_float = float(tmin_val) if tmin_val is not None else 0.0
            precip_float = float(precip_val) if precip_val is not None else 0.0
        except (ValueError, TypeError):
            tmax_float = 0.0
            tmin_float = 0.0
            precip_float = 0.0

        records.append(
            {
                "ds": str(times[i]),
                "tmax": tmax_float,
                "tmin": tmin_float,
                "precip": precip_float,
            }
        )
    return records
