"""Tests for MercatiAmbientali."""
from datetime import date

import pytest
from aioresponses import aioresponses

from mercati_energetici import MercatiAmbientali
from mercati_energetici.exceptions import MercatiEnergeticiRequestError
from conftest import (
    AUTH_OK,
    AUTH_URL,
    ENV_RESULTS_DATA,
    REQUEST_URL,
    api_response,
    error_response,
)


class TestMercatiAmbientali:
    async def test_get_trading_results(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(ENV_RESULTS_DATA))
            async with MercatiAmbientali("u", "p") as client:
                result = await client.get_trading_results("GO", date(2023, 3, 23))
        assert isinstance(result, list)
        assert len(result) == len(ENV_RESULTS_DATA)
        r = result[0]
        assert r["mercato"] == "GO"
        assert r["data"] == 20230323
        assert set(r.keys()) == {
            "data", "mercato", "tipologia", "periodo",
            "prezzoRiferimento", "prezzoMinimo", "prezzoMassimo", "volumi",
        }

    async def test_get_trading_results_string_date(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(ENV_RESULTS_DATA))
            async with MercatiAmbientali("u", "p") as client:
                result = await client.get_trading_results("GO", "20230323")
        assert result[0]["data"] == 20230323

    async def test_get_trading_results_tee(self):
        tee_data = [
            {
                "data": 20230328, "mercato": "TEE", "tipologia": "Tipo I",
                "periodo": "2022", "prezzoRiferimento": 265.0,
                "prezzoMinimo": 260.0, "prezzoMassimo": 270.0, "volumi": 29209.0,
            }
        ]
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(tee_data))
            async with MercatiAmbientali("u", "p") as client:
                result = await client.get_trading_results("TEE", date(2023, 3, 28))
        assert result[0]["mercato"] == "TEE"

    async def test_get_trading_results_request_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MercatiAmbientali("u", "p") as client:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await client.get_trading_results("NONEXISTENT")
