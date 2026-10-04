#!/usr/bin/env python3
"""Prepare a pinned iLetComfort SHERPA read-only pilot, without credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

UPSTREAM = "https://github.com/tgenov/ha-iletcomfort.git"
REVISION = "4e12b905b922115be27ec0548579f6ba1ab6dde6"
HASHES = {
    "api.py": "4d79e1337571439c3d14500f71bb46ec100de407681221515631c9d88b0405e5",
    "climate.py": "5684a316628bad7d3a932a2479c9c7cb8a3a9c2e37f5c011ff573f85aa2b93d3",
    "manifest.json": "7e5f9a9e0404fe78b338d69e01608638844c5291de74cd5a38d382dc96c44511",
}
MESSAGE = (
    "SHERPA/ATW pilot is read-only: independent Zone-1 and DHW control "
    "requires validation against this controller's official-app commands"
)


def insert_once(text: str, anchor: str, addition: str) -> str:
    if text.count(anchor) != 1:
        raise ValueError("Pinned source anchor mismatch")
    return text.replace(anchor, addition + anchor, 1)


def adapt(component: Path) -> None:
    """All validation precedes edits; never send commands to any device."""
    for name, expected in HASHES.items():
        if hashlib.sha256((component / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Unexpected upstream file: {name}")

    api_path = component / "api.py"
    api = api_path.read_text()
    api = insert_once(api, "        if resolve_profile(sn8) is ModelProfile.KJRH120L:\n",
        "        if resolve_profile(sn8) is ModelProfile.ATW:\n"
        f"            raise ApiError({MESSAGE!r})\n\n")

    climate_path = component / "climate.py"
    climate = climate_path.read_text()
    climate = insert_once(climate, "        if self._is_kjrh120l_dual:\n            return ClimateEntityFeature(0)\n",
        "        if self._profile is ModelProfile.ATW:\n"
        "            return ClimateEntityFeature(0)\n")
    climate = insert_once(climate, "        if self._is_kjrh120l_dual:\n            raise HomeAssistantError(\n",
        "        if self._profile is ModelProfile.ATW:\n"
        f"            raise HomeAssistantError({MESSAGE!r})\n")
    start = climate.index("        # ATW exposes its meaningful current value as the DHW tank temperature.\n")
    end = climate.index("        # AQUAPURA variants normally expose", start)
    climate = climate[:start] + (
        "        # SHERPA hydronic telemetry awaits an actual hardware capture.\n"
        "        # The DHW tank is not space-conditioning water.\n"
        "        if self._profile is ModelProfile.ATW:\n"
        "            return None\n"
    ) + climate[end:]
    climate = climate.replace("def hvac_mode(self) -> HVACMode:",
                              "def hvac_mode(self) -> HVACMode | None:")
    # A 25-byte layout has no confirmed power/mode signal. Avoid false OFF.
    climate = insert_once(climate, "        return _QUERY_MODE_TO_HVAC.get(self._status.mode, HVACMode.OFF)\n",
        "        if self._profile is ModelProfile.ATW:\n"
        "            from .model_profiles import _is_galmet_atw_status\n"
        "            if not _is_galmet_atw_status(self._status.raw_body):\n"
        "                return None\n")

    manifest_path = component / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["name"] = "SHERPA iLetComfort — piloto de leitura"
    manifest["version"] = "0.18.3+sherpa.pilot1"
    api_path.write_text(api)
    climate_path.write_text(climate)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory for config/custom_components; never overwritten")
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination.exists():
        parser.error("Output already exists; choose a new directory")
    with tempfile.TemporaryDirectory(prefix="sherpa-pilot-") as temporary:
        source = Path(temporary) / "upstream"
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", UPSTREAM, str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "checkout", "--quiet", "--detach", REVISION], check=True)
        component = source / "custom_components" / "iletcomfort"
        adapt(component)
        staged = Path(temporary) / "output"
        shutil.copytree(component, staged / "custom_components" / "iletcomfort")
        (staged / "PROVENANCE.json").write_text(json.dumps({
            "upstream": UPSTREAM, "revision": REVISION,
            "pilot": "read-only", "model_code": "171H120F",
            "hardware_tested": False, "independent_zone_writes_validated": False,
        }, indent=2) + "\n")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staged, destination)
    print(f"Prepared read-only pilot: {destination}")
    print("Not installed. Hardware validation and independent zone commands remain pending.")


if __name__ == "__main__":
    main()
