import pytest

from validation.device.serial_device import SerialDevice


class FakeSerial:
    """Minimal serial-port fake that simulates a non-responsive DUT."""

    is_open = True

    def write(self, data: bytes) -> int:
        return len(data)

    def readline(self) -> bytes:
        return b""


@pytest.mark.unit
def test_serial_device_raises_timeout_when_dut_does_not_respond():
    device = SerialDevice(port="FAKE")
    device._serial = FakeSerial()

    with pytest.raises(
        TimeoutError,
        match="No response received for command: PING",
    ):
        device.ping()


class MalformedResponseSerial:
    """Serial fake that returns an invalid temperature response."""

    is_open = True

    def write(self, data: bytes) -> int:
        return len(data)

    def readline(self) -> bytes:
        return b"TEMP=abc\n"


@pytest.mark.unit
def test_serial_device_rejects_malformed_temperature_response():
    device = SerialDevice(port="FAKE")
    device._serial = MalformedResponseSerial()

    with pytest.raises(
        ValueError,
        match="Unexpected GET_TEMP response",
    ):
        device.read_temperature()
