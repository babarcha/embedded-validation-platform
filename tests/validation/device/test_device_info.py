def test_device_reports_identification(device):
    info = device.get_info()

    assert info.model
    assert info.firmware_version