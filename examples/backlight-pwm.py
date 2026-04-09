#!/usr/bin/env python3

import time
import math
from gpiozero import PWMOutputDevice
from st7789 import ST7789
from PIL import Image, ImageDraw

print("""backlight-pwm.py - Demonstrate the backlight being controlled by PWM

This advanced example shows you how to achieve a variable backlight
brightness using PWM via gpiozero's PWMOutputDevice.

Note: Updated for Trixie (Debian 13) / kernel 6.x.
      RPi.GPIO replaced with gpiozero + lgpio backend.

Press Ctrl+C to exit!
""")

SPI_SPEED_MHZ = 90

# Give us an image buffer to draw into
image = Image.new("RGB", (240, 240), (255, 0, 255))
draw = ImageDraw.Draw(image)

# Standard display setup for Pirate Audio, backlight managed manually
st7789 = ST7789(
    rotation=90,
    port=0,
    cs=1,
    dc=9,
    backlight=None,  # We'll control the backlight ourselves
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

# Set up backlight pin as PWM output (pin 13, 500Hz via gpiozero)
backlight = PWMOutputDevice(13, frequency=500)
backlight.value = 1.0  # Start at full brightness

try:
    while True:
        # Use math.sin() to produce a smooth 0.0-1.0 brightness wave
        brightness = (math.sin(time.time()) + 1) / 2.0
        backlight.value = brightness

        draw.rectangle((0, 0, 240, 240), (255, 0, 255))

        # Draw an on-screen bar showing current brightness
        bar_width = int(220 * brightness)
        draw.rectangle((10, 220, 10 + bar_width, 230), (255, 255, 255))

        st7789.display(image)
        time.sleep(1.0 / 30)

finally:
    backlight.value = 0
    backlight.close()
