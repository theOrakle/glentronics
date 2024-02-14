import pydash
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from .const import DOMAIN, _LOGGER, BINARY_SENSORS

async def async_setup_entry(hass, config, async_add_entities):
    coordinator = hass.data[DOMAIN][config.entry_id]
    entities = []
    for field in BINARY_SENSORS:
        entities.append(MySensor(coordinator, field, BINARY_SENSORS[field]))
    async_add_entities(entities)

class MySensor(Entity):
    def __init__(self,coordinator,idx,entity):
        self.coordinator = coordinator
        self.entity = entity
        self.idx = idx
        self.device = self.coordinator.name
        self.field = entity.name
        self._icon = entity.icon
        self._device_class = entity.device_class
        self._state = None
        self._attributes = {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device)},
            manufacturer=DOMAIN,
            model=pydash.get(self.coordinator.device,"ControlUnitType"),
            sw_version=pydash.get(self.coordinator.device,"FirmwareVersion"),
            name=self.device.capitalize())

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.device}_{self.field}"

    @property
    def name(self):
        return f"{self.device}_{self.field}"

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        return self._device_class

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        return self._attributes

    async def async_update(self) -> None:
        for field in self.coordinator.fields: 
            if pydash.get(field,"FieldLabel").find(self.idx) == 0:
                state = pydash.get(field,"FieldStatusOK")
                self._attributes["Value"] = pydash.get(field,"FieldValue")
                self._attributes["Detail"] = pydash.get(field,"FieldDetailInfo")
                self._attributes["Warning"] = pydash.get(field,"IsWarning")
        if bool(state): 
            if not self.field.find("WiFi") == 0:
                self._state = "off"
            else:
                self._state = "on"
        else:
            self._state = "off"
