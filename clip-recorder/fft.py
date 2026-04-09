#!/usr/bin/env python3
import math
import time
import pathlib
import numpy
from PIL import Image, ImageDraw, ImageFont

from fonts.ttf import RobotoMedium
from gpiozero import Button
from st7789 import ST7789
import sounddevice

WIDTH = 480
HEIGHT = 480

COLOR_WHITE = (255, 255, 255)
COLOR_RED = (232, 56, 58)
COLOR_GREEN = (47, 173, 102)
COLOR_YELLOW = (242, 146, 0)

BUTTON_PINS = [5, 6, 16, 20]
LABELS = ["A", "B", "X", "Y"]


def transparent(color, opacity=0.2):
    opacity = int(255 * opacity)
    r, g, b = color
    return r, g, b, opacity


class Recordamajig:
    def __init__(self, device="mic_out", output_device="upmix", samplerate=16000):
        self._state = "initial"
        self._clip = 1

        self._vu_left = 0
        self._vu_right = 0
        self._graph = [0 for _ in range(44)]
        self._fft = [0 for _ in range(10)]
        self._indata = numpy.empty((0, 2))

        self._device = device
        self._samplerate = samplerate

        self._image = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._image)

        self._background = Image.open(pathlib.Path("background.png"))

        self._font = ImageFont.truetype(RobotoMedium, size=62)
        self._font_small = ImageFont.truetype(RobotoMedium, size=47)
        self._font_tiny = ImageFont.truetype(RobotoMedium, size=28)

        self._stream = sounddevice.InputStream(
            device=self._device,
            dtype="int16",
            channels=2,
            samplerate=self._samplerate,
            callback=self.audio_callback
        )
        self._stream.start()

    def audio_callback(self, indata, frames, time, status):
        self._vu_left = numpy.average(numpy.abs(indata[:, 0])) / 65535.0 * 5
        self._vu_right = numpy.average(numpy.abs(indata[:, 1])) / 65535.0 * 5
        self._graph.append(min(1.0, max(self._vu_left, self._vu_right)))
        self._graph = self._graph[-44:]
        self._indata = numpy.concatenate((self._indata, indata))
        if len(self._indata) >= self._samplerate:
            self._indata = self._indata[-self._samplerate:]
            self.calculate_fft()

    def calculate_fft(self):
        fft = numpy.abs(numpy.fft.fft(self._indata[:, 0])) / self._samplerate
        fft = fft[range(2000)]
        self._fft = numpy.mean(fft.reshape(-1, 2000 // 10), axis=1)

    def draw_text(self, x, y, text, font, w=480, h=None, alignment="left", vertical_alignment="top", color=COLOR_WHITE):
        # Pillow 10+: use getbbox() instead of removed textsize()
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if h is None:
            h = th
        if alignment == "center":
            x += w // 2
            x -= tw // 2
        if vertical_alignment == "center":
            y += h // 2
            y -= th // 2
        self._draw.text((x, y), text, color, font=font)

    @property
    def running(self):
        return not self._stream.stopped and self._stream.active

    def render(self):
        self._draw.rectangle((0, 0, 480, 480), (0, 0, 0, 0))

        bar_x = 0
        bar_color = COLOR_WHITE

        for bar in range(10):
            scale = min(1.0, self._fft[bar] / 100.0)
            bar_w = 24
            bar_h = max(2, 480 * scale)
            if bar_h % 1:
                bar_h += 1
            bar_y = 240 - (bar_h // 2)
            self._draw.rectangle((bar_x, bar_y, bar_x + bar_w - 1, bar_y + bar_h - 1), bar_color)
            bar_x += 48

        return Image.alpha_composite(self._background.convert("RGBA"), self._image).convert("RGB")


SPI_SPEED_MHZ = 80

display = ST7789(
    rotation=90,
    port=0,
    cs=1,
    dc=9,
    backlight=13,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

recordamajig = Recordamajig()

# No button handling in fft.py (display only), but pins set up for future use
buttons = [Button(pin, pull_up=True, bounce_time=0.25) for pin in BUTTON_PINS]

while recordamajig.running:
    display.display(recordamajig.render().resize((240, 240)))
    time.sleep(1.0 / 30)
