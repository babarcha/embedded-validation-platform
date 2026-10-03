import pytest


@pytest.mark.hil
def test_device_responds_to_ping(device):
    assert device.ping()

@pytest.mark.hil
def test_repeated_device_ping(device):
    """DUT must remain responsive across repeated transactions."""

    iterations = 100

    for attempt in range(1, iterations + 1):
        assert device.ping(), (
            f"DUT failed to respond to PING "
            f"on attempt {attempt}/{iterations}"
        )	