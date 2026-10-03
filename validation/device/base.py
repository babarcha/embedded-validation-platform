from abc import ABC, abstractmethod

from validation.device.models import DeviceInfo


class Device(ABC):
    """Abstract interface for a device under test."""

    @abstractmethod
    def connect(self) -> None:
        """Establish communication with the DUT."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close communication with the DUT."""
        pass

    @abstractmethod
    def ping(self) -> bool:
        """Return True when the DUT responds."""
        pass

    @abstractmethod
    def get_info(self) -> DeviceInfo:
        """Return DUT identification information."""
        pass

    @abstractmethod
    def read_temperature(self) -> float:
        """Return the DUT temperature in degrees Celsius."""
        pass

    @abstractmethod
    def scan_i2c(self) -> int:
        """Return the number of devices detected on the I2C bus."""
        pass

    @abstractmethod
    def spi_loopback(self) -> bool:
        """Run the DUT SPI loopback test and return whether it passed."""
        pass

    @abstractmethod
    def uart_loopback(self) -> bool:
        """Run the DUT UART loopback test and return whether it passed."""
        pass

    @abstractmethod
    def send_raw_command(self, command: str) -> str:
        """Send a raw command and return the DUT response."""
        pass