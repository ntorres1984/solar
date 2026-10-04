"""Expose raw responses without claiming unvalidated temperature mappings."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from . import DOMAIN
async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SherpaRaw(c, entry, key) for key in ("status", "sensors")])
class SherpaRaw(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = "Resposta " + key
        self._attr_unique_id = entry.entry_id + "_" + key
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}, "name": "Olimpia Splendid SHERPA", "manufacturer": "Olimpia Splendid", "model": "171H120F"}
    @property
    def native_value(self):
        obj = (self.coordinator.data or {}).get(self.key)
        return len(obj.raw_body) if obj else None
    @property
    def extra_state_attributes(self):
        obj = (self.coordinator.data or {}).get(self.key)
        return {"raw_hex": obj.raw_body.hex(",") if obj else None, "control_validated": False, "temperature_mapping_validated": False}
