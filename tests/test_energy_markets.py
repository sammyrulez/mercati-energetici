"""Test the authenticated markets base class utilities."""
import os
import pytest, pytest_asyncio
from datetime import date
from mercati_energetici.authenticated_markets import AuthenticatedMercatiEnergetici

USERNAME = os.environ.get("GME_USERNAME", "")
PASSWORD = os.environ.get("GME_PASSWORD", "")


@pytest_asyncio.fixture
async def client():
    async with AuthenticatedMercatiEnergetici(USERNAME, PASSWORD) as c:
        yield c


@pytest.mark.asyncio
class TestAuthenticatedMercatiEnergetici:
    async def test_handle_date(self, client):
        assert client._handle_date(date(2020, 1, 1)) == "20200101"
        assert client._handle_date("20210203") == "20210203"
        assert client._handle_date(None) == date.today().strftime("%Y%m%d")
        with pytest.raises(ValueError):
            client._handle_date("2020-01-01")
        with pytest.raises(ValueError):
            client._handle_date("2020/01/01")
        with pytest.raises(TypeError):
            client._handle_date(20200101)

    async def test_get_quotas(self, client):
        quotas = await client.get_quotas()
        assert quotas is not None
        assert type(quotas) is dict
