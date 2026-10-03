import pytest


@pytest.mark.hil
def test_spi_loopback(device):
    """
    DUT must successfully transmit and receive the SPI
    loopback test pattern.
    """

    assert device.spi_loopback() is True