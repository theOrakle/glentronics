"""Binary sensor platform for glentronics."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import GlentronicsConfigEntry, GlentronicsDataUpdateCoordinator
from .entity import GlentronicsEntity

# Vendor field that carries each status row's OK/not-OK flag.
FIELD_STATUS_KEY = "FieldStatusOK"

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="Alarm Status",
        name="Status",
        icon="mdi:water-pump",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Alarm Status (USB)",
        name="Status",
        icon="mdi:usb",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Alarm Status (Remote Terminals)",
        name="Remote Terminals",
        icon="mdi:chip",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Water Sensor Connection",
        name="Water Sensor",
        icon="mdi:connection",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="Water Sensor Status",
        name="High Water",
        icon="mdi:home-flood",
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    BinarySensorEntityDescription(
        key="WiFi Module Status",
        name="WiFi",
        icon="mdi:wifi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="Firmware Version (software is up to date)",
        name="Firmware",
        icon="mdi:update",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Last Received Alarm from WiFi Module",
        name="Last Alarm",
        icon="mdi:alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GlentronicsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    devices = []
    coordinator = entry.runtime_data
    for proxy in coordinator.data:
        fields = coordinator.data[proxy].get("StatusFields", [])
        for f in fields:
            for e in ENTITY_DESCRIPTIONS:
                if e.key == f.get("FieldLabel"):
                    devices.append(
                        GlentronicsBinarySensor(
                            coordinator=coordinator,
                            entity_description=e,
                            proxy=proxy,
                        )
                    )
    async_add_entities(devices)


class GlentronicsBinarySensor(GlentronicsEntity, BinarySensorEntity):
    """glentronics binary_sensor class."""

    def __init__(
        self,
        coordinator: GlentronicsDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        proxy,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description, proxy)
        self._attributes = {}

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        status = False
        desc = self.entity_description
        fields = self.coordinator.data.get(self.proxy, {}).get("StatusFields", [])
        for field in fields:
            if field.get("FieldLabel") == desc.key:
                if desc.device_class == BinarySensorDeviceClass.CONNECTIVITY:
                    status = bool(field.get(FIELD_STATUS_KEY))
                else:
                    status = not bool(field.get(FIELD_STATUS_KEY))
                self._attributes["Value"] = field.get("FieldValue")
                self._attributes["Detail"] = field.get("FieldDetailInfo")
                self._attributes["Warning"] = field.get("IsWarning")
                break
        return status
