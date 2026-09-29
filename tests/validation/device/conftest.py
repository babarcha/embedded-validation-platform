import os

import pytest

from validation.device.serial_device import SerialDevice
from validation.device.simulator import SimulatedDevice


@pytest.fixture
def device():
    device_type = os.getenv("DEVICE_TYPE", "simulator")

    if device_type == "serial":
        port = os.getenv("DEVICE_PORT", "COM3")
        dut = SerialDevice(port=port)
    else:
        dut = SimulatedDevice()

    dut.connect()

    yield dut

    dut.disconnect()
