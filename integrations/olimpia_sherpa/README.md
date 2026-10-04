# Olimpia Splendid SHERPA 171H120F — 0.1.0

Original Home Assistant integration, domain `olimpia_sherpa`.
This first version exposes two diagnostic sensors with raw status/sensor responses.
It deliberately does not decode unvalidated fields or provide climate controls.

It depends on the installed iLetComfort integration for authentication and transport.
It is therefore not yet a standalone replacement. It creates no additional login
and sends no additional commands. Existing iLetComfort behaviour remains in effect.

Install this directory as `config/custom_components/olimpia_sherpa`, restart HA,
then add “Olimpia Splendid SHERPA 171H120F” in Devices & services.
Requires a loaded iLetComfort entry with model code 171H120F.

The user's supplied response has 25 status bytes and 38 sensor bytes.
DHW and space-conditioning commands and field mappings still require validation.
Hardware installation/testing has not been performed. No solar automation is included.
