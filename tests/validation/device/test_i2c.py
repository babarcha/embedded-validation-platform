import pytest


@pytest.mark.hil
def test_i2c_bus_scan(device):
    """DUT must successfully scan the I2C bus."""

    device_count = device.scan_i2c()

    assert isinstance(device_count, int)
    assert device_count >= 0


@pytest.mark.hil
def test_i2c_bus_is_empty(device):
    """
    Current lab configuration has no I2C peripheral attached.

    The DUT should therefore report zero detected devices.
    """

    device_count = device.scan_i2c()

    assert device_count == 0