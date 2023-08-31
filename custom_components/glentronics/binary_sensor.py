import websockets
import aiohttp
import json
import pydash
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import CONF_USERNAME, CONF_PIN
from .const import DOMAIN, URL, _LOGGER, API_USERNAME, API_PASSWORD

async def async_setup_entry(hass, config, async_add_entities) -> None:
    creds = {
        "APIUsername": API_USERNAME,
        "APIPassword": API_PASSWORD,
        "ProxyID": config.data[CONF_PIN],
        "Username": config.data[CONF_USERNAME]
    }
    
    url = URL + "/Device/RetrieveProxyStatus"
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data=creds) as r:
            results = await r.json()
    device = []
    device.append(pydash.get(results,"Location"))
    device.append(pydash.get(results,"StatusList.0.ControlUnitType"))
    fields = pydash.get(results,"StatusFields")

    entities = []
    for idx, field in enumerate(fields):
        entities.append(GlentronicsSensor(hass, creds, device, field, idx))

    async_add_entities(entities)

class GlentronicsSensor(Entity):

    def parse_results(self,results):
        state = not pydash.get(results,f"{self.idx}.FieldStatusOK")
        if state:
            self._state="on"
        else:
            self._state = "off"
        self._attributes["Value"] = pydash.get(results,f"{self.idx}.FieldValue")
        self._attributes["Detail"] = pydash.get(results,f"{self.idx}.FieldDetailInfo")
        self._attributes["Warning"] = pydash.get(results,f"{self.idx}.IsWarning")

    def __init__(self,hass,creds,device,field, idx):
        self.creds = creds
        self.device = device[0]
        self.idx = idx
        self.field = field["FieldLabel"]
        self._state = None
        self._attributes = {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device[0])},
            manufacturer=DOMAIN,
            model=device[1],
            name=device[0].capitalize())

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.device}_{self.name}"

    @property
    def name(self):
        return f"{DOMAIN}_{self.field}"

    @property
    def icon(self):
        match self.field:
            case 'Alarm Status (USB)':
                return 'mdi:usb'
            case 'High Water Detector Status':
                return 'mdi:home-flood'
            case 'WiFi Module Status':
                return 'mdi:wifi'
            case 'Firmware Version (software is up to date)':
                return 'mdi:update'
            case 'Last Received Alarm from WiFi Module':
                return 'mdi:alert'
            case _:
                return 'mdi:pipe'

    @property
    def device_class(self):
        return BinarySensorDeviceClass.PROBLEM

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        return self._attributes

    async def async_update(self) -> None:
        try:
            url = URL + "/Device/RetrieveProxyStatus"
            async with aiohttp.ClientSession() as session:
                async with session.post(url,data=self.creds) as r:
                    results = await r.json()
        except:
            _LOGGER.error("Failed to communicate to the API")

        self.parse_results(pydash.get(results,"StatusFields"))
