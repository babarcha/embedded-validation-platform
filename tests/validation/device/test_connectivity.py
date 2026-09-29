def test_device_responds_to_ping(device):
    assert device.ping()