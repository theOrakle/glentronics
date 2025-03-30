"""Binary sensor platform for glentronics."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .coordinator import GlentronicsDataUpdateCoordinator
from .entity import GlentronicsEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="Alarm Status",
        translation_key="FieldStatusOK",
        name="Status",
        icon="mdi:water-pump",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Alarm Status (USB)",
        translation_key="FieldStatusOK",
        name="Status",
        icon="mdi:usb",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Alarm Status (Remote Terminals)",
        translation_key="FieldStatusOK",
        name="Remote Terminals",
        icon="mdi:chip",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Water Sensor Connection",
        translation_key="FieldStatusOK",
        name="High Water",
        icon="mdi:home-flood",
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    BinarySensorEntityDescription(
        key="High Water Detector Status",
        translation_key="FieldStatusOK",
        name="High Water",
        icon="mdi:home-flood",
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    BinarySensorEntityDescription(
        key="WiFi Module Status",
        translation_key="FieldStatusOK",
        name="WiFi",
        icon="mdi:wifi",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="Firmware Version (software is up to date)",
        translation_key="FieldStatusOK",
        name="Firmware",
        icon="mdi:update",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="Last Received Alarm from WiFi Module",
        translation_key="FieldStatusOK",
        name="Last Alarm",
        icon="mdi:alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    devices = []
    coordinator = hass.data[DOMAIN][entry.entry_id]
    for proxy in coordinator.data:
        water_alarm = coordinator.data[proxy].get("HasWaterAlarm")
        fields = coordinator.data[proxy].get("StatusFields")   
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
    async_add_devices(devices)


class GlentronicsBinarySensor(GlentronicsEntity, BinarySensorEntity):
    """glentronics binary_sensor class."""

    def __init__(
        self,
        coordinator: GlentronicsDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        proxy,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator,entity_description,proxy)
        self._attributes = {}
        self.entity_description = entity_description
        self.proxy = proxy

    @property
    def state_attributes(self):
        return self._attributes

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        status = None
        desc = self.entity_description
        fields = self.coordinator.data[self.proxy].get("StatusFields")
        for field in fields:
            if field.get("FieldLabel").find(desc.key) == 0:
                if field.get("FieldLabel").find("WiFi") == 0:
                    status = field.get(desc.translation_key)
                else:
                    status = not(field.get(desc.translation_key))
                self._attributes["Value"] = field.get("FieldValue")
                self._attributes["Detail"] = field.get("FieldDetailInfo")
                self._attributes["Warning"] = field.get("IsWarning")
        return status
