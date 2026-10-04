"""Select an existing transport; no second login or pump commands."""
import voluptuous as vol
from homeassistant import config_entries
from . import DOMAIN
class SherpaFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        sources = {e.entry_id: e.title for e in self.hass.config_entries.async_entries("iletcomfort")
                   if getattr(self.hass.data.get("iletcomfort", {}).get(e.entry_id), "sn8", None) == "171H120F"}
        if not sources:
            return self.async_abort(reason="no_matching_device")
        if user_input:
            selected = user_input["source_entry"]
            if selected not in sources:
                return self.async_abort(reason="no_matching_device")
            await self.async_set_unique_id(selected)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Olimpia Splendid SHERPA 171H120F", data=user_input)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required("source_entry"): vol.In(sources)}))
