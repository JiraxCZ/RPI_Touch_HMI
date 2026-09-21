# RPI Touch HMI (720x720)

A touch-friendly Raspberry Pi application for controlling four relays using a 720x720 display.

## Features

- Four large touch controls in a 2x2 layout
- Explicit ON/OFF state handling for reliable touch control
- Red OFF and green ON indicators
- Configurable active-low / active-high relay output
- Safe GPIO cleanup when the application exits

## GPIO mapping (BCM)

| Relay | GPIO | Physical pin |
| --- | --- | --- |
| 1 | GPIO17 | 11 |
| 2 | GPIO27 | 13 |
| 3 | GPIO22 | 15 |
| 4 | GPIO23 | 16 |

The default is an active-low relay board. For an active-high board, set `ACTIVE_LOW = False` in `main.py`.

## Install on Raspberry Pi

```bash
cd ~/RPI_Touch_HMI
python3 -m venv ~/hmi-venv
source ~/hmi-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Manual start

```bash
cd ~/RPI_Touch_HMI
source ~/hmi-venv/bin/activate
python main.py
```

## Test relay logic without hardware

```bash
cd ~/RPI_Touch_HMI
source ~/hmi-venv/bin/activate
python -m unittest discover -s tests
```

## Autostart with systemd

```bash
sudo cp ~/RPI_Touch_HMI/hmi.service /etc/systemd/system/hmi.service
sudo systemctl daemon-reload
sudo systemctl enable hmi.service
sudo systemctl restart hmi.service
```
