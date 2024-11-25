# This assumes you have st7789_mpy and micropython in the same root directory
include("$(PORT_DIR)/boards/manifest.py")
module("axp202c.py", base_path="$(MPY_DIR)/../st7789_mpy/lib")
module("focaltouch.py", base_path="$(MPY_DIR)/../st7789_mpy/lib")
module("vga1_8x8.py", base_path="$(MPY_DIR)/../st7789_mpy/fonts/bitmap")
require("logging")
require("aioble")
require("aiohttp")
