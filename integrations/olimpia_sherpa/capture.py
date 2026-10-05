"""Bounded, passive capture of frames on the existing appliance subscription."""
from collections import deque
from datetime import datetime, timezone
import json
import re

HEX = re.compile(r"[0-9a-fA-F]{2,4096}\Z")

def extract_frame(payload):
    """Retain only hexadecimal frame data, never the JSON account envelope."""
    try:
        message = json.loads(payload)
        data = message.get("data") if isinstance(message, dict) else None
        frame = data.get("commandHex") if isinstance(data, dict) else None
        if not isinstance(frame, str) or len(frame) % 2 or not HEX.fullmatch(frame):
            return None
        return frame.lower()
    except (ValueError, TypeError, UnicodeError):
        return None

class PassiveCapture:
    def __init__(self, hass, source):
        self.hass = hass
        self.source = source
        self.count = 0
        self.frames = deque(maxlen=100)
        self.client = None
        self.original = None
        self.wrapper = None
        self.listeners = set()

    def attach(self, *_):
        push = getattr(self.source, "_push_client", None)
        client = getattr(push, "_mqtt", None)
        if client is self.client:
            return
        self.detach()
        if client is None or not callable(client.on_message):
            self.notify()
            return
        self.client = client
        self.original = client.on_message
        original = self.original
        def receive(c, userdata, msg):
            frame = extract_frame(msg.payload)
            self.hass.loop.call_soon_threadsafe(self.record, frame)
            original(c, userdata, msg)
        self.wrapper = receive
        client.on_message = receive
        self.notify()

    def record(self, frame):
        self.count += 1
        if frame is not None:
            self.frames.append({"time": datetime.now(timezone.utc).isoformat(), "frame": frame})
        self.notify()

    def notify(self):
        for listener in tuple(self.listeners):
            listener()

    def detach(self):
        if self.client is not None and self.client.on_message is self.wrapper:
            self.client.on_message = self.original
        self.client = self.original = self.wrapper = None

    def snapshot(self):
        push = getattr(self.source, "_push_client", None)
        return {"capture_attached": self.client is not None,
                "mqtt_connected": bool(getattr(push, "connected", False)),
                "messages_received": self.count,
                "frames": list(self.frames),
                "scope": "existing appliance status subscription only",
                "control_validated": False}
