"""Original SHERPA diagnostic entities using the installed transport."""
from homeassistant.exceptions import ConfigEntryNotReady
DOMAIN = "olimpia_sherpa"
async def async_setup_entry(hass, entry):
    source = hass.data.get("iletcomfort", {}).get(entry.data["source_entry"])
    if source is None:
        raise ConfigEntryNotReady("iLetComfort transport is not loaded")
    if source.sn8 != "171H120F":
        raise ConfigEntryNotReady("This integration requires model 171H120F")
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = source
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True
async def async_unload_entry(hass, entry):
    ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
