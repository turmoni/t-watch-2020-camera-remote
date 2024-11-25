import network
import json
import time
import aiohttp
import logging
import Camera


class BanditCamera(Camera.Camera):
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.base_uri = "http://192.168.1.101/api/2"
        self.cache_time = None
        self.session = None
        self.is_connecting = False
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        if self.is_connecting:
            return

        self.is_connecting = True
        nic = network.WLAN(network.STA_IF)
        nic.active(True)
        nic.connect(self.ssid, self.password)
        self.nic = nic

    def connected(self):
        try:
            return self.nic.isconnected()
        except AttributeError as exc:
            self.logger.debug(
                f"Got an AttributeError, so returning not connected: {str(exc)}"
            )
            return False

    def connecting(self):
        if self.is_connecting and self.nic.isconnected():
            self.is_connecting = False

        return self.is_connecting

    def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(self.base_uri)

        return self.session

    def invalidate_cache(self):
        self.cache_time = None

    async def _refresh_status_cache(self):
        session = self._get_session()
        async with session.get("/status") as response:
            # self.status_cache = json.loads(await response.text())
            self.status_cache = await response.json()
            self.cache_time = time.ticks_ms()

    async def _ensure_status_cache(self):
        if (
            self.cache_time is None
            or time.ticks_diff(time.ticks_ms(), self.cache_time) > 1000 * 10
        ):
            await self._refresh_status_cache()

    async def get_status_entry(self, entry):
        await self._ensure_status_cache()
        return self.status_cache[entry]

    async def get_recording_state(self):
        return await self.get_status_entry("recording_active")

    async def get_battery_level(self):
        return await self.get_status_entry("battery_level_pct")

    async def start_recording(self):
        session = self._get_session()
        async with session.post("/record", data=b'{"recording_active": true}') as resp:
            pass

    async def stop_recording(self):
        session = self._get_session()
        async with session.post("/record", data=b'{"recording_active": false}') as resp:
            pass
