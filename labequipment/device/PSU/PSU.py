from labequipment.device import device
import abc
from abc import abstractmethod

# TODO: fix this mess!!!!

class PSU(device.device, metaclass=abc.ABCMeta):

    def set_voltage(self, voltage, output_nr):
        print("setVoltage ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def get_voltage(self, output_nr):
        print("getVoltage ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def get_measured_voltage(self, output_nr):
        print("getMeasuredVoltage ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def set_current(self, current, output_nr):
        print("setCurrent ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def get_current(self, output_nr):
        print("getCurrent ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def get_measured_current(self, output_nr):
        print("getMeasuredCurrent ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def enable_output(self, output_nr):
        print("enabelOutput ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def disable_output(self, output_nr):
        print("disableOutput ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def get_output_state(self, output_nr):
        print("getOutputState ERROR NOT IMPLENTED")
        raise NotImplementedError

    def get_cc_status_live(self, output_nr):
        print("getCCStatusLive ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def get_cv_status_live(self, output_nr):
        print("getCVStatusLive ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def lock_panel(self):
        print("lockPanel ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def set_local(self):
        print("setLocal ERROR NOT IMPLEMENTED")
        raise NotImplementedError
