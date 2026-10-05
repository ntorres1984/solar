"""Anonymous status fixtures from the user's official-app tests."""
import unittest
from decoder import decode_status

BASE = bytes.fromhex("01 00 17 01 02 02 05 17 37 30 41 23 19 05 37 19 19 05 3c 22 3c 14 25 00 80")

def changed(index, value):
    frame = bytearray(BASE)
    frame[index] = value
    return bytes(frame)

class CapturedStatusTests(unittest.TestCase):
    def test_app_temperature_round_trip(self):
        for frame, expected in ((BASE, 5), (changed(6, 6), 6), (BASE, 5)):
            self.assertEqual(decode_status(frame, "171H120F").target_temperature, expected)

    def test_app_on_off_activity_round_trip(self):
        self.assertFalse(decode_status(BASE, "171H120F").activity_signal)
        self.assertTrue(decode_status(changed(1, 1), "171H120F").activity_signal)
        self.assertFalse(decode_status(BASE, "171H120F").activity_signal)

    def test_tank_temperature_is_not_climate_target(self):
        self.assertEqual(decode_status(changed(22, 36), "171H120F").target_temperature, 5)

    def test_other_layouts_and_models_are_unknown(self):
        for frame, model in ((BASE, "17100003"), (BASE[:-1], "171H120F"),
                             (BASE + b"\0\0", "171H120F"), (changed(24, 0), "171H120F"),
                             (changed(6, 55), "171H120F"), (changed(1, 3), "171H120F")):
            self.assertIsNone(decode_status(frame, model))

if __name__ == "__main__":
    unittest.main()
