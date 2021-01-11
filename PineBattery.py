#!/usr/bin/env python3
# coding: utf-8

import subprocess
import json
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
        self.cpu0 = builder.get_object('cpu0_label')
        self.gpu0 = builder.get_object('gpu0_label')
        self.gpu1 = builder.get_object('gpu1_label')
        self.health = builder.get_object('health_label')
        self.voltage_now = 0
        self.current_now = 0
        self.path = "/sys/class/power_supply/axp20x-battery"
        self.discharging = True

        self.updateValues()

        # Start the auto-updater in the background with a 1s interval
        GLib.timeout_add(interval=1000, function=self.updateValues)

    def updateValues(self):
        self.update_capacity()
        self.update_status()
        self.update_voltage()
        self.update_current()
        self.update_power()
        self.update_temperatures()
        self.update_health()
        return True

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
        current = -current if self.discharging else current
        self.current.set_text(f"{current:.3f} A")
        self.current_now = current

    def update_power(self):
        power = self.voltage_now * self.current_now
        self.power.set_text(f"{power:.3f} W")

    def update_temperatures(self):
        chips = ["cpu0_thermal-virtual-0", "gpu0_thermal-virtual-0", 
                 "gpu1_thermal-virtual-0"]
        labels = [self.cpu0, self.gpu0, self.gpu1]

        data = sensors()

        for chip, label in zip(chips, labels):
            label.set_text(f'{data[chip]["temp1"]["temp1_input"]} °C')

    def update_health(self):
        health = cat(f"{self.path}/health")
        self.health.set_text(health)

    def update_status(self):
        status = cat(f"{self.path}/status")
        if status == "Discharging":
            self.discharging = True
        else:
            self.discharging = False


def cat(path):
    task = subprocess.Popen(["cat", path], stdout=subprocess.PIPE)
    for item in task.stdout:
        return item.decode("utf-8").strip()


def sensors():
    task = subprocess.Popen(["sensors", "-j"], stdout=subprocess.PIPE)
    buffer = ""
    for item in task.stdout:
        buffer += item.decode("utf-8").strip()

    return json.loads(buffer)


def main():
    builder = Gtk.Builder()
    builder.add_from_file('UI.glade')

    window = builder.get_object('main_window')
    window.connect('delete-event', Gtk.main_quit)

    builder.connect_signals(App(builder))

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()

# TODO: - Either remove the temperature or add all of them
#       - Colors for the gauge, status charging/discharging...