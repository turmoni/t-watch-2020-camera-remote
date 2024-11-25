import logging
import asyncio
from machine import Pin, SPI, I2C
import machine
import axp202c
import st7789
import vga1_8x8 as font
import time
import json
from res import unplugged, disconnected, recording, idle, connecting
import focaltouch


class Watch:
    """Handle all of the watchy functions"""

    FONT_HEIGHT = 8

    async def send_notification(self):
        """Endlessly send a buzz pattern to the vibration motor, being sure to finish off with the vibration disabled"""
        try:
            while True:
                self.buzz.value(1)
                await asyncio.sleep(1)
                self.buzz.value(0)
                await asyncio.sleep(2)
        finally:
            self.buzz.value(0)

    def print_recording_status(self, recording_state, x, y):
        """Format and print the given recording status of a camera"""
        self.display.text(font, "Rec:", x, y, st7789.WHITE)

        if recording_state:
            rec_state_col = st7789.GREEN
            text = "yes"
        else:
            rec_state_col = st7789.RED
            text = "no"

        start_point = x + 8 * 5
        self.display.text(font, text, start_point, y, rec_state_col)

    def draw_status(self, status, x, y):
        """Draw the status image"""
        if status not in self.statuses:
            raise ValueError(f"Invalid status passed to draw_status: {status}")

        self.display.bitmap(self.statuses[status]["image"], x, y)

    def draw_battery_level(self, battery_level, x, y, width):
        """Draw a coloured rectangle indicating the given battery level"""
        self.display.rect(x, y, width, 100 + 2, st7789.WHITE)
        if not isinstance(battery_level, int):
            # Draw a thing, I think the Bandit remote control doesn't know this
            return

        if battery_level > 60:
            bat_level_col = st7789.GREEN
        elif battery_level > 20:
            bat_level_col = st7789.YELLOW
        else:
            bat_level_col = st7789.RED

        self.display.fill_rect(
            x + 1, y + 1, width - 2, 100 - battery_level, st7789.BLACK
        )
        self.display.fill_rect(
            x + 1,
            y + 1 + (100 - battery_level),
            width - 2,
            battery_level,
            bat_level_col,
        )

    def print_battery_level(self, battery_level, x, y):
        """Format and print a given battery level, in text"""
        self.display.text(font, "Bat:", x, y, st7789.WHITE)

        if battery_level > 60:
            bat_level_col = st7789.GREEN
        elif battery_level > 10:
            bat_level_col = st7789.YELLOW
        else:
            bat_level_col = st7789.RED

        start_point = x + 8 * 5
        self.display.text(font, f"{battery_level}%", start_point, y, bat_level_col)

    async def watch_camera(self, pane):
        """Set up the configuration for a single camera, then endlessly watch the status of it and keep updating the screen and kick off/cancel notification tasks"""
        config = self.panes[pane]
        device = config["camera"]
        config["width"] = config["dimensions"]["x"][1] - config["dimensions"]["x"][0]
        image_x_start = int(config["dimensions"]["x"][0] + (config["width"] - 80) / 2)
        config["has_recording_started"] = False

        self.touchzones[pane] = {
            "x": config["dimensions"]["x"][0],
            "width": config["width"],
            "y": config["dimensions"]["y"][0],
            "height": 120,
            "function": self.handle_touch_toggle,
            "params": {"device": device},
        }

        while True:
            try:
                if device.connecting():
                    self.draw_status("connecting", image_x_start, 20)
                    await asyncio.sleep(0.1)
                    continue

                if not device.connected():
                    self.draw_status("disconnected", image_x_start, 20)
                    await asyncio.sleep(0.5)
                    continue

                # FIXME report this better
                try:
                    recording_state = await device.get_recording_state()
                except Exception as exc:
                    self.logger.info(
                        f"Setting recording_state to false because {str(exc)}"
                    )
                    recording_state = False

                # Get this bit in early in case something later on errors
                if recording_state:
                    try:
                        config["notification_task"].cancel()
                        del config["notification_task"]
                    except KeyError:
                        self.logger.info(
                            "Tried to cancel a notification task that doesn't exist"
                        )
                        pass
                    except AttributeError as exc:
                        self.logger.info(f"Got attribute error: {str(exc)}")
                        pass

                    config["has_recording_started"] = True
                elif (
                    config["notify_on_stop"]
                    and config["has_recording_started"]
                    and not "notification_task" in config
                ):
                    config["notification_task"] = self.event_loop.create_task(
                        self.send_notification()
                    )

                # FIXME report this better
                try:
                    battery_level = await device.get_battery_level()
                except Exception as exc:
                    self.logger.info(f"Returning 0 battery level due to {str(exc)}")
                    battery_level = 0

                self.display.fill_rect(
                    config["dimensions"]["x"][0],
                    config["dimensions"]["y"][0],
                    config["width"],
                    Watch.FONT_HEIGHT * 4,
                    st7789.BLACK,
                )
                self.draw_status(
                    "recording" if recording_state else "idle", image_x_start, 20
                )
                self.draw_battery_level(battery_level, image_x_start, 120, 80)
                self.print_battery_level(
                    battery_level, config["dimensions"]["x"][0], Watch.FONT_HEIGHT
                )

            except Exception as exc:
                self.logger.error(f"General unhandled exception: {str(exc)}")
                self.display.text(
                    font, "Exception!", config["dimensions"]["x"][0], 0, st7789.RED
                )
            await asyncio.sleep(config["poll_time"])

    async def record_trigger(self, pane):
        """Start a camera recording based on a press of the side button"""
        if not pane:
            self.logger.debug("No device configured for button_press_start")
            return

        device = self.panes[pane]["camera"]
        try:
            await device.start_recording()
            device.invalidate_cache()
            await asyncio.sleep(1)
        except Exception as exc:
            self.logger.error(f"Exception in button handling: {str(exc)}")
            self.display.text(
                font,
                "Not connected!",
                self.panes[pane]["dimensions"]["x"][0],
                Watch.FONT_HEIGHT * 3,
                st7789.RED,
            )

    async def update_watch_battery(self):
        """Endless loop updating the text showing the current battery percentage of the watch"""
        while True:
            percentage = self.axp.getBattPercentage()
            self.display.fill_rect(
                0,
                self.display.height() - Watch.FONT_HEIGHT,
                self.display.width(),
                Watch.FONT_HEIGHT,
                st7789.BLACK,
            )
            self.display.text(
                font,
                f"Watch batt: {percentage}%",
                0,
                self.display.height() - Watch.FONT_HEIGHT,
            )
            await asyncio.sleep(60)

    async def handle_touch_toggle(self, device, zone):
        """The function to fire when the status icon for a camera has been touched"""
        if not device.connected():
            self.logger.info("Connecting to device")
            # The module should handle safely dealing with multiple connect calls
            asyncio.create_task(device.connect())
            return

        if not await device.get_recording_state():
            self.logger.info("Starting recording")
            await device.start_recording()
            device.invalidate_cache()
            # Give time for it to respond appropriately
            await asyncio.sleep(1)
            return

        x = self.touchzones[zone]["x"]
        y = self.touchzones[zone]["y"]
        endx = x + self.touchzones[zone]["width"]
        endy = y + self.touchzones[zone]["height"]

        endtime = time.ticks_add(time.ticks_ms(), 3000)
        while time.ticks_diff(endtime, time.ticks_ms()) > 0:
            if self.ft.touched != 1:
                return

            if not x <= self.ft.touches[0]["x"] <= endx:
                return

            if not y <= self.ft.touches[0]["y"] <= endy:
                return

            await asyncio.sleep(0.1)

        self.logger.info("Stopping recording")
        await device.stop_recording()
        # Give time for it to respond appropriately
        await asyncio.sleep(1)
        device.invalidate_cache()
        self.panes[zone]["has_recording_started"] = False

    async def watch_touchscreen(self):
        """Endlessly loop to see if the touchscreen has been touched"""
        while True:
            # I've seen the library give 255 on startup
            if self.ft.touched == 1:
                # Only bother handling a single touch
                lookup = self._lookup_touch(self.ft.touches[0])
                if lookup:
                    await lookup["function"](**lookup["params"], zone=lookup["zone"])

            await asyncio.sleep(0.1)

    def _lookup_touch(self, touch):
        """Map a set of touched coordinates to an action to take"""
        for zonename in self.touchzones:
            zone = self.touchzones[zonename]
            if not zone["x"] <= touch["x"] <= zone["x"] + zone["width"]:
                continue
            if not zone["y"] <= touch["y"] <= zone["y"] + zone["height"]:
                continue

            self.logger.debug(f"Got touch zone {zonename}")
            return {
                "function": zone["function"],
                "params": zone["params"],
                "zone": zonename,
            }

        return None

    async def _handle_exception(self, loop, context):
        """Log exceptions, hopefully"""
        self.logger.error(f"Got an unhandled exception: {context}")

    def main(self):
        """Set up everything for running the watch loop"""
        logging.basicConfig(filename="watch.log", level=logging.INFO)
        self.logger.info("Startup")

        with open("config.json", "r") as conffile:
            config = json.load(conffile)

        for entry in config["devices"]:
            config["devices"][entry]["module"] = __import__(
                config["devices"][entry]["driver"]
            )

        def axp_interrupt(pin):
            loop = asyncio.get_event_loop()
            self.logger.debug("Button has been pressed")
            loop.create_task(self.record_trigger(self.button_press_start))
            self.axp.clearIRQ()

        self.axp_int.irq(trigger=Pin.IRQ_FALLING, handler=axp_interrupt)

        self.button_press_start = config.get("button_press_start", None)
        self.event_loop = asyncio.get_event_loop()
        self.panes = {
            "left": {
                "dimensions": {
                    "x": [0, int(self.display.width() / 2) - 1],
                    "y": [0, self.display.height() - 1],
                },
                "camera": getattr(
                    config["devices"]["left"]["module"],
                    config["devices"]["left"]["driver"],
                )(**config["devices"]["left"]["parameters"]),
                "notify_on_stop": config["devices"]["left"].get(
                    "notify_on_stop", False
                ),
                "poll_time": config["devices"]["left"].get("poll_time", 2),
            },
            "right": {
                "dimensions": {
                    "x": [int(self.display.width() / 2), self.display.width() - 1],
                    "y": [0, self.display.height() - 1],
                },
                "camera": getattr(
                    config["devices"]["right"]["module"],
                    config["devices"]["right"]["driver"],
                )(**config["devices"]["right"]["parameters"]),
                "notify_on_stop": config["devices"]["right"].get(
                    "notify_on_stop", False
                ),
                "poll_time": config["devices"]["right"].get("poll_time", 2),
            },
        }

        for pane in self.panes:
            self.event_loop.create_task(self.watch_camera(pane))

        self.event_loop.create_task(self.update_watch_battery())
        self.event_loop.create_task(self.watch_touchscreen())
        self.event_loop.set_exception_handler(self._handle_exception)
        self.event_loop.run_forever()

    def __init__(self):
        """Set up the core hardware for the watch"""
        self.buzz = Pin(4, Pin.OUT)
        self.axp = axp202c.PMU()
        self.axp.enablePower(axp202c.AXP202_LDO2)
        self.axp.clearIRQ()
        self.axp_int = Pin(35, Pin.IN)
        self.display = st7789.ST7789(
            SPI(1, baudrate=32000000, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT)),
            240,
            240,
            cs=Pin(5, Pin.OUT),
            dc=Pin(27, Pin.OUT),
            # backlight=Pin(12, Pin.OUT), for V1
            backlight=Pin(15, Pin.OUT),  # V3
            rotation=2,
        )

        self.display.init()
        self.statuses = {
            "idle": {"image": idle},
            "disconnected": {"image": disconnected},
            "recording": {"image": recording},
            "connecting": {"image": connecting},
        }

        self.i2c = I2C(1, scl=Pin(32), sda=Pin(23))
        self.ft = focaltouch.FocalTouch(self.i2c)
        self.touchzones = {}
        self.panes = {}
        self.logger = logging.getLogger(__name__)

    def charging(self):
        """Don't do all the watchy stuff, just show charging state"""

        battery_width = 140
        battery_height = 200
        left_start = int((self.display.width() - battery_width) / 2)
        top_start = int((self.display.height() - battery_height) / 2)

        self.display.rect(
            left_start - 1,
            top_start - 1,
            battery_width + 2,
            battery_height + 2,
            st7789.WHITE,
        )

        logging.basicConfig(filename="watch.log", level=logging.ERROR)
        self.logger = logging.getLogger(__name__)

        def axp_interrupt(pin):
            machine.reset()

        self.axp_int.irq(trigger=Pin.IRQ_FALLING, handler=axp_interrupt)

        while True:
            try:
                if not self.axp.isVBUSPlug():
                    self.logger.debug("Not plugged in")
                    self.display.bitmap(unplugged, left_start, top_start)
                    self.logger.debug("Displayed bitmap")
                    while not self.axp.isVBUSPlug():
                        self.logger.debug("Still not plugged in")
                        # No need to keep re-rendering a static PNG
                        time.sleep(1)

                percentage = self.axp.getBattPercentage()
                self.logger.debug(f"Percentage of battery is {percentage}")

                if percentage < 40:
                    colour = st7789.RED
                elif percentage < 80:
                    colour = st7789.YELLOW
                else:
                    colour = st7789.GREEN

                self.logger.debug("About to draw the rectangle")
                self.display.fill_rect(
                    left_start,
                    top_start + (100 - percentage) * 2,
                    battery_width,
                    percentage * 2,
                    colour,
                )
                self.logger.debug("About to sleep after drawing the rectangle")
                time.sleep(1)
            except Exception as exc:
                self.logger.error(f"Exception: {exc}")


def m():
    """A function with a short name for easily running the watch from the REPL"""
    w = Watch()
    w.main()
