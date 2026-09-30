class DeviceError(Exception):
    """Base exception for device validation failures."""


class DeviceConnectionError(DeviceError, RuntimeError):
    """Raised when the DUT is not connected or cannot be used."""


class DeviceTimeoutError(DeviceError, TimeoutError):
    """Raised when the DUT does not respond within the expected time."""


class ProtocolError(DeviceError, ValueError):
    """Raised when the DUT returns an invalid protocol response."""
