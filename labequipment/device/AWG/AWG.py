from labequipment.device import device
import abc
from abc import abstractmethod


class AWG(device.device, metaclass=abc.ABCMeta):
    """ Arbitrary Waveform generator parent class"""

    @abstractmethod
    def set_frequency(self, frequency: float, output_nr: int) -> None:
        pass

    @abstractmethod
    def get_frequency(self, output_nr: float) -> float:
        pass

    def set_waveform(self, waveform: float, output_nr: int) -> None:
        pass

    def get_waveform(self, output_nr: int) -> int:
        pass

    @abstractmethod
    def set_amplitude(self, amp: float, output_nr: int) -> None:
        pass

    @abstractmethod
    def get_amplitude(self, output_nr: int) -> float:
        pass

    def set_offset(self, offset: int, output_nr: int) -> None:
        pass

    def get_offset(self, output_nr: int) -> float:
        pass

    @abstractmethod
    def enable_output(self, output_nr: int) -> None:
        pass

    @abstractmethod
    def disable_output(self, output_nr: int) -> None:
        pass

    @abstractmethod
    def get_output_state(self, output_nr: int) -> bool:
        pass
