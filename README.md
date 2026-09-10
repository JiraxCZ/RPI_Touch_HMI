# RPI Touch HMI (720x720)

A touch-friendly Kivy application for Raspberry Pi to control **4 relays** on a **720x720 px** display.

## Features

- Fullscreen touch GUI for 720x720
- Four large relay buttons (ON/OFF)
- Color state indication (green = ON, red = OFF)
- Safe relay shutdown on app exit
- systemd service file for autostart

## Hardware

- Raspberry Pi (with GPIO)
- Touch display 720x720
- 4-channel relay module

## GPIO Mapping (BCM)

- Relay 1 -> GPIO17 (physical pin 11)
- Relay 2 -> GPIO27 (physical pin 13)
- Relay 3 -> GPIO22 (physical pin 15)
- Relay 4 -> GPIO23 (physical pin 16)

> The app is configured for **active-low** relay boards (`ACTIVE_LOW = True`).
> If your board is active-high, set `ACTIVE_LOW = False` in `main.py`.

## Installation

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv libatlas-base-dev

cd ~/RPI_Touch_HMI
python3 -m venv ~/hmi-venv
source ~/hmi-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run manually

```bash
source ~/hmi-venv/bin/activate
python main.py
```

## Autostart with systemd

Copy service file:

```bash
sudo cp hmi.service /etc/systemd/system/hmi.service
sudo systemctl daemon-reload
sudo systemctl enable hmi.service
sudo systemctl start hmi.service
```

Check status:

```bash
sudo systemctl status hmi.service
```
