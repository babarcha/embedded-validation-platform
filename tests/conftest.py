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


def pytest_configure(config):
    """Register custom pytest markers."""

    config.addinivalue_line(
        "markers",
        "hil: functional validation tests that can run against a physical DUT",
    )

    config.addinivalue_line(
        "markers",
        "unit: software-only tests of the validation framework",
    )


@pytest.fixture(scope="session")
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
