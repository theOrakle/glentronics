"""GlentronicsEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION
from .coordinator import GlentronicsDataUpdateCoordinator

class GlentronicsEntity(CoordinatorEntity):
    """GlentronicsEntity class."""

    def __init__(
        self, 
        coordinator: GlentronicsDataUpdateCoordinator,
        entity_description,
        proxy,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        proxy_data = coordinator.data.get(proxy, {})
        self._attr_unique_id = f"{DOMAIN}_{proxy}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, proxy)},
            name=proxy_data.get("Proxy"),
            model=proxy_data.get("ControlUnitType"),
            manufacturer=DOMAIN.capitalize(),
            sw_version=proxy_data.get("FirmwareVersion"),
        )
