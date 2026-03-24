"""Test the environmental markets module."""
import os
import pytest, pytest_asyncio
from datetime import date
from mercati_energetici import MercatiAmbientali
from mercati_energetici.exceptions import (
    MercatiEnergeticiRequestError,
)

USERNAME = os.environ.get("GME_USERNAME", "")
PASSWORD = os.environ.get("GME_PASSWORD", "")


@pytest_asyncio.fixture
async def mercati_ambientali():
    async with MercatiAmbientali(USERNAME, PASSWORD) as ma:
        yield ma


@pytest.mark.asyncio
class TestMercatiAmbientali:
    async def test_trading_results(self, mercati_ambientali):
        results = await mercati_ambientali.get_trading_results("GO", day=date(2023, 3, 23))
        assert results is not None
        assert type(results) is list
        assert len(results) > 0
        for res in results:
            assert type(res) is dict
        data = await mercati_ambientali.get_trading_results("GO", date(2023, 3, 2))
        assert data[0]["data"] == 20230302
        data = await mercati_ambientali.get_trading_results("GO", "20230303")
        assert data[0]["data"] == 20230303
        with pytest.raises(MercatiEnergeticiRequestError):
            await mercati_ambientali.get_trading_results("NONEXISTENT")
