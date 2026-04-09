#!/usr/bin/env python3

import signal
import dbus
from gpiozero import Button

"""
shairport-sync-control.py - Control Shairport Sync via DBus and Pirate Audio buttons.

Play/Pause, Next and volume control are supported.

Note: Updated for Trixie (Debian 13) / kernel 6.x.
      RPi.GPIO replaced with gpiozero + lgpio backend.

You *must* compile Shairport Sync with DBus support for this to work.

You must also have dbus-python installed:
    pip3 install --break-system-packages dbus-python

Controls can be a little slow - there's a lot going on here. Be patient!
"""

BUTTON_PINS = [5, 6, 16, 20]
LABELS = ["A", "B", "X", "Y"]

bus = dbus.SystemBus()
proxy = bus.get_object("org.gnome.ShairportSync", "/org/gnome/ShairportSync")
interface = dbus.Interface(
    proxy, dbus_interface="org.gnome.ShairportSync.RemoteControl"
)

shairport_playpause = interface.get_dbus_method("PlayPause")
shairport_next = interface.get_dbus_method("Next")
shairport_volumeup = interface.get_dbus_method("VolumeUp")
shairport_volumedown = interface.get_dbus_method("VolumeDown")


def make_handler(label):
    def handle_button():
        if label == "X":
            shairport_next()
            print("RemoteControl: Next")
        elif label == "Y":
            shairport_volumeup()
            print("RemoteControl: VolumeUp")
        elif label == "A":
            shairport_playpause()
            print("RemoteControl: PlayPause")
        elif label == "B":
            shairport_volumedown()
            print("RemoteControl: VolumeDown")
    return handle_button


buttons = [Button(pin, pull_up=True, bounce_time=0.25) for pin in BUTTON_PINS]
for button, label in zip(buttons, LABELS):
    button.when_pressed = make_handler(label)

signal.pause()
