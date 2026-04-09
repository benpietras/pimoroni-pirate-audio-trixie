#!/usr/bin/env python3
import sys
import signal
from gpiozero import Button

print("""read_gpio_pins.py - Detect which button has been pressed

This example demonstrates how to:
1. set up gpiozero to read buttons,
2. determine which button has been pressed

Note: Updated for Trixie (Debian 13) / kernel 6.x.
      RPi.GPIO replaced with gpiozero + lgpio backend.

Press Ctrl+C to exit!
""")

# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20
# Try changing 24 to 20 if your Y button doesn't work.
BUTTON_PINS = [5, 6, 16, 20]
LABELS = ['A', 'B', 'X', 'Y']

buttons = [Button(pin, pull_up=True, bounce_time=0.25) for pin in BUTTON_PINS]


def make_handler(pin, label):
    def handle_button():
        print("Button press detected on pin={} label={}".format(pin, label))
        sys.stdout.flush()
    return handle_button


for button, pin, label in zip(buttons, BUTTON_PINS, LABELS):
    button.when_pressed = make_handler(pin, label)

signal.pause()
