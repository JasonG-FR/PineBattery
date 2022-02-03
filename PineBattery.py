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

    def __init__(self, builder, ravg=10, interval=500):
        self.device = builder.get_object('device_id')
        self.cap_label = builder.get_object('cap_label')
        self.cap_gauge = builder.get_object('cap_gauge')
        self.voltage = builder.get_object('voltage_label')
        self.current = builder.get_object('current_label')
        self.power = builder.get_object('power_label')
        self.sensor0 = builder.get_object('sensor0_value')
        self.sensor1 = builder.get_object('sensor1_value')
        self.sensor2 = builder.get_object('sensor2_value')
        self.health = builder.get_object('health_label')
        self.status = builder.get_object('status_label')
        self.load = builder.get_object('load_label')
        self.uptime = builder.get_object('uptime_label')

        self.voltage_now = 0
        self.current_now = 0
        self.path = get_battery_path()
        self.voltage_max_path = f"{self.path}/{get_voltage_max_path(self.path)}"

        self.discharging = True
        self.ravg = ravg
        self.capacity_values = []
        self.voltage_values = []
        self.voltage_now_values = []
        self.current_values = []

        self.temperature_values = init_temp_sensors()
        sensor_labels = ['sensor0_label', 'sensor1_label', 'sensor2_label']
        sensor_values = ['sensor0_value', 'sensor1_value', 'sensor2_value']
        sensor_names = self.temperature_values.keys()

        # Set the sensor labels to match 'sensors' output
        for label, name in zip(sensor_labels[:len(sensor_names)], sensor_names):
            builder.get_object(label).set_text(f"{name.split('_')[0]} :")
        # Blanks the sensor labels and values if not available
        for label, value in zip(sensor_labels[len(sensor_names):],
                                sensor_values[len(sensor_names):]):
            builder.get_object(label).set_text("")
            builder.get_object(value).set_text("")

        self.updateValues()

        # Start the auto-updater in the background with the selected interval
        GLib.timeout_add(interval=interval, function=self.updateValues)

    def calc_ravg(self, attr_name, value):
        values = getattr(self, attr_name)
        while len(values) >= self.ravg:
            del(values[0])

        values.append(value)
        setattr(self, attr_name, values)
        
        return sum(values) / len(values)

    def calc_ravg_temp(self, chip, temp):
        temps = self.temperature_values[chip]
        while len(temps) >= self.ravg:
            del(temps[0])

        temps.append(temp)
        self.temperature_values[chip] = temps
        
        return sum(temps) / len(temps)

    def updateValues(self):
        self.update_capacity()
        self.update_status()
        self.update_voltage()
        self.update_current()
        self.update_power()
        self.update_temperatures()
        self.update_health()
        self.update_load()
        self.update_uptime()

        return True  # Auto-updater stops if function doesn't return True

    def update_capacity(self):
        capacity = int(cat(f"{self.path}/capacity"))
        ravg_capacity = self.calc_ravg("capacity_values", capacity)
        self.cap_label.set_text(f"{ravg_capacity:.0f} %")
        self.cap_gauge.set_value(ravg_capacity)

    def update_voltage(self):
        voltage = int(cat(self.voltage_max_path)) / 1000000
        ravg_voltage = self.calc_ravg("voltage_values", voltage)
        self.voltage.set_text(f"{ravg_voltage:.3f} V")
        
        voltage_now = int(cat(f"{self.path}/voltage_now")) / 1000000
        self.voltage_now = self.calc_ravg("voltage_now_values", voltage_now)

    def update_current(self):
        current = int(cat(f"{self.path}/current_now")) / 1000000
        current = -current if self.discharging else current
        ravg_current = self.calc_ravg("current_values", current)
        self.current.set_text(f"{ravg_current:.3f} A")
        self.current_now = ravg_current

    def update_power(self):
        power = self.voltage_now * self.current_now
        self.power.set_text(f"{power:.3f} W")

    def update_temperatures(self):
        chips = self.temperature_values.keys()
        labels = [self.sensor0, self.sensor1, self.sensor2]

        data = sensors()

        for chip, label in zip(chips, labels[:len(chips)]):
            temp = data[chip]["temp1"]["temp1_input"]
            ravg_temp = self.calc_ravg_temp(chip, temp)
            label.set_text(f'{ravg_temp:.1f} °C')

    def update_health(self):
        health = cat(f"{self.path}/health")
        self.health.set_text(f"Health : {health}")

    def update_status(self):
        status = cat(f"{self.path}/status")
        if status == "Discharging":
            self.discharging = True
        else:
            self.discharging = False
        self.status.set_text(status)

    def update_load(self):
        load = cat("/proc/loadavg")[:14].replace(" ", ", ")
        self.load.set_text(f"Load : {load}")

    def update_uptime(self):
        self.uptime.set_text(f"Uptime : {uptime()[3:]}")  # Removes "up "


def abs_path(filename):
    script_path = "/".join(__file__.split("/")[:-1])
    return f"{script_path}/{filename}"


def cat(path):
    task = subprocess.Popen(["cat", path], stdout=subprocess.PIPE)
    for item in task.stdout:
        return item.decode("utf-8").strip()


def get_battery_path():
    task = subprocess.Popen(["ls", "/sys/class/power_supply/"], stdout=subprocess.PIPE)
    for item in task.stdout:
        d_item = item.decode("utf-8").strip()
        if "battery" in d_item:
            return f"/sys/class/power_supply/{d_item}"


def ls(path):
    task = subprocess.Popen(["ls", path], stdout=subprocess.PIPE)
    return [item.decode("utf-8").strip() for item in task.stdout]
        

def get_voltage_max_path(battery_path):
    parameters = ls(battery_path)
    if "voltage_ocv" in parameters:
        # It's a PinePhone or a PineTab
        return "voltage_ocv"
    elif "voltage_max" in parameters:
        # It's a PinePhone Pro
        return "voltage_max"
    else:
        # It's something else (PineBookPro)
        return "voltage_now"


def uptime():
    task = subprocess.Popen(["uptime", "-p"], stdout=subprocess.PIPE)
    for item in task.stdout:
        return item.decode("utf-8").strip()


def sensors():
    task = subprocess.Popen(["sensors", "-j"], stdout=subprocess.PIPE)
    buffer = ""
    for item in task.stdout:
        buffer += item.decode("utf-8").strip()

    return json.loads(buffer)


def init_temp_sensors():
    chips = [chip for chip in sensors() if "cpu" in chip or "gpu" in chip]
    return {chip:[] for chip in chips[:3]}  # [:3] to make sure we get max 3 sensors


def main():
    builder = Gtk.Builder()
    builder.add_from_file(abs_path('UI.glade'))

    window = builder.get_object('main_window')
    window.connect('delete-event', Gtk.main_quit) 

    builder.connect_signals(App(builder))

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
