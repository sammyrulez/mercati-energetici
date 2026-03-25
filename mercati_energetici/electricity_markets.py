"""Electricity Markets"""
from __future__ import annotations
from datetime import date
from typing import Any

from .authenticated_markets import AuthenticatedMercatiEnergetici
from .exceptions import MercatiEnergeticiZoneError

_PLATFORM = "PublicMarketResults"


class MercatiElettrici(AuthenticatedMercatiEnergetici):
    """
    Electricity Markets API wrapper.
    See [the GME website](https://www.mercatoelettrico.org/En/Mercati/MercatoElettrico/IlMercatoElettrico.aspx)
    for an explanation of the markets.
    """

    async def get_prices(self, market: str, day: date | str | None = None) -> list[dict[str, Any]]:
        """Get electricity prices in €/MWh for a specific day on all the market zones.

        Args:
            market: The market segment, e.g. ``"MGP"``.
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries like: ``[{"FlowDate": "20230323",
                                            "Hour": "1",
                                            "Market": "MGP",
                                            "Zone": "CALA",
                                            "Price": "128.69",
                                            "Period": "0"}]``
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, market, "ME_ZonalPrices", date_str, date_str)

    async def get_volumes(self, market: str, day: date | str | None = None) -> list[dict[str, Any]]:
        """Get bought and sold volume for a specific day on all the market zones.

        Args:
            market: The market segment, e.g. ``"MGP"``.
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries like: ``[{"FlowDate": "20230323",
                                             "Hour": "1",
                                             "Market": "MGP",
                                             "Zone": "CALA",
                                             "Purchased": "482.198",
                                             "Sold": "1001.576",
                                             "Period": "0"}]``
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, market, "ME_ZonalVolumes", date_str, date_str)

    async def get_liquidity(self, day: date | str | None = None) -> list[dict[str, Any]]:
        """Get liquidity of electricity markets.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries like: ``[{"FlowDate": "20230323",
                                            "Hour": "1",
                                            "Liquidity": "74.47",
                                            "Period": "0"}]``
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, "MGP", "ME_Liquidity", date_str, date_str)


class MGP(MercatiElettrici):
    """
    Day-ahead Electricity Market.
    Higher-level interface over MercatiElettrici for the MGP market and the PUN price.
    Hours are in [0 -> 23].
    """

    async def get_prices(self, day: date | str | None = None, zone: str = "PUN") -> dict[int, float]:
        """Get electricity prices in €/MWh for a specific day and zone.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.
            zone: One of ``["CALA","CNOR","CSUD","NORD","PUN","SARD","SICI","SUD"]``.
                  Default is ``"PUN"`` (whole Italy).

        Returns:
            A ``dict[int, float]`` mapping hour (0–23) to price in €/MWh.
        """
        data = await super().get_prices("MGP", day)
        prices = {record["Zone"]: {} for record in data if "Zone" in record}
        for record in data:
            prices[record["Zone"]][int(record["Hour"]) - 1] = float(record["Price"])
        if zone not in prices.keys():
            raise MercatiEnergeticiZoneError(
                f"Zone '{zone}' not found. Available zones are: {list(prices.keys())}"
            )
        return prices[zone]

    async def daily_pun(self, day: date | str | None = None) -> float:
        """Get the average PUN price for a specific day.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            The PUN price in €/MWh.
        """
        prices = await self.get_prices(day, zone="PUN")
        hourly_pun = list(prices.values())
        return sum(hourly_pun) / len(hourly_pun)

    async def get_volumes(
        self, day: date | str | None = None, zone: str = "TOTALE"
    ) -> tuple[dict[int, float], dict[int, float]]:
        """Get bought and sold volume for a specific day and zone.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.
            zone: One of ``["CALA","CNOR","CSUD","NORD","SARD","SICI","SUD","TOTALE"]``.
                  Default is ``"TOTALE"`` (whole Italy).

        Returns:
            A tuple ``(bought, sold)`` where each is a ``dict[int, float]``
            mapping hour (0–23) to volume in MWh.
        """
        data = await super().get_volumes("MGP", day)
        bought = {record["Zone"]: {} for record in data if "Zone" in record}
        sold = {z: {} for z in bought}
        for record in data:
            bought[record["Zone"]][int(record["Hour"]) - 1] = float(record["Purchased"])
            sold[record["Zone"]][int(record["Hour"]) - 1] = float(record["Sold"])
        if zone not in bought.keys():
            raise MercatiEnergeticiZoneError(
                f"Zone '{zone}' not found. Available zones are: {list(bought.keys())}"
            )
        return bought[zone], sold[zone]

    async def get_liquidity(self, day: date | str | None = None) -> dict[int, float]:
        """Get liquidity of electricity markets.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A ``dict[int, float]`` mapping hour (0–23) to liquidity in %.
        """
        data = await super().get_liquidity(day)
        return {int(x["Hour"]) - 1: float(x["Liquidity"]) for x in data}
