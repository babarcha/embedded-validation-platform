from validation.device.base import Device
from validation.device.models import DeviceInfo


class SimulatedDevice(Device):
    """Deterministic simulated DUT used for software validation."""

    def __init__(self):
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def _require_connection(self) -> None:
        if not self._connected:
            raise RuntimeError("Device is not connected")

    def ping(self) -> bool:
        self._require_connection()
        return True

    def get_info(self) -> DeviceInfo:
        self._require_connection()

        return DeviceInfo(
            model="ESP32-DUT",
            firmware_version="1.0.0",
        )

    def read_temperature(self) -> float:
        self._require_connection()
        return 23.45

    def send_raw_command(self, command: str) -> str:
        self._require_connection()

        if command == "PING":
            return "OK"

        return "ERROR=UNKNOWN_COMMAND"