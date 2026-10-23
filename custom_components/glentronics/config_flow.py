"""Adds config flow for Glentronics."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    GlentronicsApiClient,
    GlentronicsApiClientAuthenticationError,
    GlentronicsApiClientCommunicationError,
    GlentronicsApiClientError,
)
from .const import DOMAIN, LOGGER


class GlentronicsFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Glentronics."""

    VERSION = 1

    async def _validate(self, username: str, password: str) -> str | None:
        """Test the login and return a flow error key, or None when it works."""
        try:
            await self._test_credentials(username=username, password=password)
        except GlentronicsApiClientAuthenticationError as exception:
            LOGGER.warning(exception)
            return "invalid_auth"
        except GlentronicsApiClientCommunicationError as exception:
            LOGGER.error(exception)
            return "cannot_connect"
        except GlentronicsApiClientError as exception:
            LOGGER.exception(exception)
            return "unknown"
        return None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            if error := await self._validate(username, user_input[CONF_PASSWORD]):
                errors["base"] = error
            else:
                await self.async_set_unique_id(username.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=username,
                    data={
                        **user_input,
                        CONF_USERNAME: username,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start re-authentication after Glentronics rejected the stored login."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the account password again."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()
        if user_input is not None:
            if error := await self._validate(
                reauth_entry.data[CONF_USERNAME], user_input[CONF_PASSWORD]
            ):
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            description_placeholders={"username": reauth_entry.data[CONF_USERNAME]},
            errors=errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        client = GlentronicsApiClient(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_load_proxies()
