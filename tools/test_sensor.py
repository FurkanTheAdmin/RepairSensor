#!/usr/bin/env python3
"""Manually test a single HC-SR04 sensor and print live distance readings.

Stop the systemd service first so it doesn't fight over the same GPIO pins:
    sudo systemctl stop slot-monitor

Usage:
    python3 tools/test_sensor.py --trig 17 --echo 27
"""

import argparse
import time

from gpiozero import DistanceSensor

parser = argparse.ArgumentParser()
parser.add_argument("--trig", type=int, required=True, help="BCM pin number for TRIG")
parser.add_argument("--echo", type=int, required=True, help="BCM pin number for ECHO")
parser.add_argument("--max-distance", type=float, default=2.0, help="meters")
args = parser.parse_args()

sensor = DistanceSensor(echo=args.echo, trigger=args.trig, max_distance=args.max_distance)
print(f"TRIG=BCM{args.trig} ECHO=BCM{args.echo}  (Ctrl+C ile durdur)")

try:
    while True:
        print(f"{sensor.distance * 100:6.1f} cm")
        time.sleep(0.3)
except KeyboardInterrupt:
    pass
finally:
    sensor.close()
