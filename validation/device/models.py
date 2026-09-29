from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInfo:
    model: str
    firmware_version: str