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

        # Discard stale serial data left from boot messages or an earlier
        # transaction before issuing a new command.
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

            if not response:
                continue

            # Firmware command-handler diagnostics are not part of the
            # machine-readable DUT protocol.
            if response.startswith("DEBUG"):
                continue

            # ESP-IDF logging may appear between the command request and
            # the actual DUT protocol response. Ignore these diagnostic
            # records and continue reading.
            #
            # Examples:
            #   I (8720) twai_test: TWAI self-test passed
            #   W (1000) component: warning
            #   E (2000) spi_test: SPI loopback data mismatch
            #
            # The authoritative protocol response follows separately,
            # for example CAN_SELF_TEST=PASS or SPI_LOOPBACK=FAIL.
            if response.startswith(
                ("I (", "W (", "E (", "D (", "V (")
            ):
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

    def scan_i2c(self) -> int:
        """
        Scan the DUT I2C bus.

        Returns the number of I2C peripherals detected by the
        ESP32 I2C master.
        """

        response = self._send_command("I2C_SCAN")

        if not response.startswith("I2C_DEVICES="):
            raise ProtocolError(
                f"Unexpected I2C_SCAN response: {response}"
            )

        value = response.split("=", 1)[1]

        try:
            device_count = int(value)

        except ValueError as exc:
            raise ProtocolError(
                f"Invalid I2C device count: {value}"
            ) from exc

        if device_count < 0:
            raise ProtocolError(
                f"Invalid I2C device count: {device_count}"
            )

        return device_count

    def spi_loopback(self) -> bool:
        """
        Run the DUT physical SPI loopback test.

        The firmware transmits a known byte pattern on MOSI and
        verifies that the same data is received on MISO.
        """

        response = self._send_command("SPI_LOOPBACK")

        if response == "SPI_LOOPBACK=PASS":
            return True

        if response == "SPI_LOOPBACK=FAIL":
            return False

        raise ProtocolError(
            f"Unexpected SPI_LOOPBACK response: {response}"
        )

    def uart_loopback(self) -> bool:
        """
        Run the DUT physical UART loopback test.

        The firmware transmits a known byte pattern on UART2 TX
        and verifies that the same data is received on UART2 RX.
        """

        response = self._send_command("UART_LOOPBACK")

        if response == "UART_LOOPBACK=PASS":
            return True

        if response == "UART_LOOPBACK=FAIL":
            return False

        raise ProtocolError(
            f"Unexpected UART_LOOPBACK response: {response}"
        )

    def can_self_test(self) -> bool:
        """
        Run the DUT TWAI/CAN logic-level self-test.

        The firmware transmits a known CAN frame through the ESP32
        TWAI controller and verifies the received frame.
        """

        response = self._send_command("CAN_SELF_TEST")

        if response == "CAN_SELF_TEST=PASS":
            return True

        if response == "CAN_SELF_TEST=FAIL":
            return False

        raise ProtocolError(
            f"Unexpected CAN_SELF_TEST response: {response}"
        )

    def send_raw_command(self, command: str) -> str:
        """Send a raw DUT protocol command."""

        return self._send_command(command)