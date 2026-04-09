#!/usr/bin/env python3
import sys
import time

from PIL import Image, ImageDraw, ImageFont
import st7789

MESSAGE = "Hello World! How are you today?"

print("""
scrolling-text.py - Display scrolling text.

Note: Updated for Trixie (Debian 13) / kernel 6.x.
      Pillow textsize() replaced with font.getbbox().

Usage: {} "<message>" <display_type>

Where <display_type> is one of:

  * square - 240x240 1.3" Square LCD
  * round  - 240x240 1.3" Round LCD (applies an offset)
  * rect   - 240x135 1.14" Rectangular LCD (applies an offset)
  * dhmini - 320x240 2.0" Display HAT Mini
""".format(sys.argv[0]))

try:
    MESSAGE = sys.argv[1]
except IndexError:
    pass

try:
    display_type = sys.argv[2]
except IndexError:
    display_type = "square"

if display_type in ("square", "rect", "round"):
    disp = st7789.ST7789(
        height=135 if display_type == "rect" else 240,
        rotation=0 if display_type == "rect" else 90,
        port=0,
        cs=st7789.BG_SPI_CS_FRONT,
        dc=9,
        backlight=19,
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0 if display_type == "square" else 40,
        offset_top=53 if display_type == "rect" else 0
    )
elif display_type == "dhmini":
    disp = st7789.ST7789(
        height=240,
        width=320,
        rotation=180,
        port=0,
        cs=1,
        dc=9,
        backlight=13,
        spi_speed_hz=60 * 1000 * 1000,
        offset_left=0,
        offset_top=0
    )
else:
    print("Invalid display type!")
    sys.exit(1)

disp.begin()

WIDTH = disp.width
HEIGHT = disp.height

img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)

# Pillow 10+: use getbbox() instead of removed textsize()
bbox = font.getbbox(MESSAGE)
size_x = bbox[2] - bbox[0]
size_y = bbox[3] - bbox[1]

text_x = disp.width
text_y = (disp.height - size_y) // 2

t_start = time.time()

while True:
    x = (time.time() - t_start) * 100
    x %= (size_x + disp.width)
    draw.rectangle((0, 0, disp.width, disp.height), (0, 0, 0))
    draw.text((int(text_x - x), text_y), MESSAGE, font=font, fill=(255, 255, 255))
    disp.display(img)
