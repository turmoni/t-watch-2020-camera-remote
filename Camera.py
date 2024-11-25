"""
Base module for the camera API used by the watch.
Implements stubs for everything that's required
"""


class Camera:

    # The following are mandatory to implement:
    async def connect(self) -> None:
        """Connect to the camera"""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """Disconnect from the camera"""
        raise NotImplementedError

    async def get_recording_state(self) -> bool:
        """Implement this to return the recording state of the camera, as a boolean where True is recording"""
        raise NotImplementedError

    def connected(self) -> bool:
        """Implement this to determine whether your camera is connected or not, returning a boolean"""
        raise NotImplementedError

    def connecting(self) -> bool:
        """Return True if the watch is currently trying to connect to the camera, False otherwise"""
        raise NotImplementedError

    async def start_recording(self) -> None:
        """Tell the camera to start recording"""
        raise NotImplementedError

    async def stop_recording(self) -> None:
        """Tell the camera to stop recording"""
        raise NotImplementedError

    # These are optional but recommended if applicable
    def invalidate_cache(self) -> None:
        """Only implement this if you have a cache to invalidate"""
        pass

    async def get_battery_level(self) -> int:
        """Return the battery level of the device, as a percentage"""
        self.logger.info("Using parent get_battery_level, data is not accurate")
        return 0
