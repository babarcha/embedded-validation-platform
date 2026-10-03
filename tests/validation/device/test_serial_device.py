import pytest

from validation.device.exceptions import (
    DeviceConnectionError,
    DeviceTimeoutError,
    ProtocolError,
)
from validation.device.serial_device import SerialDevice


class BaseFakeSerial:
    """Minimal pyserial-compatible test double."""

    def __init__(self):
        self.is_open = True

    def write(self, data: bytes) -> int:
        return len(data)

    def reset_input_buffer(self) -> None:
        pass

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.is_open = False


class DelayedReadySerial(BaseFakeSerial):
    """Serial fake that becomes responsive after initial startup noise."""

    def __init__(self):
        super().__init__()
        self.attempt = 0

    def write(self, data: bytes) -> int:
        self.attempt += 1
        return len(data)

    def readline(self) -> bytes:
        if self.attempt < 2:
            return b""

        return b"OK\n"


class FakeSerial(BaseFakeSerial):
    """Serial fake that simulates a non-responsive DUT."""

    def readline(self) -> bytes:
        return b""


class MalformedResponseSerial(BaseFakeSerial):
    """Serial fake that returns an invalid temperature response."""

    def readline(self) -> bytes:
        return b"TEMP=abc\n"


class MissingFirmwareSerial(BaseFakeSerial):
    """Serial fake that omits the firmware field."""

    def readline(self) -> bytes:
        return b"MODEL=ESP32-DUT\n"


class InvalidTemperatureSerial(BaseFakeSerial):
    """Serial fake that returns non-numeric temperature data."""

    def readline(self) -> bytes:
        return b"TEMP_CDEG=abc\n"


class DiagnosticLogSerial(BaseFakeSerial):
    """Serial fake that emits an ESP-IDF log before the protocol response."""

    def __init__(self):
        super().__init__()
        self.responses = [
            b"I (9110) spi_test: SPI loopback passed: 8 bytes verified\n",
            b"SPI_LOOPBACK=PASS\n",
        ]

    def readline(self) -> bytes:
        if self.responses:
            return self.responses.pop(0)

        return b""


@pytest.mark.unit
def test_serial_device_raises_timeout_when_dut_does_not_respond():
    device = SerialDevice(
        port="FAKE",
        timeout=0.01,
    )
    device._serial = FakeSerial()

    with pytest.raises(
        DeviceTimeoutError,
        match="No response received for command: PING",
    ):
        device.ping()


@pytest.mark.unit
def test_serial_device_rejects_malformed_temperature_response():
    device = SerialDevice(port="FAKE")
    device._serial = MalformedResponseSerial()

    with pytest.raises(
        ProtocolError,
        match="Unexpected GET_TEMP response",
    ):
        device.read_temperature()


@pytest.mark.unit
def test_connect_retries_until_dut_is_ready(monkeypatch):
    fake_serial = DelayedReadySerial()

    device = SerialDevice(
        port="FAKE",
        timeout=0.01,
        retry_delay=0,
    )

    monkeypatch.setattr(
        device,
        "_open_serial",
        lambda: fake_serial,
    )

    device.connect()

    assert fake_serial.attempt >= 2
    assert device.ping() is True


@pytest.mark.unit
def test_connect_times_out_when_dut_never_becomes_ready(monkeypatch):
    fake_serial = FakeSerial()

    device = SerialDevice(
        port="FAKE",
        timeout=0.01,
        ready_attempts=3,
        retry_delay=0,
    )

    monkeypatch.setattr(
        device,
        "_open_serial",
        lambda: fake_serial,
    )

    with pytest.raises(
        DeviceTimeoutError,
        match="DUT on FAKE did not become ready after 3 attempts",
    ):
        device.connect()

    assert fake_serial.is_open is False


@pytest.mark.unit
def test_get_info_rejects_missing_firmware_field():
    device = SerialDevice(port="FAKE")
    device._serial = MissingFirmwareSerial()

    with pytest.raises(
        ProtocolError,
        match="Invalid GET_INFO response",
    ):
        device.get_info()


@pytest.mark.unit
def test_read_temperature_rejects_non_numeric_value():
    device = SerialDevice(port="FAKE")
    device._serial = InvalidTemperatureSerial()

    with pytest.raises(
        ProtocolError,
        match="Invalid temperature value",
    ):
        device.read_temperature()


@pytest.mark.unit
def test_command_rejected_when_device_is_not_connected():
    device = SerialDevice(port="FAKE")

    with pytest.raises(
        DeviceConnectionError,
        match="Device is not connected",
    ):
        device.ping()


@pytest.mark.unit
def test_serial_device_ignores_esp_idf_log_before_protocol_response():
    """
    ESP-IDF diagnostic logs must not be mistaken for DUT protocol responses.
    """

    device = SerialDevice(port="FAKE")
    device._serial = DiagnosticLogSerial()

    assert device.spi_loopback() is True