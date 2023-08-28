"""Constants for the Glentronics online component."""
import logging

from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = "glentronics"

ICON = 'mdi:pipe'

HOST = "api.glentronicsconnect.com"
URL = f"https://{HOST}"
API_USERNAME = "Glentronics"
API_PASSWORD = "API201622@"

PLATFORMS = [Platform.BINARY_SENSOR]
