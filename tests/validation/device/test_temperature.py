import pytest


@pytest.mark.hil
def test_temperature_is_within_valid_range(device):
    temperature = device.read_temperature()

    assert isinstance(temperature, (int, float))
    assert -10.0 <= temperature <= 60.0
