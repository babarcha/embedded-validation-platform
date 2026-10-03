import pytest


@pytest.mark.hil
def test_uart_loopback(device):
    """
    DUT must successfully transmit and receive the UART
    loopback test pattern.
    """

    assert device.uart_loopback() is True