#!/bin/bash

python3 generate_desktop_file.py
chmod +x PineBattery.desktop
cp PineBattery.desktop ~/.local/share/applications/