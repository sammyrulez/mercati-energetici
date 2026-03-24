"""Electricity Markets"""
from __future__ import annotations
from datetime import date

from .authenticated_markets import AuthenticatedMercatiEnergetici
from .exceptions import MercatiEnergeticiZoneError

_PLATFORM = "PublicMarketResults"


class MercatiElettrici(AuthenticatedMercatiEnergetici):
    """
    Electricity Markets API wrapper.
    See [the GME website](https://www.mercatoelettrico.org/En/Mercati/MercatoElettrico/IlMercatoElettrico.aspx)
    for an explanation of the markets.
    """

    async def get_prices(self, market: str, day: date | str = None) -> list[dict]:
        """Get electricity prices in €/MWh for a specific day on all the market zones.

        Args:
            market: The market segment, e.g. ``"MGP"``.
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries like: ``[{"data": 20230323,
                                            "ora": 1,
                                            "mercato": "MGP",
                                            "zona": "CALA",
                                            "prezzo": 128.69}]``
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, market, "ME_ZonalPrices", date_str, date_str)

    async def get_volumes(self, market: str, day: date | str = None) -> list[dict]:
        """Get bought and sold volume for a specific day on all the market zones.

        Args:
            market: The market segment, e.g. ``"MGP"``.
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries like: ``[{"data": 20230323,
                                             "ora": 1,
                                             "mercato": "MGP",
                                             "zona": "CALA",
                                             "acquisti": 482.198,
                                             "vendite": 1001.576}]``
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, market, "ME_ZonalVolumes", date_str, date_str)

    async def get_liquidity(self, day: date | str = None) -> list[dict]:
        """Get liquidity of electricity markets.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries like: ``[{"data": 20230323,
                                            "ora": 1,
                                            "liquidita": 74.47}]``
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, "MGP", "ME_Liquidity", date_str, date_str)


class MGP(MercatiElettrici):
    """
    Day-ahead Electricity Market.
    Higher-level interface over MercatiElettrici for the MGP market and the PUN price.
    Hours are in [0 -> 23].
    """

    async def get_prices(self, day: date | str = None, zone: str = "PUN") -> dict:
        """Get electricity prices in €/MWh for a specific day and zone.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.
            zone: One of ``["CALA","CNOR","CSUD","NORD","PUN","SARD","SICI","SUD"]``.
                  Default is ``"PUN"`` (whole Italy).

        Returns:
            A dictionary like: ``{hour: price_per_MWh}``
        """
        data = await super().get_prices("MGP", day)
        prices = {record["zona"]: {} for record in data if "zona" in record}
        for record in data:
            prices[record["zona"]][record["ora"] - 1] = record["prezzo"]
        if zone not in prices.keys():
            raise MercatiEnergeticiZoneError(
                f"Zone '{zone}' not found. Available zones are: {list(prices.keys())}"
            )
        return prices[zone]

    async def daily_pun(self, day: date | str = None) -> float:
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
        self, day: date | str = None, zone: str = "Totale"
    ) -> tuple[dict, dict]:
        """Get bought and sold volume for a specific day and zone.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.
            zone: One of ``["CALA","CNOR","CSUD","NORD","SARD","SICI","SUD","Totale"]``.
                  Default is ``"Totale"`` (whole Italy).

        Returns:
            Two dictionaries like: ``{hour: MWh}`` for bought and sold volumes.
        """
        data = await super().get_volumes("MGP", day)
        bought = {record["zona"]: {} for record in data if "zona" in record}
        sold = {zone: {} for zone in bought}
        for record in data:
            bought[record["zona"]][record["ora"] - 1] = record["acquisti"]
            sold[record["zona"]][record["ora"] - 1] = record["vendite"]
        if zone not in bought.keys():
            raise MercatiEnergeticiZoneError(
                f"Zone '{zone}' not found. Available zones are: {list(bought.keys())}"
            )
        return bought[zone], sold[zone]

    async def get_liquidity(self, day: date | str = None) -> dict:
        """Get liquidity of electricity markets.

        Args:
            day: Date to query. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A dictionary like: ``{hour: liquidity}``.
        """
        data = await super().get_liquidity(day)
        return {x["ora"] - 1: x["liquidita"] for x in data}
