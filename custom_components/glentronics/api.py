"""Glentronics API Client."""
from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp
import async_timeout

from .const import LOGGER

API_URL = "https://api.glentronicsconnect.com"
API_USERNAME = "Glentronics"
API_PASSWORD = "API201622@"


class GlentronicsApiClientError(Exception):
    """Exception to indicate a general API error."""


class GlentronicsApiClientCommunicationError(
    GlentronicsApiClientError
):
    """Exception to indicate a communication error."""


class GlentronicsApiClientAuthenticationError(
    GlentronicsApiClientError
):
    """Exception to indicate an authentication error."""


class GlentronicsApiClient:
    """Glentronics API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Glentronics API Client."""
        self._username = username
        self._password = password
        self._session = session
        self.proxies: list[str] = []
        self._base_creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "Username": username
        }

    async def async_load_proxies(self) -> None:
        """Get proxy from the API."""
        creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "email": self._username,
            "Password": self._password
        }
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method="post",
                    url="https://glentronicsconnect.com/ApiAccount/Login",
                    json=creds,
                )
            if response.status in (400, 401, 403):
                raise GlentronicsApiClientAuthenticationError(
                    "Invalid credentials",
                )
            response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise GlentronicsApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise GlentronicsApiClientCommunicationError(
                f"Error fetching information: {type(exception).__name__}: {exception}",
            ) from exception
        modules = await self._api_wrapper(
            method="post",
            url=f"{API_URL}/Device/RetrieveWifiModules",
            data={
                **self._base_creds,
                "ProxyID": None,
            },
        )
        proxies: list[str] = []
        for module in modules:
            if not isinstance(module, dict):
                continue
            proxy_id = module.get("ProxyID")
            if proxy_id is None:
                continue
            if proxy_id not in proxies:
                proxies.append(proxy_id)
        self.proxies = proxies

    async def async_get_data(self) -> dict[Any, dict[str, Any]]:
        """Get data from the API."""
        data: dict[Any, dict[str, Any]] = {}
        await self.async_load_proxies()
        for proxy in self.proxies:
            details = await self._api_wrapper(
                method="post",
                url=f"{API_URL}/Device/RetrieveProxyStatus",
                data={
                    **self._base_creds,
                    "ProxyID": proxy,
                },
            )
            status_list = details.get("StatusList", [])
            if not isinstance(status_list, list) or not status_list:
                continue
            status_entry = status_list[0]
            if not isinstance(status_entry, dict):
                continue
            data[proxy] = status_entry
            data[proxy]["StatusFields"] = details.get("StatusFields", [])
            data[proxy]["Proxy"] = details.get("Location")
        LOGGER.debug(data)
        return data

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        auth_error_codes: tuple[int, ...] = (401, 403),
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in auth_error_codes:
                    raise GlentronicsApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise GlentronicsApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise GlentronicsApiClientCommunicationError(
                f"Error fetching information: {type(exception).__name__}: {exception}",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise GlentronicsApiClientError(
                f"Unexpected error fetching information: {type(exception).__name__}"
            ) from exception
