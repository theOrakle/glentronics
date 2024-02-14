from __future__ import annotations

import aiohttp
import pydash
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_PIN, CONF_USERNAME, CONF_PASSWORD
from .exceptions import ApiException, AuthenticationError
from .const import DOMAIN, _LOGGER, LOGIN_URL, API_URL, API_USERNAME, API_PASSWORD

DATA_SCHEMA = vol.Schema(
  {
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str
  }
)

async def validate_input(hass: core.HomeAssistant, data):
    try:
        creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "email": data[CONF_USERNAME],
            "Password": data[CONF_PASSWORD]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(LOGIN_URL,data=creds) as r:
                status = r.status
    except:
        _LOGGER.error('Troubles talking to the API')
        raise ApiException()
    if status == 200:
        creds = {
            "APIUsername": API_USERNAME,
            "APIPassword": API_PASSWORD,
            "Username": data[CONF_USERNAME]
        }
        url = API_URL + "/Device/RetrieveWifiModules"
        async with aiohttp.ClientSession() as session:
            async with session.post(url,data=creds) as r:
                results = await r.json()
        data[CONF_PIN] = pydash.get(results,"0.ProxyID")
        return data
    else:
        raise AuthenticationError()

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=user_input[CONF_USERNAME], data=info)
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )   
