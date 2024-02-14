from __future__ import annotations

import aiohttp
import json
import pydash
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator, 
    UpdateFailed
)
from homeassistant.const import CONF_USERNAME, CONF_PIN
from .const import DOMAIN, _LOGGER, UPDATE_FREQ, API_URL, API_USERNAME, API_PASSWORD

class MyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        self.creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "ProxyID": config.data[CONF_PIN],
            "Username": config.data[CONF_USERNAME]
        }
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_FREQ)
        )

    async def _async_update_data(self):
        try:
            url = API_URL + "/Device/RetrieveProxyStatus"
            async with aiohttp.ClientSession() as session:
                async with session.post(url,data=self.creds) as r:
                    results = await r.json()
            self.name = pydash.get(results,"Location")
            self.device = pydash.get(results,"StatusList.0")
            self.fields = pydash.get(results,"StatusFields")
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(err)
