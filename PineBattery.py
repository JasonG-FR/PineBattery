#!/usr/bin/env python3
# coding: utf-8

import subprocess
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib


class App(object):
    """
    docstring
    """

    def __init__(self, builder):
        self.device = builder.get_object('device_id')
        self.cap_label = builder.get_object('cap_label')
        self.cap_gauge = builder.get_object('cap_gauge')
        self.voltage = builder.get_object('voltage_label')
        self.current = builder.get_object('current_label')
        self.power = builder.get_object('power_label')
        self.temperature = builder.get_object('temperature_label')
        self.health = builder.get_object('health_label')
        self.voltage_now = 0
        self.current_now = 0
        self.path = "/sys/class/power_supply/axp20x-battery"

        # Start the auto-updater in the background with a 1s interval
        GLib.timeout_add(interval=1000, function=self.updateValues)

    def updateValues(self):
        self.update_capacity()
        self.update_voltage()
        self.update_current()
        self.update_power()
        self.update_temperature()
        self.update_health()

    def update_capacity(self):
        capacity = int(cat(f"{self.path}/capacity"))
        self.cap_label.set_text(f"{capacity} %")
        self.cap_gauge.set_value(capacity)

    def update_voltage(self):
        voltage = int(cat(f"{self.path}/voltage_ocv")) / 1000000
        self.voltage.set_text(f"{voltage:.3f} V")
        self.voltage_now = int(cat(f"{self.path}/voltage_now")) / 1000000

    def update_current(self):
        current = int(cat(f"{self.path}/current_now")) / 1000000
        self.current.set_text(f"{current:.3f} A")
        self.current_now = current

    def update_power(self):
        power = self.voltage_now * self.current_now
        self.power.set_text(f"{power:.3f} W")

    def update_temperature(self):
        # TODO : Is there even a sensor that can read this value?
        pass

    def update_health(self):
        health = cat(f"{self.path}/health")
        self.power.set_text(health)


def cat(path):
    task = subprocess.Popen(["cat", path], stdout=subprocess.PIPE)
    for item in task.stdout:
        return item.decode("utf-8").strip()


builder = Gtk.Builder()
builder.add_from_file('UI.glade')  

window = builder.get_object('main_window')
window.connect('delete-event', Gtk.main_quit)

app = App(builder)

window.show_all()
Gtk.main()