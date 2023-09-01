"""Constants for the Glentronics online component."""
import logging

from homeassistant.const import Platform
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntityDescription

_LOGGER = logging.getLogger(__name__)

DOMAIN = "glentronics"

ICON = 'mdi:pipe'

HOST = "api.glentronicsconnect.com"
URL = f"https://{HOST}"
API_USERNAME = "Glentronics"
API_PASSWORD = "API201622@"

PLATFORMS = [Platform.BINARY_SENSOR]
BINARY_SENSORS = {
    "Alarm Status": BinarySensorEntityDescription(
        name="Status",
        icon="mdi:usb",
        key="FieldValue",
        device_class=BinarySensorDeviceClass.PROBLEM),
    "High Water Detector Status": BinarySensorEntityDescription(
        name="High Water",
        icon="mdi:home-flood",
        key="FieldValue",
        device_class=BinarySensorDeviceClass.MOISTURE),
    "WiFi Module Status": BinarySensorEntityDescription(
        name="WiFi",
        icon="mdi:wifi",
        key="FieldValue",
        device_class=BinarySensorDeviceClass.CONNECTIVITY),
    "Firmware Version": BinarySensorEntityDescription(
        name="Firmware",
        icon="mdi:update",
        key="FieldValue",
        device_class=BinarySensorDeviceClass.UPDATE),
    "Last Received Alarm from WiFi Module": BinarySensorEntityDescription(
        name="Last Alarm",
        icon="mdi:alert",
        key="FieldValue",
        device_class=BinarySensorDeviceClass.PROBLEM)
}
