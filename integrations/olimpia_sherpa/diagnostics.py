"""Export only the bounded passive capture, without credentials or device IDs."""
from . import DOMAIN

async def async_get_config_entry_diagnostics(hass, entry):
    capture = hass.data[DOMAIN + "_capture"][entry.entry_id][0]
    return capture.snapshot()
