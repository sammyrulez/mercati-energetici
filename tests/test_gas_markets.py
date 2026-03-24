"""Test the gas markets module."""
import os
import pytest, pytest_asyncio
from datetime import date
from mercati_energetici import MercatiGas
from mercati_energetici.exceptions import (
    MercatiEnergeticiRequestError,
)

USERNAME = os.environ.get("GME_USERNAME", "")
PASSWORD = os.environ.get("GME_PASSWORD", "")


@pytest_asyncio.fixture
async def mercati_gas():
    async with MercatiGas(USERNAME, PASSWORD) as mg:
        yield mg


@pytest.mark.asyncio
class TestMercatiGas:
    async def test_continuous_trading_results(self, mercati_gas):
        results = await mercati_gas.get_continuous_trading_results(
            "MGP-2023-03-23", day=date(2023, 3, 22)
        )
        assert results is not None
        assert type(results) is list
        assert len(results) > 0
        for result in results:
            assert type(result) is dict
        with pytest.raises(MercatiEnergeticiRequestError):
            await mercati_gas.get_continuous_trading_results("NONEXISTENT")

    async def test_auction_trading_results(self, mercati_gas):
        results = await mercati_gas.get_auction_trading_results(
            "MGP-2023-03-24", day=date(2023, 3, 23)
        )
        assert results is not None
        assert type(results) is list
        assert len(results) > 0
        for result in results:
            assert type(result) is dict
        with pytest.raises(MercatiEnergeticiRequestError):
            await mercati_gas.get_auction_trading_results("NONEXISTENT")

    async def test_stored_gas_trading_results(self, mercati_gas):
        results = await mercati_gas.get_stored_gas_trading_results(
            "Stogit", day=date(2023, 3, 22)
        )
        assert results is not None
        assert type(results) is list
        assert len(results) > 0
        for result in results:
            assert type(result) is dict
        with pytest.raises(MercatiEnergeticiRequestError):
            await mercati_gas.get_stored_gas_trading_results("NONEXISTENT")
