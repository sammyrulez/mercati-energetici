"""Gas Markets"""
from __future__ import annotations
from datetime import date
from typing import Any

from .authenticated_markets import AuthenticatedMercatiEnergetici

_PLATFORM = "PublicMarketResults"


class MercatiGas(AuthenticatedMercatiEnergetici):
    """
    Gas markets API wrapper.
    See [the GME website](https://www.mercatoelettrico.org/en/Mercati/MGAS/MGas.aspx)
    for an explanation of the markets.
    """

    async def get_continuous_trading_results(
        self, product: str, day: date | str | None = None
    ) -> list[dict[str, Any]]:
        """Get gas market results on the continuous trading mode.

        Args:
            product: The product identifier, e.g. ``"MGP-2023-03-23"``.
            day: Date of the market negotiation. Default is today. A string in
                    the format ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries with continuous trading results.
        """
        date_str = self._handle_date(day)
        return await self.request_data(
            _PLATFORM, "MGAS_C", "GAS_ContinuousTrading", date_str, date_str,
            {"Product": product},
        )

    async def get_auction_trading_results(
        self, product: str, day: date | str | None = None
    ) -> list[dict[str, Any]]:
        """Get gas market results on the auction mode.

        Args:
            product: The product identifier, e.g. ``"MGP-2023-03-24"``.
            day: Date of the market negotiations. Default is today. A string in
                    the format ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries with auction trading results.
        """
        date_str = self._handle_date(day)
        return await self.request_data(
            _PLATFORM, "MGAS_A", "GAS_MGASAuctionResults", date_str, date_str,
            {"Product": product},
        )

    async def get_stored_gas_trading_results(
        self, company: str, day: date | str | None = None
    ) -> list[dict[str, Any]]:
        """Get gas market results for the stored gas.

        Args:
            company: The storage company identifier, e.g. ``"Stogit"`` or ``"MGS-Stogit"``.
            day: Date of the market negotiations. Default is today. A string in
                    the format ``"YYYYMMDD"`` or a ``datetime.date`` object.

        Returns:
            A list of dictionaries with stored gas trading results.
        """
        date_str = self._handle_date(day)
        return await self.request_data(
            _PLATFORM, "MGS", "GAS_MGSAuctionResults", date_str, date_str,
            {"Company": company.replace("MGS-", "")},
        )
