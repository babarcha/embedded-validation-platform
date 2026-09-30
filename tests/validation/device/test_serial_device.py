import pytest

from validation.device.serial_device import SerialDevice


class DelayedReadySerial:
    """Serial fake that becomes responsive after initial startup noise."""

    is_open = True

    def __init__(self):
        self.attempt = 0

    def write(self, data: bytes) -> int:
        self.attempt += 1
        return len(data)

    def readline(self) -> bytes:
        if self.attempt < 2:
            return b""
        return b"OK\n"

    def reset_input_buffer(self) -> None:
        pass

    def close(self) -> None:
        self.is_open = False


class FakeSerial:
    """Minimal serial-port fake that simulates a non-responsive DUT."""

    is_open = True

    def write(self, data: bytes) -> int:
        return len(data)

    def readline(self) -> bytes:
        return b""

    def reset_input_buffer(self) -> None:
        pass

    def close(self) -> None:
        self.is_open = False


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


@pytest.mark.unit
def test_connect_retries_until_dut_is_ready(monkeypatch):
    fake_serial = DelayedReadySerial()
    device = SerialDevice(port="FAKE")

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
        ready_attempts=3,
        retry_delay=0,
    )

    monkeypatch.setattr(
        device,
        "_open_serial",
        lambda: fake_serial,
    )

    with pytest.raises(
        TimeoutError,
        match="DUT on FAKE did not become ready after 3 attempts",
    ):
        device.connect()

    assert fake_serial.is_open is False
