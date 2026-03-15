"""Sensor platform for glentronics."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import GlentronicsDataUpdateCoordinator
from .entity import GlentronicsEntity

TOP_LEVEL_SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key="SerialConnectionStatus",
        name="Serial Connection",
        icon="mdi:serial-port",
    ),
    SensorEntityDescription(
        key="ErrorString",
        name="System Status",
        icon="mdi:information-outline",
    ),
    SensorEntityDescription(
        key="WirelessModuleBatteryStatus",
        name="Wireless Module Battery",
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="Voltage",
        name="Voltage",
        icon="mdi:flash",
    ),
)

FIELD_SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key="Last Received Alarm from WiFi Module",
        name="Last Alarm",
        icon="mdi:alert",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    devices = []
    coordinator = hass.data[DOMAIN][entry.entry_id]
    for proxy, proxy_data in coordinator.data.items():
        for description in TOP_LEVEL_SENSOR_DESCRIPTIONS:
            if proxy_data.get(description.key) in (None, ""):
                continue
            devices.append(
                GlentronicsSensor(
                    coordinator=coordinator,
                    entity_description=description,
                    proxy=proxy,
                )
            )

        fields = proxy_data.get("StatusFields", [])
        for field in fields:
            for description in FIELD_SENSOR_DESCRIPTIONS:
                if description.key == field.get("FieldLabel"):
                    devices.append(
                        GlentronicsFieldSensor(
                            coordinator=coordinator,
                            entity_description=description,
                            proxy=proxy,
                        )
                    )
    async_add_devices(devices)


class GlentronicsSensor(GlentronicsEntity, SensorEntity):
    """glentronics sensor class."""

    def __init__(
        self,
        coordinator: GlentronicsDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        proxy,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description, proxy)
        self.entity_description = entity_description
        self.proxy = proxy

    @property
    def native_value(self):
        """Return the sensor value."""
        value = self.coordinator.data.get(self.proxy, {}).get(self.entity_description.key)
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            return _parse_datetime(value)
        return value


class GlentronicsFieldSensor(GlentronicsEntity, SensorEntity):
    """glentronics field-backed sensor class."""

    def __init__(
        self,
        coordinator: GlentronicsDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        proxy,
    ) -> None:
        """Initialize the field sensor class."""
        super().__init__(coordinator, entity_description, proxy)
        self._attributes = {}
        self.entity_description = entity_description
        self.proxy = proxy

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        return self._attributes

    @property
    def native_value(self):
        """Return the sensor value."""
        fields = self.coordinator.data.get(self.proxy, {}).get("StatusFields", [])
        for field in fields:
            if field.get("FieldLabel") != self.entity_description.key:
                continue
            self._attributes["Detail"] = field.get("FieldDetailInfo")
            self._attributes["Warning"] = field.get("IsWarning")
            return _parse_datetime(field.get("FieldValue"))
        return None


def _parse_datetime(value: str | None):
    """Parse a vendor timestamp into a timezone-aware datetime."""
    if not value:
        return None

    parsed = dt_util.parse_datetime(value)
    if parsed is not None:
        if parsed.tzinfo is None:
            return dt_util.as_local(parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE))
        return parsed

    try:
        parsed = datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        return value

    return dt_util.as_local(parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE))
