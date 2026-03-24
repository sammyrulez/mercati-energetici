"""Tests for AuthenticatedMercatiEnergetici base class."""
from datetime import date

import pytest
from aioresponses import aioresponses

from mercati_energetici import AuthenticatedMercatiEnergetici
from mercati_energetici.exceptions import (
    MercatiEnergeticiAuthError,
    MercatiEnergeticiConnectionError,
)
from conftest import AUTH_FAIL, AUTH_OK, AUTH_URL, QUOTAS_DATA, QUOTAS_URL


class TestHandleDate:
    def test_date_object(self):
        client = AuthenticatedMercatiEnergetici("u", "p")
        assert client._handle_date(date(2020, 1, 1)) == "20200101"

    def test_date_string(self):
        client = AuthenticatedMercatiEnergetici("u", "p")
        assert client._handle_date("20210203") == "20210203"

    def test_none_returns_today(self):
        client = AuthenticatedMercatiEnergetici("u", "p")
        assert client._handle_date(None) == date.today().strftime("%Y%m%d")

    def test_invalid_string_format(self):
        client = AuthenticatedMercatiEnergetici("u", "p")
        with pytest.raises(ValueError):
            client._handle_date("2020-01-01")
        with pytest.raises(ValueError):
            client._handle_date("2020/01/01")

    def test_invalid_type(self):
        client = AuthenticatedMercatiEnergetici("u", "p")
        with pytest.raises(TypeError):
            client._handle_date(20200101)


class TestAuthentication:
    async def test_authenticate_success(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            client = AuthenticatedMercatiEnergetici("user", "pass")
            await client.authenticate()
            assert client._token == "test-token"
            await client.close()

    async def test_authenticate_failure(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_FAIL)
            client = AuthenticatedMercatiEnergetici("user", "wrong")
            with pytest.raises(MercatiEnergeticiAuthError):
                await client.authenticate()
            await client.close()

    async def test_authenticate_502(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, status=502)
            client = AuthenticatedMercatiEnergetici("user", "pass")
            with pytest.raises(MercatiEnergeticiConnectionError):
                await client.authenticate()
            await client.close()

    async def test_request_data_without_auth(self):
        client = AuthenticatedMercatiEnergetici("user", "pass")
        with pytest.raises(MercatiEnergeticiAuthError):
            await client.request_data("PublicMarketResults", "MGP", "ME_ZonalPrices", "20230328", "20230328")


class TestGetQuotas:
    async def test_get_quotas(self):
        with aioresponses() as mock:
            mock.post(AUTH_URL, payload=AUTH_OK)
            mock.get(QUOTAS_URL, payload=QUOTAS_DATA)
            async with AuthenticatedMercatiEnergetici("user", "pass") as client:
                quotas = await client.get_quotas()
        assert quotas == QUOTAS_DATA

    async def test_get_quotas_without_auth(self):
        client = AuthenticatedMercatiEnergetici("user", "pass")
        with pytest.raises(MercatiEnergeticiAuthError):
            await client.get_quotas()
