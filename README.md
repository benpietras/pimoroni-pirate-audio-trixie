# Pirate Radio (Trixie / Debian 13 compatible)

This is a community-maintained fork of [pimoroni/pirate-audio](https://github.com/pimoroni/pirate-audio), updated for compatibility with **Raspberry Pi OS Trixie (Debian 13)** and **kernel 6.x**.

Assumes user 'pi'. Only tested on the pre 5/2025 lineout hat version. 

## What changed from upstream

| Issue | Old | New |
|---|---|---|
| GPIO library | `RPi.GPIO` (broken on kernel 6.x) | `gpiozero` + `lgpio` backend |
| Pillow `textsize()` | Removed in Pillow 10+ | Replaced with `font.getbbox()` |
| `ST7789` import | Inconsistent casing | Normalised to `from st7789 import ST7789` |
| `pip install` as root | Blocked by PEP 668 on Trixie | Uses `--break-system-packages` or venv |
| Boot config path | `/boot/config.txt` | `/boot/firmware/config.txt` |
| `python3-rpi.gpio` apt package | Broken on kernel 6.x | `python3-lgpio` + `python3-gpiozero` |
| `pkg_resources` | Deprecated | `importlib.metadata` |

## Hardware

* ST7789 240x240 pixel LCD display
* Four buttons, active low, connected to BCM 5, 6, 16, and 24 (A, B, X, Y respectively)

## config.txt (required)

Add to `/boot/firmware/config.txt`:

```
dtoverlay=hifiberry-dac
gpio=25=op,dh
dtparam=audio=off
```

## Dependencies

```bash
sudo apt update
sudo apt install -y \
  python3-lgpio \
  python3-gpiozero \
  python3-spidev \
  python3-pil \
  python3-numpy \
  python3-pip

pip3 install --break-system-packages st7789
```

## Using with Mopidy

See [mopidy/](mopidy/) for the updated install script.

## Using with Spotify Connect / Shairport Sync

See [raspotify/](raspotify/) and [shairport-sync/](shairport-sync/).

## Build Your Own

See [build your own/](build%20your%20own/) for display and GPIO examples.
