import pytest


@pytest.mark.hil
def test_can_self_test(device):
    """
    DUT must successfully transmit and receive a CAN frame
    through the TWAI logic-level loopback path.
    """

    assert device.can_self_test() is True