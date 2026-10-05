"""SHERPA diagnostic responses and experimentally confirmed target reading."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from . import DOMAIN
from .decoder import decode_status

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SherpaRaw(coordinator, entry, key) for key in ("status", "sensors")]
                       + [SherpaTarget(coordinator, entry),
                          SherpaCapture(coordinator, entry, hass.data[DOMAIN + "_capture"][entry.entry_id][0])])

class SherpaCapture(SensorEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Mensagens recebidas"
    _attr_should_poll = False
    def __init__(self, coordinator, entry, capture):
        self.capture = capture
        self._attr_unique_id = entry.entry_id + "_capture_count"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.capture.listeners.add(self.async_write_ha_state)
        self.async_on_remove(lambda: self.capture.listeners.discard(self.async_write_ha_state))
    @property
    def native_value(self):
        return self.capture.count
    @property
    def extra_state_attributes(self):
        snapshot = self.capture.snapshot()
        snapshot.pop("frames")
        return snapshot

class SherpaBase(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)},
                                 "name": "Olimpia Splendid SHERPA",
                                 "manufacturer": "Olimpia Splendid", "model": "171H120F"}
    @property
    def reading(self):
        status = (self.coordinator.data or {}).get("status")
        return decode_status(status.raw_body, self.coordinator.sn8) if status else None

class SherpaRaw(SherpaBase):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator, entry)
        self.key = key
        self._attr_name = "Resposta " + key
        self._attr_unique_id = entry.entry_id + "_" + key
    @property
    def native_value(self):
        obj = (self.coordinator.data or {}).get(self.key)
        return len(obj.raw_body) if obj else None
    @property
    def extra_state_attributes(self):
        obj = (self.coordinator.data or {}).get(self.key)
        reading = self.reading
        return {"raw_hex": obj.raw_body.hex(",") if obj else None,
                "control_validated": False,
                "temperature_mapping_validated": reading is not None if self.key == "status" else False,
                "activity_signal": reading.activity_signal if reading and self.key == "status" else None,
                "persistent_power_validated": False}

class SherpaTarget(SherpaBase):
    _attr_name = "Temperatura definida de climatização"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = entry.entry_id + "_climate_target"
    @property
    def available(self):
        return super().available and self.reading is not None
    @property
    def native_value(self):
        reading = self.reading
        return reading.target_temperature if reading else None
