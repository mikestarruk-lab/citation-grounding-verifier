"""Atomic, cross-process reservations; interrupted calls retain their reservation."""

import json
import math
import os
import uuid
from pathlib import Path

from filelock import FileLock

from .domain import VerifyError


class Budget:
    def __init__(self, path: Path, limit: float = 20):
        if not math.isfinite(limit) or limit <= 0 or limit > 20:
            raise ValueError("This project's budget must be greater than zero and at most $20")
        self.path, self.limit = path, limit
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self):
        if not self.path.exists():
            return {"spent_usd": 0.0, "reservations": {}}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        values = [data["spent_usd"], *data["reservations"].values()]
        if any(not math.isfinite(v) or v < 0 for v in values):
            raise ValueError("Invalid budget ledger")
        return data

    def _write(self, data):
        temp = self.path.with_name(self.path.name + ".tmp")
        temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(temp, self.path)

    def reserve(self, maximum: float) -> str:
        if not math.isfinite(maximum) or maximum <= 0:
            raise ValueError("Reservation must be finite and positive")
        with FileLock(str(self.path) + ".lock", timeout=1):
            data = self._read()
            if data["spent_usd"] + sum(data["reservations"].values()) + maximum > self.limit:
                raise VerifyError("budget_exhausted", "Project API budget is exhausted", 503)
            key = uuid.uuid4().hex
            data["reservations"][key] = maximum
            self._write(data)
            return key

    def settle(self, key: str, actual: float):
        with FileLock(str(self.path) + ".lock", timeout=1):
            data = self._read()
            reserved = data["reservations"].pop(key)
            if not math.isfinite(actual) or actual < 0 or actual > reserved:
                raise ValueError(
                    "Reported cost exceeds the reservation; audit the price configuration"
                )
            data["spent_usd"] += actual
            self._write(data)

    def snapshot(self):
        with FileLock(str(self.path) + ".lock", timeout=1):
            return self._read()
