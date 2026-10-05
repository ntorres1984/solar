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
        self.subscribe_original = None
        self.subscribe_wrapper = None
        self.subscription_mid = None
        self.subscription_result = "not_checked"
        self.subscription_codes = []
        self.probe_sent = False

    def attach(self, *_):
        push = getattr(self.source, "_push_client", None)
        client = getattr(push, "_mqtt", None)
        if client is self.client and client is not None and client.on_message is self.wrapper:
            self.probe_subscription(push)
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
        self.subscribe_original = client.on_subscribe
        subscribe_original = self.subscribe_original
        def subscribed(c, userdata, mid, granted, *extra):
            codes = [int(getattr(code, "value", code)) for code in granted]
            self.hass.loop.call_soon_threadsafe(self.record_subscription, c, mid, codes)
            if subscribe_original is not None:
                subscribe_original(c, userdata, mid, granted, *extra)
        self.subscribe_wrapper = subscribed
        client.on_subscribe = subscribed
        self.probe_subscription(push)
        self.notify()

    def probe_subscription(self, push):
        """Ask only for the existing own-appliance topic; never publish controls."""
        if self.probe_sent or not getattr(push, "connected", False):
            return
        region = getattr(push, "_region", None)
        appliance = getattr(push, "_appliance_code", None)
        if not region or not appliance:
            self.subscription_result = "missing_topic_parameters"
            return
        self.probe_sent = True
        self.subscription_result = "awaiting_ack"
        rc, mid = self.client.subscribe(f"{region}/midea/dev/{appliance}", qos=0)
        self.subscription_mid = mid
        if int(rc) != 0:
            self.subscription_result = "send_failed"
        self.notify()

    def record_subscription(self, client, mid, codes):
        if client is not self.client or mid != self.subscription_mid:
            return
        self.subscription_codes = codes
        self.subscription_result = "accepted" if codes and all(code < 128 for code in codes) else "rejected"
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
        if self.client is not None and self.client.on_subscribe is self.subscribe_wrapper:
            self.client.on_subscribe = self.subscribe_original
        self.client = self.original = self.wrapper = None
        self.subscribe_original = self.subscribe_wrapper = None
        self.subscription_mid = None
        self.subscription_result = "not_checked"
        self.subscription_codes = []
        self.probe_sent = False

    def snapshot(self):
        push = getattr(self.source, "_push_client", None)
        return {"capture_attached": self.client is not None,
                "capture_callback_active": self.client is not None and self.client.on_message is self.wrapper,
                "subscription_result": self.subscription_result,
                "subscription_codes": list(self.subscription_codes),
                "mqtt_connected": bool(getattr(push, "connected", False)),
                "messages_received": self.count,
                "frames": list(self.frames),
                "scope": "existing appliance status subscription only",
                "control_validated": False}
