"""GlentronicsEntity class."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GlentronicsDataUpdateCoordinator


class GlentronicsEntity(CoordinatorEntity[GlentronicsDataUpdateCoordinator]):
    """Base class for Glentronics entities (one device per proxy)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GlentronicsDataUpdateCoordinator,
        entity_description: EntityDescription,
        proxy: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.proxy = proxy
        proxy_data = coordinator.data.get(proxy, {})
        self._attr_unique_id = f"{DOMAIN}_{proxy}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, proxy)},
            name=proxy_data.get("Proxy"),
            model=proxy_data.get("ControlUnitType"),
            manufacturer="Glentronics",
            sw_version=str(v) if (v := proxy_data.get("FirmwareVersion")) is not None else None,
        )
