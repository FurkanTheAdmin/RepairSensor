"""HC-SR04 slot monitoring: reads 4 distance sensors and tracks, per slot,
whether it is occupied and for how long.
"""

import os
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

import config

# Must be set before gpiozero is imported.
os.environ.setdefault("GPIOZERO_PIN_FACTORY", config.PIN_FACTORY)

from gpiozero import DistanceSensor  # noqa: E402


@dataclass
class SlotState:
    id: int
    name: str
    occupied: bool = False
    distance_m: Optional[float] = None
    since: Optional[float] = None  # time.time() when it became occupied
    _pending: bool = field(default=False, repr=False)
    _pending_count: int = field(default=0, repr=False)

    def to_dict(self):
        elapsed = int(time.time() - self.since) if self.occupied and self.since else 0
        return {
            "id": self.id,
            "name": self.name,
            "occupied": self.occupied,
            "distance_cm": round(self.distance_m * 100, 1) if self.distance_m is not None else None,
            "elapsed_seconds": elapsed,
        }


class SlotMonitor:
    """Owns the 4 HC-SR04 sensors and a background thread that keeps
    SlotState up to date. Thread-safe reads via get_states()."""

    def __init__(self, slots_config=config.SLOTS):
        self._lock = threading.Lock()
        self._states = {}
        self._sensors = {}
        for slot in slots_config:
            self._states[slot["id"]] = SlotState(id=slot["id"], name=slot["name"])
            self._sensors[slot["id"]] = DistanceSensor(
                echo=slot["echo"],
                trigger=slot["trig"],
                max_distance=config.MAX_DISTANCE_M,
                queue_len=5,
            )
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=2)
        for sensor in self._sensors.values():
            sensor.close()

    def get_states(self):
        with self._lock:
            return [self._states[sid].to_dict() for sid in sorted(self._states)]

    def _run(self):
        while not self._stop.is_set():
            for sid, sensor in self._sensors.items():
                try:
                    distance_m = sensor.distance
                except Exception:
                    distance_m = None
                self._update_slot(sid, distance_m)
            self._stop.wait(config.POLL_INTERVAL_S)

    def _update_slot(self, sid, distance_m):
        with self._lock:
            state = self._states[sid]
            state.distance_m = distance_m

            raw_occupied = distance_m is not None and distance_m < config.OCCUPIED_THRESHOLD_M

            if raw_occupied == state.occupied:
                state._pending_count = 0
                return

            if raw_occupied == state._pending:
                state._pending_count += 1
            else:
                state._pending = raw_occupied
                state._pending_count = 1

            if state._pending_count >= config.DEBOUNCE_READINGS:
                state.occupied = raw_occupied
                state.since = time.time() if raw_occupied else None
                state._pending_count = 0
