# Olimpia Splendid SHERPA 171H120F — 0.2.0

Original Home Assistant integration, domain `olimpia_sherpa`.
Adds “Temperatura definida de climatização” and retains both raw response sensors.
The user's official-app tests established status byte 6 (zero-based) as the climate
target: 5 → 6 → 5 °C. Byte 1 bit 0 changed with ON/OFF; it is exposed only as
an activity attribute, not as persistent power or compressor state.

The decoder accepts only the model and narrow 25-byte captured signature.
Unsupported responses make the target unavailable. The observed cooling target
range is 5–25 °C; other layouts/modes need evidence before broadening the gate.
DHW temperature is never substituted for the climate target.

Depends on installed iLetComfort for authentication and transport. Creates no
additional login or device commands. Existing iLetComfort behaviour remains.
Install this directory as `config/custom_components/olimpia_sherpa`, restart HA,
then add “Olimpia Splendid SHERPA 171H120F” in Devices & services.

Verification: four fixture tests cover temperature changes, ON/OFF correlation,
tank independence, and rejection of other models/layouts. Run
`python3 -m unittest discover -s integrations/olimpia_sherpa -p 'test_*.py'`.
Python compilation passed. Installation and live entity updates remain untested.
No solar automation or write controls are included. Status offsets do not prove
control-command encoding. This release does not change DHW or its schedules.
