"""Custom integration to integrate glentronics with Home Assistant.

For more details about this integration, please refer to
https://github.com/theOrakle/glentronics
"""
from __future__ import annotations

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GlentronicsApiClient
from .coordinator import GlentronicsConfigEntry, GlentronicsDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: GlentronicsConfigEntry) -> bool:
    """Set up this integration using UI."""
    coordinator = GlentronicsDataUpdateCoordinator(
        hass,
        entry,
        GlentronicsApiClient(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        ),
    )
    # Raises ConfigEntryNotReady (retry) or ConfigEntryAuthFailed (reauth).
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GlentronicsConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
