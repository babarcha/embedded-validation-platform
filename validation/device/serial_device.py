import time
import serial

from validation.device.base import Device
from validation.device.models import DeviceInfo


class SerialDevice(Device):
    """Physical ESP32 DUT accessed through a serial connection."""

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 2.0,
        ready_attempts: int = 5,
        retry_delay: float = 0.2,
    ):
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._ready_attempts = ready_attempts
        self._retry_delay = retry_delay
        self._serial = None

    def _open_serial(self):
        """Create and return the serial connection."""
        return serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=self._timeout,
        )

    def connect(self) -> None:
        if self._serial is not None and self._serial.is_open:
            return

        self._serial = self._open_serial()

        # Discard ESP-IDF boot messages that may already be available.
        self._serial.reset_input_buffer()

        for _ in range(self._ready_attempts):
            try:
                if self.ping():
                    return
            except TimeoutError:
                pass

            time.sleep(self._retry_delay)

        self.disconnect()
        raise TimeoutError(
            f"DUT on {self._port} did not become ready "
            f"after {self._ready_attempts} attempts"
        )

    def disconnect(self) -> None:
        if self._serial is not None and self._serial.is_open:
            self._serial.close()

    def _require_connection(self) -> None:
        if self._serial is None or not self._serial.is_open:
            raise RuntimeError("Device is not connected")

    def _send_command(self, command: str) -> str:
        self._require_connection()

        self._serial.write(f"{command}\n".encode())

        response = (
            self._serial.readline()
            .decode(errors="replace")
            .strip()
        )

        if not response:
            raise TimeoutError(
                f"No response received for command: {command}"
            )

        return response

    def ping(self) -> bool:
        return self._send_command("PING") == "OK"

    def get_info(self) -> DeviceInfo:
        response = self._send_command("GET_INFO")

        if not response.startswith("MODEL="):
            raise ValueError(
                f"Unexpected GET_INFO response: {response}"
            )

        fields = {}

        for item in response.split(";"):
            key, value = item.split("=", 1)
            fields[key] = value

        return DeviceInfo(
            model=fields["MODEL"],
            firmware_version=fields["FW"],
        )

    def read_temperature(self) -> float:
        response = self._send_command("GET_TEMP")

        if not response.startswith("TEMP_CDEG="):
            raise ValueError(
                f"Unexpected GET_TEMP response: {response}"
            )

        centidegrees = int(response.split("=", 1)[1])
        return centidegrees / 100.0

    def send_raw_command(self, command: str) -> str:
        return self._send_command(command)
