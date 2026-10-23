"""Tests for Glentronics setup, unload and entities."""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.glentronics.api import (
    GlentronicsApiClientAuthenticationError,
    GlentronicsApiClientCommunicationError,
)
from custom_components.glentronics.const import DOMAIN

from .conftest import PROXY, make_data


async def test_setup_and_unload(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """The entry loads, creates the device and entities, and unloads cleanly."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED

    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, PROXY), mock_config_entry.entry_id
    )
    assert device is not None
    assert device.name == "Basement"
    assert device.model == "Sump Pump Alarm"
    assert device.manufacturer == "Glentronics"
    assert device.sw_version == "12"

    assert hass.states.get("sensor.basement_voltage").state == "12.5"
    # PROBLEM-class rows are "on" when the vendor flag says not OK.
    assert hass.states.get("binary_sensor.basement_status").state == "off"
    assert hass.states.get("binary_sensor.basement_high_water").state == "on"
    # CONNECTIVITY-class rows follow the vendor flag directly.
    assert hass.states.get("binary_sensor.basement_wifi").state == "on"
    assert hass.states.get("sensor.basement_last_alarm").state.startswith("2026-10-20")

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_reload_when_proxies_change(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """A proxy appearing on the account triggers a reload so it gets entities."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    data = make_data()
    data["proxy-2"] = {**data[PROXY], "Proxy": "Garage"}
    mock_client.async_get_data.return_value = data
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=6))
    await hass.async_block_till_done()

    assert hass.states.get("sensor.garage_voltage") is not None


async def test_setup_retries_when_unreachable(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """A connection failure at setup is retried, not a hard error."""
    mock_client.async_get_data.side_effect = GlentronicsApiClientCommunicationError("down")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_starts_reauth_on_rejected_login(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """A rejected login starts a re-authentication flow."""
    mock_client.async_get_data.side_effect = GlentronicsApiClientAuthenticationError("bad")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    assert [f["context"]["source"] for f in flows] == ["reauth"]
