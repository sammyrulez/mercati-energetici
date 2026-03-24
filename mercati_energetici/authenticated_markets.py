"""AuthenticatedMercatiEnergetici — client for the GME authenticated API.

Endpoint: https://api.mercatoelettrico.org/request/api/v1/
Authentication: POST /Auth → JWT Bearer token
Data: POST /RequestData → base64-encoded zip containing data.json
"""
from __future__ import annotations

import base64
import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from aiohttp import ClientSession
from yarl import URL

from .exceptions import (
    MercatiEnergeticiAuthError,
    MercatiEnergeticiConnectionError,
    MercatiEnergeticiRequestError,
)

_API_HOST = "api.mercatoelettrico.org"
_BASE_PATH = "/request/api/v1"


@dataclass
class AuthenticatedMercatiEnergetici:
    """Client for the GME authenticated API (api.mercatoelettrico.org).

    Credentials (username and password) must be obtained by registering
    at https://api.mercatoelettrico.org/users/RegistrationForm/RegistrationRequest

    Usage::

        async with AuthenticatedMercatiEnergetici("myuser", "mypassword") as client:
            data = await client.request_data(
                platform="PublicMarketResults",
                segment="MGP",
                data_name="ME_ZonalVolumes",
                interval_start="20250501",
                interval_end="20250501",
            )
    """

    username: str
    password: str
    session: ClientSession | None = None
    _token: str | None = field(default=None, init=False, repr=False)
    _close_session: bool = field(default=False, init=False, repr=False)

    async def authenticate(self) -> None:
        """Obtain a JWT token from the /Auth endpoint.

        Raises:
            MercatiEnergeticiAuthError: If credentials are invalid.
            MercatiEnergeticiConnectionError: If the API is unreachable.
        """
        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        url = URL.build(scheme="https", host=_API_HOST, path=f"{_BASE_PATH}/Auth")
        response = await self.session.post(
            url,
            json={"Login": self.username, "Password": self.password},
            headers={"Content-Type": "application/json"},
        )

        if response.status == 502:
            raise MercatiEnergeticiConnectionError("The GME API is unreachable")

        response.raise_for_status()

        data = await response.json()
        if not data.get("success"):
            reason = data.get("reason", "unknown")
            raise MercatiEnergeticiAuthError(
                f"Authentication failed: {reason}"
            )

        self._token = data["token"]

    async def request_data(
        self,
        platform: str,
        segment: str,
        data_name: str,
        interval_start: str,
        interval_end: str,
        attributes: dict[str, Any] | None = None,
    ) -> Any:
        """Request market data from the /RequestData endpoint.

        Args:
            platform: Platform identifier, e.g. ``"PublicMarketResults"``.
            segment: Market segment, e.g. ``"MGP"``.
            data_name: Dataset name, e.g. ``"ME_ZonalVolumes"``.
            interval_start: Start date in ``YYYYMMDD`` format.
            interval_end: End date in ``YYYYMMDD`` format.
            attributes: Optional additional filter attributes.

        Returns:
            Parsed JSON content from the response zip archive.

        Raises:
            MercatiEnergeticiAuthError: If not authenticated.
            MercatiEnergeticiRequestError: If the API returns an error for the request.
            MercatiEnergeticiConnectionError: If the API is unreachable.
        """
        if self._token is None:
            raise MercatiEnergeticiAuthError(
                "Not authenticated. Call authenticate() first or use the async context manager."
            )

        url = URL.build(
            scheme="https", host=_API_HOST, path=f"{_BASE_PATH}/RequestData"
        )
        payload = {
            "platform": platform,
            "segment": segment,
            "dataName": data_name,
            "intervalStart": interval_start,
            "intervalEnd": interval_end,
            "attributes": attributes or {},
        }

        response = await self.session.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}",
            },
        )

        if response.status == 502:
            raise MercatiEnergeticiConnectionError("The GME API is unreachable")

        response.raise_for_status()

        data = await response.json()

        if data.get("resultRequest") is not None:
            raise MercatiEnergeticiRequestError(data["resultRequest"])

        raw = base64.b64decode(data["contentResponse"])
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            with zf.open("data.json") as f:
                return json.load(f)

    async def get_quotas(self) -> dict:
        """Retrieve current usage quotas for this user account.

        Returns:
            A dictionary with quota usage and limits.

        Raises:
            MercatiEnergeticiAuthError: If not authenticated.
            MercatiEnergeticiConnectionError: If the API is unreachable.
        """
        if self._token is None:
            raise MercatiEnergeticiAuthError(
                "Not authenticated. Call authenticate() first or use the async context manager."
            )

        url = URL.build(
            scheme="https", host=_API_HOST, path=f"{_BASE_PATH}/GetMyQuotas"
        )
        response = await self.session.get(
            url,
            headers={"Authorization": f"Bearer {self._token}"},
        )

        if response.status == 502:
            raise MercatiEnergeticiConnectionError("The GME API is unreachable")

        response.raise_for_status()
        return await response.json()

    def _handle_date(self, day: date | str | None) -> str:
        """Format a date to YYYYMMDD string.

        Args:
            day: A ``datetime.date`` object, a string in ``YYYYMMDD`` format,
                 or ``None`` (defaults to today).

        Returns:
            A string in ``YYYYMMDD`` format.
        """
        if day is None:
            day = date.today()
        elif isinstance(day, str):
            day = datetime.strptime(day, "%Y%m%d").date()
        elif not isinstance(day, date):
            raise TypeError(
                "day must be a datetime.date or a string in the format YYYYMMDD"
            )
        return day.strftime("%Y%m%d")

    async def close(self) -> None:
        """Close the underlying client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> AuthenticatedMercatiEnergetici:
        await self.authenticate()
        return self

    async def __aexit__(self, *_exc_info) -> None:
        await self.close()
