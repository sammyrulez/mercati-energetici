"""Tests for MercatiGas."""
from datetime import date

import pytest
from aioresponses import aioresponses

from mercati_energetici import MercatiGas
from mercati_energetici.exceptions import MercatiEnergeticiRequestError
from conftest import (
    AUTH_OK,
    AUTH_URL,
    AUCTION_TRADING_DATA,
    CONTINUOUS_TRADING_DATA,
    REQUEST_URL,
    STORED_GAS_DATA,
    api_response,
    error_response,
)


class TestMercatiGas:
    async def test_get_continuous_trading_results(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(CONTINUOUS_TRADING_DATA))
            async with MercatiGas("u", "p") as client:
                result = await client.get_continuous_trading_results(
                    "MGP-2023-04-06", date(2023, 4, 5)
                )
        assert isinstance(result, list)
        assert len(result) == 1
        r = result[0]
        assert r["prodotto"] == "MGP-2023-04-06"
        assert r["data"] == 20230405
        assert set(r.keys()) == {
            "data", "mercato", "prodotto", "primoPrezzo", "ultimoPrezzo",
            "prezzoMinimo", "prezzoMassimo", "prezzoMedio", "prezzoControllo",
            "volumiMw", "volumiMwh",
        }

    async def test_get_continuous_trading_results_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MercatiGas("u", "p") as client:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await client.get_continuous_trading_results("NONEXISTENT")

    async def test_get_auction_trading_results(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(AUCTION_TRADING_DATA))
            async with MercatiGas("u", "p") as client:
                result = await client.get_auction_trading_results(
                    "MI-2023-04-05", date(2023, 4, 5)
                )
        assert isinstance(result, list)
        assert len(result) == 1
        r = result[0]
        assert r["prodotto"] == "MI-2023-04-05"
        assert set(r.keys()) == {
            "data", "mercato", "prodotto", "prezzo", "volumiMw", "volumiMwh",
            "acquistiTso", "venditeTso",
        }

    async def test_get_auction_trading_results_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MercatiGas("u", "p") as client:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await client.get_auction_trading_results("NONEXISTENT")

    async def test_get_stored_gas_trading_results(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(STORED_GAS_DATA))
            async with MercatiGas("u", "p") as client:
                result = await client.get_stored_gas_trading_results(
                    "Stogit", date(2023, 4, 5)
                )
        assert isinstance(result, list)
        assert len(result) == 1
        r = result[0]
        assert r["impresaStoccaggio"] == "Stogit"
        assert set(r.keys()) == {
            "data", "dataFlusso", "impresaStoccaggio", "tipologia",
            "prezzo", "volumi", "acquistiSrg", "venditeSrg",
        }

    async def test_get_stored_gas_mgs_prefix_stripped(self):
        """Company name with MGS- prefix is stripped before passing to API."""
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(STORED_GAS_DATA))
            async with MercatiGas("u", "p") as client:
                result = await client.get_stored_gas_trading_results(
                    "MGS-Stogit", date(2023, 4, 5)
                )
        assert result[0]["impresaStoccaggio"] == "Stogit"

    async def test_get_stored_gas_trading_results_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MercatiGas("u", "p") as client:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await client.get_stored_gas_trading_results("NONEXISTENT")
