#!/usr/bin/env python3

import time
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw
from st7789 import ST7789

print("""rainbow.py - Display a rainbow on the Pirate Audio LCD

This example demonstrates how to:
1. set up the Pirate Audio LCD,
2. create a PIL image to use as a buffer,
3. draw something into that image,
4. and display it on the display

Note: Updated for Trixie (Debian 13) / kernel 6.x.

Press Ctrl+C to exit!
""")

SPI_SPEED_MHZ = 80

image = Image.new("RGB", (240, 240), (0, 0, 0))
draw = ImageDraw.Draw(image)

st7789 = ST7789(
    rotation=90,
    port=0,
    cs=1,
    dc=9,
    backlight=13,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

while True:
    hue = time.time() / 10
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
    draw.rectangle((0, 0, 240, 240), (r, g, b))
    st7789.display(image)
    time.sleep(1.0 / 30)
