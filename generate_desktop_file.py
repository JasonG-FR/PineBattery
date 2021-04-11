#!/bin/python3
# coding: utf-8

from PineBattery import abs_path


def generate_desktop_file():
    with open("PineBattery.desktop", "w") as dkp_file:
        # Get the application directory
        exec_path = abs_path('PineBattery.py')

        parameters = {"Categories": "Utility;Application;",
                      "Comment": "Battery Monitor for Pine64 Devices",
                      "Exec": f"python3 '{exec_path}'",
                      "GenericName": "",
                      "Icon": "battery", 
                      "MimeType": "",
                      "Name": "PineBattery",
                      "Path": "",
                      "StartupNotify": "true",
                      "Terminal": "false", 
                      "TerminalOptions": "",
                      "Type": "Application",
                      "Version": "1.0",
                      "X-DBUS-ServiceName": "",
                      "X-DBUS-StartupType": "",
                      "X-KDE-SubstituteUID": "false", 
                      "X-KDE-Username": ""}

        dkp_file.write("[Desktop Entry]\n")
        for p in parameters:
            dkp_file.write(f"{p}={parameters[p]}\n")


if __name__ == "__main__":
    generate_desktop_file()
