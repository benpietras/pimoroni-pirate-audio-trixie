#!/usr/bin/env python3
import sys

from PIL import Image, ImageDraw, ImageFont
import st7789

print("""
shapes.py - Display test shapes on the LCD using PIL.

Note: Updated for Trixie (Debian 13) / kernel 6.x.
      Pillow textsize() replaced with font.getbbox().

Usage: {} <display_type>

Where <display_type> is one of:

  * square - 240x240 1.3" Square LCD
  * round  - 240x240 1.3" Round LCD (applies an offset)
  * rect   - 240x135 1.14" Rectangular LCD (applies an offset)
  * dhmini - 320x240 2.0" Display HAT Mini
""".format(sys.argv[0]))

try:
    display_type = sys.argv[1]
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

img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 0, 0))
draw = ImageDraw.Draw(img)

draw.rectangle((10, 10, WIDTH - 10, HEIGHT - 10), outline=(255, 255, 0), fill=(255, 0, 255))
draw.ellipse((10, 10, WIDTH - 10, HEIGHT - 10), outline=(0, 255, 0), fill=(0, 0, 255))
draw.line((10, 10, WIDTH - 10, HEIGHT - 10), fill=(255, 255, 255))
draw.line((10, HEIGHT - 10, WIDTH - 10, 10), fill=(255, 255, 255))
draw.polygon([(WIDTH / 2, 10), (WIDTH - 10, HEIGHT - 10), (10, HEIGHT - 10)], outline=(0, 0, 0), fill=(0, 255, 255))

font = ImageFont.load_default()


def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    draw = ImageDraw.Draw(image)
    # Pillow 10+: use getbbox() instead of removed textsize()
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    rotated = textimage.rotate(angle, expand=1)
    image.paste(rotated, position, rotated)


draw_rotated_text(img, 'Hello World!', (0, 0), 90, font, fill=(255, 255, 255))
draw_rotated_text(img, 'This is a line of text.', (10, HEIGHT - 10), 0, font, fill=(255, 255, 255))

disp.display(img)
