import time

import serial

from validation.device.base import Device
from validation.device.models import DeviceInfo
from validation.device.exceptions import (
    DeviceConnectionError,
    DeviceTimeoutError,
    ProtocolError,
)


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
        """Open the serial connection and verify that the DUT is responsive."""

        if self._serial is not None and self._serial.is_open:
            return

        self._serial = self._open_serial()

        # ESP32 may have produced boot messages before the connection
        # was established. Discard those messages before beginning the
        # DUT command protocol.
        self._serial.reset_input_buffer()

        for _ in range(self._ready_attempts):
            try:
                if self.ping():
                    return

            except DeviceTimeoutError:
                pass

            time.sleep(self._retry_delay)

        self.disconnect()

        raise DeviceTimeoutError(
            f"DUT on {self._port} did not become ready "
            f"after {self._ready_attempts} attempts"
        )

    def disconnect(self) -> None:
        """Close the serial connection."""

        if self._serial is not None and self._serial.is_open:
            self._serial.close()

    def _require_connection(self) -> None:
        """Ensure that a serial connection is currently available."""

        if self._serial is None or not self._serial.is_open:
            raise DeviceConnectionError(
                "Device is not connected"
            )

    def _send_command(self, command: str) -> str:
        """
        Send one DUT command and return one protocol response.

        Diagnostic messages are ignored so that the validation layer
        receives only DUT protocol responses.
        """

        self._require_connection()

        # Remove stale data left from boot output or an earlier
        # transaction.
        self._serial.reset_input_buffer()

        request = f"{command}\n".encode("utf-8")

        self._serial.write(request)
        self._serial.flush()

        deadline = time.monotonic() + self._timeout

        while time.monotonic() < deadline:
            response = (
                self._serial.readline()
                .decode("utf-8", errors="replace")
                .strip()
            )

            # No complete line received yet.
            if not response:
                continue

            # Firmware diagnostic output is not part of the DUT
            # command protocol.
            if response.startswith("DEBUG"):
                continue

            return response

        raise DeviceTimeoutError(
            f"No response received for command: {command}"
        )

    def ping(self) -> bool:
        """Check whether the DUT responds to the PING command."""

        return self._send_command("PING") == "OK"

    def get_info(self) -> DeviceInfo:
        """Read DUT model and firmware identification."""

        response = self._send_command("GET_INFO")

        if not response.startswith("MODEL="):
            raise ProtocolError(
                f"Unexpected GET_INFO response: {response}"
            )

        fields = {}

        try:
            for item in response.split(";"):
                key, value = item.split("=", 1)
                fields[key] = value

            model = fields["MODEL"]
            firmware_version = fields["FW"]

        except (ValueError, KeyError) as exc:
            raise ProtocolError(
                f"Invalid GET_INFO response: {response}"
            ) from exc

        return DeviceInfo(
            model=model,
            firmware_version=firmware_version,
        )

    def read_temperature(self) -> float:
        """Read the DUT temperature and return degrees Celsius."""

        response = self._send_command("GET_TEMP")

        if not response.startswith("TEMP_CDEG="):
            raise ProtocolError(
                f"Unexpected GET_TEMP response: {response}"
            )

        value = response.split("=", 1)[1]

        try:
            centidegrees = int(value)

        except ValueError as exc:
            raise ProtocolError(
                f"Invalid temperature value: {value}"
            ) from exc

        return centidegrees / 100.0

    def send_raw_command(self, command: str) -> str:
        """Send a raw DUT protocol command."""

        return self._send_command(command)