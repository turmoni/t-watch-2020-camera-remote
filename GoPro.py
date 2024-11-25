import aioble
import bluetooth
import logging
import asyncio
import Camera


class GoPro(Camera.Camera):
    def __init__(self, name):
        self.name = name
        self.is_connecting = False
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _gp(uuid):
        """Return a UUID in full based on "GP-XXXX" values in the documentation"""
        return bluetooth.UUID(f"b5f9{uuid}-aa8d-11e3-9046-0002a5d5c51b")

    @staticmethod
    def _deconstruct(data):
        """Encode data for GoPro packets"""
        response = []
        this_line = bytearray(int(len(data) + 0b0010000000000000).to_bytes(2, "big"))
        to_go = len(data)
        idx = 0
        pos = 0

        while to_go > 20:
            pos = len(data) - to_go
            this_line = bytearray(this_line + data[pos : pos + 20])
            response.append(this_line)
            # Add a continuation header
            this_line = bytearray(int(idx + 0b10000000).to_bytes(1, "big"))
            idx += 1
            to_go -= 20

        response.append(this_line + data[pos : pos + to_go])
        return response

    def _reconstruct(self, data):
        """Reconstruct data from GoPro packets"""
        if data[0] > 0b10000000:
            # It's a continuation. Let's not bother with the counter
            self.logger.debug("Continuation packet")
            return (None, data[1:])

        if data[0] > 0b01000000:
            # Extended 16
            self.logger.debug("Extended 16")
            return (int.from_bytes(data[1:2], "big"), data[3:])

        if data[0] > 0b00100000:
            # Extended 13
            self.logger.debug("Extended 13")
            length = int.from_bytes(data[:1], "big") - 0b0010000000000000
            return (length, data[2:])

        # Standard old one
        self.logger.debug("Standard GoPro message")
        return (int(data[0]), data[1:])

    def invalidate_cache(self):
        """Do nothing"""
        return

    async def connect(self):
        if self.is_connecting or self.connected():
            self.logger.info("Already connected or connecting, ignoring new request")
            return

        self.logger.debug("Disconnect existing devices")
        bluetooth.BLE().active(False)
        self.device = None
        self.is_connecting = True
        self.logger.info("Scanning")
        while not self.device:
            async with aioble.scan(
                duration_ms=5000, interval_us=30000, window_us=30000, active=True
            ) as scanner:
                async for result in scanner:
                    self.logger.debug(result, f"'{result.name()}'", type(result.name()))
                    if result.name() == f"GoPro {self.name}":
                        self.device = result.device
                        self.logger.info("Found GoPro device")
                        await scanner.cancel()
                    await asyncio.sleep(0)

        self.logger.info("Connecting")
        self.connection = await self.device.connect(timeout_ms=30000)
        self.logger.info("Pairing")
        await self.connection.pair()
        self.logger.info("Paired")
        service = await self.connection.service(bluetooth.UUID(0xFEA6))
        self.command = await service.characteristic(self._gp("0072"))
        self.command_response = await service.characteristic(self._gp("0073"))
        self.query = await service.characteristic(self._gp("0076"))
        self.query_response = await service.characteristic(self._gp("0077"))
        self.logger.info("Connect finished")
        self.is_connecting = False

    def connected(self):
        """Is the device connected?"""
        try:
            return self.connection.is_connected()
        except AttributeError as exc:
            self.logger.debug(
                f"Got an AttributeError, so returning not connected: {str(exc)}"
            )
            return False

    def connecting(self):
        return self.is_connecting

    async def get_recording_state(self):
        await self.query_response.subscribe(notify=True)
        query = self._deconstruct(bytes([0x13, 10]))
        for line in query:
            await self.query.write(line)

        (length, data) = self._reconstruct(await self.query_response.notified())
        while length > len(data):
            (_, this_data) = self._reconstruct(await self.query_response.notified())
            data += this_data

        if data[:4] == b"\x13\x00\x0A\x01":
            return data[4] == 0x01

    async def get_battery_level(self):
        await self.query_response.subscribe(notify=True)
        query = self._deconstruct(bytes([0x13, 70]))
        for line in query:
            await self.query.write(line)

        (length, data) = self._reconstruct(await self.query_response.notified())
        while length > len(data):
            (_, this_data) = self._reconstruct(await self.query_response.notified())
            data += this_data

        if data[:4] == b"\x13\x00\x46\x01":
            return int(data[4])

    async def start_recording(self):
        self.logger.info("Starting recording")
        command = self._deconstruct(bytes([0x01, 0x01, 0x01]))
        for line in command:
            await self.command.write(line)

    async def stop_recording(self):
        self.logger.info("Stopping recording")
        command = self._deconstruct(bytes([0x01, 0x01, 0x00]))
        for line in command:
            await self.command.write(line)
