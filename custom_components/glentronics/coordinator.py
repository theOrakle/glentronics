"""DataUpdateCoordinator for glentronics."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    GlentronicsApiClient,
    GlentronicsApiClientAuthenticationError,
    GlentronicsApiClientError,
)
from .const import DOMAIN, LOGGER

type GlentronicsConfigEntry = ConfigEntry[GlentronicsDataUpdateCoordinator]


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class GlentronicsDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching data from the API."""

    config_entry: GlentronicsConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: GlentronicsConfigEntry,
        client: GlentronicsApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Update data via library."""
        try:
            data = await self.client.async_get_data()
        except GlentronicsApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except GlentronicsApiClientError as exception:
            raise UpdateFailed(exception) from exception

        if self.data and set(self.data) != set(data):
            # A proxy was added or removed: reload so entities match the account.
            self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)

        return data
