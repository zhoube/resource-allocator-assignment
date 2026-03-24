from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Frequency:
    times: int
    period: str

    @classmethod
    def from_value(cls, payload: Frequency | dict[str, Any]) -> Frequency:
        if isinstance(payload, cls):
            return payload
        return cls(times=int(payload["times"]), period=str(payload["period"]))

    def to_dict(self) -> dict[str, Any]:
        return {"times": self.times, "period": self.period}
