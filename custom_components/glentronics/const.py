"""Constants for glentronics."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "glentronics"

# Vendor-issued shared API credentials required by the Glentronics auth protocol.
# These are fixed by Glentronics and identical for all users of the service.
GLENTRONICS_API_USERNAME = "Glentronics"
GLENTRONICS_API_PASSWORD = "API201622@"
