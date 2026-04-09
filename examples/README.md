# Examples

Basic examples for the Pirate Audio hardware.

## buttons.py

Detects button presses on the four Pirate Audio buttons (BCM 5, 6, 16, 20).

```bash
python3 buttons.py
```

## rainbow.py

Displays a cycling rainbow colour on the ST7789 LCD.

```bash
python3 rainbow.py
```

## backlight-pwm.py

Demonstrates PWM control of the display backlight using `gpiozero.PWMOutputDevice`.

```bash
python3 backlight-pwm.py
```

## shairport-sync-control.py

Controls Shairport Sync via DBus using the Pirate Audio buttons.
Requires Shairport Sync compiled with DBus support and `dbus-python`:

```bash
pip3 install --break-system-packages dbus-python
python3 shairport-sync-control.py
```
