"""Shared fixtures for the Glentronics tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.glentronics.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"

PROXY = "proxy-1"


def make_data() -> dict:
    """Return a fresh sample payload (entities mutate nothing, but be safe)."""
    return {
        PROXY: {
            "Proxy": "Basement",
            "ControlUnitType": "Sump Pump Alarm",
            "FirmwareVersion": 12,
            "SerialConnectionStatus": "Connected",
            "ErrorString": "OK",
            "WirelessModuleBatteryStatus": "Good",
            "Voltage": "12.5",
            "StatusFields": [
                {
                    "FieldLabel": "Alarm Status",
                    "FieldValue": "OK",
                    "FieldStatusOK": True,
                    "FieldDetailInfo": "all good",
                    "IsWarning": False,
                },
                {
                    "FieldLabel": "Water Sensor Status",
                    "FieldValue": "HIGH",
                    "FieldStatusOK": False,
                    "FieldDetailInfo": "",
                    "IsWarning": True,
                },
                {
                    "FieldLabel": "WiFi Module Status",
                    "FieldValue": "Connected",
                    "FieldStatusOK": True,
                    "FieldDetailInfo": "",
                    "IsWarning": False,
                },
                {
                    "FieldLabel": "Last Received Alarm from WiFi Module",
                    "FieldValue": "10/20/2026 1:02:03 PM",
                    "FieldStatusOK": True,
                    "FieldDetailInfo": "",
                    "IsWarning": False,
                },
            ],
        }
    }


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow Home Assistant to load the custom integration under test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a Glentronics config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="user@example.com",
        unique_id="user@example.com",
        data={CONF_USERNAME: "user@example.com", CONF_PASSWORD: "secret"},
    )


@pytest.fixture
def mock_client() -> Generator[MagicMock]:
    """Patch the Glentronics API client everywhere it is constructed."""
    with (
        patch("custom_components.glentronics.GlentronicsApiClient", autospec=True) as client_cls,
        patch("custom_components.glentronics.config_flow.GlentronicsApiClient", new=client_cls),
    ):
        client = client_cls.return_value
        client.async_load_proxies = AsyncMock()
        client.async_get_data = AsyncMock(return_value=make_data())
        yield client
