"""SHERPA pilot: read-only until independent zone writes are validated."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.exceptions import HomeAssistantError

from custom_components.iletcomfort.api import ApiError, ILetComfortClient, ITSStatus, ITSSensors
from custom_components.iletcomfort.climate import ILetComfortClimate


@pytest.mark.parametrize("change", [
    {"mode": 0}, {"mode": 1}, {"mode": 3}, {"temperature": 5},
    {"power_on": True}, {"boost": True}, {"mute": 1},
])
def test_sherpa_never_sends_unvalidated_write(change):
    client = ILetComfortClient(api_base="https://eu.dollin.net")
    with patch.object(client, "send_hex_command") as send:
        with pytest.raises(ApiError, match="Zone-1"):
            client.set_device("SYNTHETIC", sn8="171H120F", **change)
        send.assert_not_called()


def make_entity():
    coord = MagicMock()
    coord.sn8 = "171H120F"
    coord.appliance_code = "SYNTHETIC"
    coord.appliance_meta = {"sn8": "171H120F"}
    coord.data = {"status": ITSStatus(), "sensors": ITSSensors(th_temp=38)}
    coord.async_set_device = AsyncMock()
    return ILetComfortClimate(coord)


def test_climate_does_not_display_dhw_temperature():
    assert make_entity().current_temperature is None


def test_sherpa_card_does_not_advertise_control():
    assert make_entity().supported_features == ClimateEntityFeature(0)


def test_unvalidated_power_signal_is_unknown_not_off():
    entity = make_entity()
    entity.coordinator.data["status"].raw_body = bytes([1]) + bytes(24)
    assert entity.hvac_mode is None


async def test_direct_climate_call_is_blocked():
    entity = make_entity()
    with pytest.raises(HomeAssistantError, match="Zone-1"):
        await entity.async_turn_on()
    entity.coordinator.async_set_device.assert_not_awaited()
