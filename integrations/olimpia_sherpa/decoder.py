"""Conservative reader for Nuno's captured SHERPA status layout.

These offsets describe status responses, never control commands.
"""
from dataclasses import dataclass

_CAPTURE = bytes.fromhex("01 00 17 01 02 02 05 17 37 30 41 23 19 05 37 19 19 05 3c 22 3c 14 25 00 80")
_VARIABLE = {1, 6, 22}

@dataclass(frozen=True)
class SherpaReading:
    target_temperature: int
    activity_signal: bool

def decode_status(raw: bytes, model: str) -> SherpaReading | None:
    """Reject other models/layouts rather than silently reuse an offset.

    The exact observed fixed bytes deliberately make this gate narrow.
    Other modes may require further captures before they can be displayed.
    Activity was correlated with app ON/OFF; persistent power is unproven.
    """
    if model != "171H120F" or len(raw) != len(_CAPTURE):
        return None
    if any(value != _CAPTURE[i] for i, value in enumerate(raw) if i not in _VARIABLE):
        return None
    if raw[1] not in (0, 1) or not 5 <= raw[6] <= 25 or not 0 <= raw[22] <= 100:
        return None
    return SherpaReading(raw[6], bool(raw[1] & 1))
