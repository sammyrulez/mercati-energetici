"""Test the electricity markets module."""
import os
import pytest, pytest_asyncio
from datetime import date
from mercati_energetici import MercatiElettrici, MGP
from mercati_energetici.exceptions import (
    MercatiEnergeticiZoneError,
    MercatiEnergeticiRequestError,
)

USERNAME = os.environ.get("GME_USERNAME", "")
PASSWORD = os.environ.get("GME_PASSWORD", "")


@pytest_asyncio.fixture
async def mercati_elettrici():
    async with MercatiElettrici(USERNAME, PASSWORD) as me:
        yield me

@pytest_asyncio.fixture
async def mgp():
    async with MGP(USERNAME, PASSWORD) as mgp:
        yield mgp


@pytest.mark.asyncio
class TestMercatiElettrici:
    async def test_prices(self, mercati_elettrici):
        prices = await mercati_elettrici.get_prices("MGP")
        assert prices is not None
        assert type(prices) is list
        assert len(prices) > 0
        for price in prices:
            assert type(price) is dict
            assert price["mercato"] == "MGP"
        data = await mercati_elettrici.get_prices("MGP", date(2023, 3, 2))
        assert data[0]["data"] == 20230302
        data = await mercati_elettrici.get_prices("MGP", "20230303")
        assert data[0]["data"] == 20230303
        with pytest.raises(MercatiEnergeticiRequestError):
            await mercati_elettrici.get_prices("NONEXISTENT")

    async def test_volumes(self, mercati_elettrici):
        volumes = await mercati_elettrici.get_volumes("MGP")
        assert volumes is not None
        assert type(volumes) is list
        assert len(volumes) > 0
        for volume in volumes:
            assert type(volume) is dict
            assert volume["mercato"] == "MGP"
        data = await mercati_elettrici.get_volumes("MGP", date(2023, 3, 2))
        assert data[0]["data"] == 20230302
        data = await mercati_elettrici.get_volumes("MGP", "20230303")
        assert data[0]["data"] == 20230303
        with pytest.raises(MercatiEnergeticiRequestError):
            await mercati_elettrici.get_volumes("NONEXISTENT")

    async def test_liquidity(self, mercati_elettrici):
        liquidity = await mercati_elettrici.get_liquidity()
        assert liquidity is not None
        assert type(liquidity) is list
        assert len(liquidity) >= 23 and len(liquidity) <= 25
        for hour in liquidity:
            assert type(hour) is dict
        data = await mercati_elettrici.get_liquidity(date(2023, 3, 2))
        assert data[0]["data"] == 20230302
        data = await mercati_elettrici.get_liquidity("20230303")
        assert data[0]["data"] == 20230303


@pytest.mark.asyncio
class TestMGP:
    async def test_prices(self, mgp):
        prices = await mgp.get_prices()
        assert prices is not None
        assert type(prices) is dict
        keys = set(prices.keys())
        assert (
            keys == set(range(24)) or keys == set(range(23)) or keys == set(range(25))
        )
        with pytest.raises(MercatiEnergeticiRequestError):
            await mgp.get_prices(date(2020, 1, 1))
        with pytest.raises(MercatiEnergeticiZoneError):
            await mgp.get_prices(zone="NONEXISTENT")

    async def test_volumes(self, mgp):
        volumes = await mgp.get_volumes()
        assert volumes is not None
        assert type(volumes) is tuple
        assert len(volumes) == 2
        bought, sold = volumes
        assert type(bought) is dict
        assert type(sold) is dict
        keys = set(bought.keys())
        assert (
            keys == set(range(24)) or keys == set(range(23)) or keys == set(range(25))
        )
        assert keys == set(sold.keys())
        with pytest.raises(MercatiEnergeticiRequestError):
            await mgp.get_volumes(date(2020, 1, 1))
        with pytest.raises(MercatiEnergeticiZoneError):
            await mgp.get_volumes(zone="NONEXISTENT")

    async def test_liquidity(self, mgp):
        liquidity = await mgp.get_liquidity()
        assert liquidity is not None
        assert type(liquidity) is dict
        keys = set(liquidity.keys())
        assert (
            keys == set(range(24)) or keys == set(range(23)) or keys == set(range(25))
        )
        with pytest.raises(MercatiEnergeticiRequestError):
            await mgp.get_liquidity(date(2020, 1, 1))
