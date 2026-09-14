"""Slot / sensor configuration.

Wire each HC-SR04 as:
  VCC  -> Pi 5V
  GND  -> Pi GND
  TRIG -> Pi GPIO (3.3V logic, safe to drive directly)
  ECHO -> voltage divider (e.g. 1k + 2k resistors) -> Pi GPIO

HC-SR04's ECHO pin outputs 5V. The Pi's GPIO inputs are only 3.3V tolerant.
Skipping the voltage divider WILL damage the GPIO pin over time.
"""

import os

# BCM pin numbers. Change these to match actual wiring.
SLOTS = [
    {"id": 1, "name": "Slot 1", "trig": 17, "echo": 27},
    {"id": 2, "name": "Slot 2", "trig": 22, "echo": 23},
    {"id": 3, "name": "Slot 3", "trig": 5, "echo": 6},
    {"id": 4, "name": "Slot 4", "trig": 13, "echo": 19},
]

# For testing with fewer than 4 sensors physically wired, restrict which
# slots are active without editing this file, e.g.:
#   ENABLED_SLOT_IDS=1 python3 app.py
_enabled_ids = os.environ.get("ENABLED_SLOT_IDS")
if _enabled_ids:
    _ids = {int(x) for x in _enabled_ids.split(",")}
    SLOTS = [s for s in SLOTS if s["id"] in _ids]

# A slot counts as "an object is in range" when the measured distance drops
# below this.
OCCUPIED_THRESHOLD_M = float(os.environ.get("OCCUPIED_THRESHOLD_M", "0.5"))

# HC-SR04 max reliable range is ~4m; readings beyond this are discarded.
MAX_DISTANCE_M = float(os.environ.get("MAX_DISTANCE_M", "2.0"))

# An object must be continuously within OCCUPIED_THRESHOLD_M for this many
# seconds before the slot is marked occupied and the repair timer starts.
# Filters out someone briefly walking past the sensor.
CONFIRM_SECONDS = float(os.environ.get("CONFIRM_SECONDS", "20"))

# Once occupied, the object must be continuously out of range for this many
# seconds before the slot is marked free again (timer resets to 0). Short,
# just enough to filter single noisy readings.
EXIT_CONFIRM_SECONDS = float(os.environ.get("EXIT_CONFIRM_SECONDS", "2"))

# How many past repair durations to keep and show per slot.
HISTORY_SIZE = int(os.environ.get("HISTORY_SIZE", "3"))

# How often (seconds) the background thread polls all sensors.
POLL_INTERVAL_S = float(os.environ.get("POLL_INTERVAL_S", "0.5"))

# gpiozero pin factory. On the Pi use "lgpio" (default). For local
# development on a machine with no GPIO hardware, set:
#   GPIOZERO_PIN_FACTORY=mock
# before running app.py.
PIN_FACTORY = os.environ.get("GPIOZERO_PIN_FACTORY", "lgpio")

WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "8080"))
