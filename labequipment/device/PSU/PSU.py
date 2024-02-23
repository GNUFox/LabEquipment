from labequipment.device import device
import abc
from abc import abstractmethod


class PSU(device.device, metaclass=abc.ABCMeta):

    @abstractmethod
    def set_voltage(self, voltage, output_nr):
        raise NotImplementedError

    @abstractmethod
    def get_voltage(self, output_nr):
        raise NotImplementedError

    def get_measured_voltage(self, output_nr):
        raise NotImplementedError

    @abstractmethod
    def set_current(self, current, output_nr):
        raise NotImplementedError

    @abstractmethod
    def get_current(self, output_nr):
        raise NotImplementedError

    def get_measured_current(self, output_nr):
        raise NotImplementedError

    @abstractmethod
    def enable_output(self, output_nr):
        raise NotImplementedError

    @abstractmethod
    def disable_output(self, output_nr):
        raise NotImplementedError

    @abstractmethod
    def get_output_state(self, output_nr):
        raise NotImplementedError

    def get_cc_status_live(self, output_nr):  # TODO: decide if these methods are needed here
        raise NotImplementedError

    def get_cv_status_live(self, output_nr):  # TODO: decide if these methods are needed here
        raise NotImplementedError

    def lock_panel(self):  # TODO: decide if these methods are needed here
        raise NotImplementedError

    def set_local(self):  # TODO: decide if these methods are needed here
        raise NotImplementedError
