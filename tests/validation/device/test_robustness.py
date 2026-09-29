def test_device_remains_responsive_after_invalid_command(device):
    response = device.send_raw_command("THIS_COMMAND_DOES_NOT_EXIST")

    assert response == "ERROR=UNKNOWN_COMMAND"
    assert device.ping()