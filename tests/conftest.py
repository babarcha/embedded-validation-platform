import pytest

from validation.device.serial_device import SerialDevice
from validation.device.simulator import SimulatedDevice


def pytest_addoption(parser):
    """Add command-line options for selecting the DUT backend."""

    parser.addoption(
        "--device",
        action="store",
        default="simulator",
        choices=("simulator", "serial"),
        help="Device backend: simulator or serial",
    )

    parser.addoption(
        "--port",
        action="store",
        default="COM3",
        help="Serial port used when --device=serial",
    )


@pytest.fixture
def device(request):
    device_type = request.config.getoption("--device")
    port = request.config.getoption("--port")

    if device_type == "serial":
        dut = SerialDevice(port=port)
    else:
        dut = SimulatedDevice()

    dut.connect()

    yield dut

    dut.disconnect()
