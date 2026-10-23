"""Tests for the Glentronics config flow."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.glentronics.api import (
    GlentronicsApiClientAuthenticationError,
    GlentronicsApiClientCommunicationError,
    GlentronicsApiClientError,
)
from custom_components.glentronics.const import DOMAIN

USER_INPUT = {CONF_USERNAME: " User@Example.com ", CONF_PASSWORD: "secret"}
ERRORS = [
    (GlentronicsApiClientAuthenticationError("bad"), "invalid_auth"),
    (GlentronicsApiClientCommunicationError("down"), "cannot_connect"),
    (GlentronicsApiClientError("boom"), "unknown"),
]


async def test_user_flow_creates_entry(hass: HomeAssistant, mock_client: MagicMock) -> None:
    """A valid login creates an entry keyed by the lower-cased username."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "User@Example.com"
    assert result["data"] == {
        CONF_USERNAME: "User@Example.com",
        CONF_PASSWORD: "secret",
    }
    assert result["result"].unique_id == "user@example.com"


@pytest.mark.parametrize(("exception", "error"), ERRORS)
async def test_user_flow_errors_recover(
    hass: HomeAssistant, mock_client: MagicMock, exception: Exception, error: str
) -> None:
    """Each failure shows its error and the flow can still finish afterwards."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    mock_client.async_load_proxies.side_effect = exception
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    mock_client.async_load_proxies.side_effect = None
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_duplicate_aborts(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """The same account cannot be added twice."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow_updates_password(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """Re-authentication stores the new password and reloads."""
    mock_config_entry.add_to_hass(hass)
    result = await mock_config_entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_PASSWORD: "new-secret"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_PASSWORD] == "new-secret"


@pytest.mark.parametrize(("exception", "error"), ERRORS)
async def test_reauth_flow_errors_recover(
    hass: HomeAssistant,
    mock_client: MagicMock,
    mock_config_entry: MockConfigEntry,
    exception: Exception,
    error: str,
) -> None:
    """A failed re-authentication shows the error and can be retried."""
    mock_config_entry.add_to_hass(hass)
    result = await mock_config_entry.start_reauth_flow(hass)
    mock_client.async_load_proxies.side_effect = exception
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_PASSWORD: "x"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    mock_client.async_load_proxies.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_PASSWORD: "good"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
