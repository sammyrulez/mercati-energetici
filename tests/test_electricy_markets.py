"""Tests for MercatiElettrici and MGP."""
from datetime import date

import pytest
from aioresponses import aioresponses

from mercati_energetici import MGP, MercatiElettrici
from mercati_energetici.exceptions import (
    MercatiEnergeticiRequestError,
    MercatiEnergeticiZoneError,
)
from conftest import (
    AUTH_OK,
    AUTH_URL,
    REQUEST_URL,
    api_response,
    error_response,
    make_liquidity_data,
    make_prices_data,
    make_volumes_data,
)


class TestMercatiElettrici:
    async def test_get_prices(self):
        data = make_prices_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MercatiElettrici("u", "p") as client:
                result = await client.get_prices("MGP", "20230328")
        assert isinstance(result, list)
        assert len(result) == len(data)
        assert result[0]["mercato"] == "MGP"
        assert result[0]["data"] == 20230328
        assert set(result[0].keys()) == {"data", "ora", "mercato", "zona", "prezzo"}

    async def test_get_prices_request_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MercatiElettrici("u", "p") as client:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await client.get_prices("NONEXISTENT")

    async def test_get_volumes(self):
        data = make_volumes_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MercatiElettrici("u", "p") as client:
                result = await client.get_volumes("MGP", "20230328")
        assert isinstance(result, list)
        assert result[0]["mercato"] == "MGP"
        assert set(result[0].keys()) == {"data", "ora", "mercato", "zona", "acquisti", "vendite"}

    async def test_get_volumes_request_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MercatiElettrici("u", "p") as client:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await client.get_volumes("NONEXISTENT")

    async def test_get_liquidity(self):
        data = make_liquidity_data()
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MercatiElettrici("u", "p") as client:
                result = await client.get_liquidity("20230328")
        assert isinstance(result, list)
        assert len(result) == 24
        assert set(result[0].keys()) == {"data", "ora", "liquidita"}

    async def test_get_liquidity_default_date(self):
        data = make_liquidity_data(date_val=int(date.today().strftime("%Y%m%d")))
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MercatiElettrici("u", "p") as client:
                result = await client.get_liquidity()
        assert result[0]["data"] == int(date.today().strftime("%Y%m%d"))


class TestMGP:
    async def test_get_prices_pun(self):
        data = make_prices_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                prices = await mgp.get_prices()
        assert isinstance(prices, dict)
        assert set(prices.keys()) == set(range(24))
        # hour 0 = ora 1 → prezzo 101.0
        assert prices[0] == pytest.approx(101.0)

    async def test_get_prices_zone(self):
        data = make_prices_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                prices = await mgp.get_prices(zone="SUD")
        assert set(prices.keys()) == set(range(24))

    async def test_get_prices_zone_error(self):
        data = make_prices_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                with pytest.raises(MercatiEnergeticiZoneError):
                    await mgp.get_prices(zone="NONEXISTENT")

    async def test_get_prices_request_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MGP("u", "p") as mgp:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await mgp.get_prices(date(2020, 1, 1))

    async def test_daily_pun(self):
        data = make_prices_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                pun = await mgp.daily_pun("20230328")
        # PUN values are 101.0..124.0, average = 112.5
        assert pun == pytest.approx(112.5)

    async def test_get_volumes(self):
        data = make_volumes_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                bought, sold = await mgp.get_volumes()
        assert set(bought.keys()) == set(range(24))
        assert set(sold.keys()) == set(range(24))
        assert bought[0] == pytest.approx(501.0)
        assert sold[0] == pytest.approx(1001.0)

    async def test_get_volumes_zone(self):
        data = make_volumes_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                bought, sold = await mgp.get_volumes(zone="NORD")
        assert set(bought.keys()) == set(range(24))

    async def test_get_volumes_zone_error(self):
        data = make_volumes_data("MGP")
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                with pytest.raises(MercatiEnergeticiZoneError):
                    await mgp.get_volumes(zone="NONEXISTENT")

    async def test_get_volumes_request_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MGP("u", "p") as mgp:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await mgp.get_volumes(date(2020, 1, 1))

    async def test_get_liquidity(self):
        data = make_liquidity_data()
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=api_response(data))
            async with MGP("u", "p") as mgp:
                liquidity = await mgp.get_liquidity("20230328")
        assert isinstance(liquidity, dict)
        assert set(liquidity.keys()) == set(range(24))
        assert liquidity[0] == pytest.approx(74.47)

    async def test_get_liquidity_request_error(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.post(REQUEST_URL, payload=error_response())
            async with MGP("u", "p") as mgp:
                with pytest.raises(MercatiEnergeticiRequestError):
                    await mgp.get_liquidity(date(2020, 1, 1))
