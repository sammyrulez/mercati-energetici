"""Environmental Markets"""
from __future__ import annotations
from datetime import date

from .authenticated_markets import AuthenticatedMercatiEnergetici

_PLATFORM = "PublicMarketResults"


class MercatiAmbientali(AuthenticatedMercatiEnergetici):
    """
    Environmental market API wrapper.
    See [the GME website](https://www.mercatoelettrico.org/En/Mercati/TEE/CosaSonoTee.aspx)
    for an explanation of the markets.
    """

    async def get_trading_results(
        self, market: str, day: date | str = None
    ) -> list[dict]:
        """Get environmental market results.

        Args:
            market: The market segment, e.g. ``"GO"`` or ``"TEE"``.
            day: Date of the market. Default is today. A string in the format
                    ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries with environmental trading results.
        """
        date_str = self._handle_date(day)
        return await self.request_data(_PLATFORM, market, "ENV_Results", date_str, date_str)
