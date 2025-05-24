"""Glentronics API Client."""
from __future__ import annotations

import asyncio
import socket

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
        self.proxies = []
        self.creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "ProxyID": None,
            "Username": username
        }

    async def async_load_proxies(self) -> any:
        """Get proxy from the API."""
        if self.proxies:
            return
        creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "email": self._username,
            "Password": self._password
        }
        async with async_timeout.timeout(10):
            response = await self._session.request(
                method="post",
                url="https://glentronicsconnect.com/ApiAccount/Login",
                json=creds,
            )
        if response.status == 400:
            raise GlentronicsApiClientAuthenticationError(
                "Invalid credentials",
            )
        modules = await self._api_wrapper(
            method="post", 
            url=f"{API_URL}/Device/RetrieveWifiModules",
            data=self.creds
        )
        for module in modules:
            self.proxies.append(module.get("ProxyID"))

    async def async_get_data(self) -> any:
        """Get data from the API."""
        data = {}
        await self.async_load_proxies()
        for proxy in self.proxies:
            self.creds["ProxyID"] = proxy
            details = await self._api_wrapper(
                method="post", 
                url=f"{API_URL}/Device/RetrieveProxyStatus",
                data=self.creds
            )
            data[proxy] = details.get("StatusList")[0]
            data[proxy]["StatusFields"] = details.get("StatusFields")
            data[proxy]["Proxy"] = details.get("Location")
        LOGGER.debug(data)
        return data

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
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
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise GlentronicsApiClientError(
                "Something really wrong happened!"
            ) from exception
