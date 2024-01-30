from enum import Enum

from labequipment.device import device
from labequipment.framework import exceptions
import abc


class acdc(Enum):
    DC = 0
    AC = 1


class DMM(device.device, metaclass=abc.ABCMeta):

    # Simple (auto-range) measurement functions
    def capacitance(self):
        """measure capacitance with autorange and no configured resolution (standard behaviour)"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:CAP?")
            ret = self.receive_data()
        return ret

    def continuity(self):
        """measure continuity"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:CONT?")
            ret = self.receive_data()
        return ret

    # TODO: FIX THIS, use enum instead of strings for dc_ac
    def current(self, dc_ac='dc', irange='auto', res='auto'):
        """measure current with autorange and no configured resolution (standard behaviour)  

        dc_ac ['dc']:     Choose DC or AC mode, Default: dc  
        irange ['auto']:  Set current range (refer to DMM Manual for possible values), Defualt: auto  
        res ['auto']:     Set Resolution (refer to DMM Manual for possible values), Default: auto  

        __CAUTION__: using autorange could cause the circuit to be disconnected briefly

        """

        ret = 0
        mod = "DC"
        if dc_ac == 'ac':
            mod = "AC"
        elif not dc_ac == 'dc':
            raise exceptions.InvalidDeviceParameter

        command = f"MEAS:CURR:{mod}?"

        if not irange == "auto":
            # irange is specified
            if isinstance(irange, int) or (
                    isinstance(irange, str) and (irange.upper() == "MIN" or irange.upper() == "MAX")):
                command += f" {irange}"
            else:
                raise exceptions.InvalidDeviceParameter

            if not res == "auto":
                if isinstance(res, int) or (isinstance(res, str) and (res.upper() == "MIN" or res.upper() == "MAX")):
                    command += f",{res}"
                else:
                    raise exceptions.InvalidDeviceParameter

        elif not res == "auto":
            # if resolution is set, vrange MUST also be set
            raise exceptions.InvalidDeviceParameter
        else:
            # Both are auto
            command += " AUTO"

        with self._lock:
            self.send_command(command)
            ret = float(self.receive_data())

        return ret

    def diode(self):
        """measure diode"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:DIOD?")
            ret = self.receive_data()
        return ret

    def frequency(self):
        """measure frequency with autorange and no configured resolution (standard behaviour)"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:FREQ?")
            ret = self.receive_data()

        return ret

    def fResistance(self):
        """measure fResistance with autorange and no configured resolution (standard behaviour)"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:FRES? AUTO")
            ret = self.receive_data()

        return ret

    def period(self):
        """measure period with autorange and no configured resolution (standard behaviour)"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:PER?")
            ret = self.receive_data()

        return ret

    def resistance(self):
        """measure resistance with autorange and no configured resolution (standard behaviour)"""
        ret = 0
        with self._lock:
            self.send_command("MEAS:RES? AUTO")
            ret = self.receive_data()

        return ret

    def temperature(self):
        """measure temperature with autorange and no configured resolution (standard behaviour)"""
        # TODO: PARAMETERS for thermometer type etc. see documentation of Device
        ret = 0
        with self._lock:
            self.send_command("MEAS:TEMP?")
            ret = self.receive_data()

        return ret

    def voltage(self, dc_ac='dc', vrange='auto', res='auto'):
        """measure voltage with autorange and no configured resolution (standard behaviour)

        dc_ac ['dc']:     Choose DC or AC mode, Default: dc  
        vrange ['auto']:  Set voltage range (refer to DMM Manual for possible values), Defualt: auto  
        res ['auto']:     Set Resolution (refer to DMM Manual for possible values), Default: auto  

        """
        ret = 0
        mod = "DC"
        if dc_ac == 'ac':
            mod = "AC"
        elif not dc_ac == 'dc':
            raise exceptions.InvalidDeviceParameter

        command = f"MEAS:VOLT:{mod}?"

        if not vrange == "auto":
            # vrange is specified
            if isinstance(vrange, int) or (
                    isinstance(vrange, str) and (vrange.upper() == "MIN" or vrange.upper() == "MAX")):
                command += f" {vrange}"
            else:
                raise exceptions.InvalidDeviceParameter

            if not res == "auto":
                if isinstance(res, int) or (isinstance(res, str) and (res.upper() == "MIN" or res.upper() == "MAX")):
                    command += f",{res}"
                else:
                    raise exceptions.InvalidDeviceParameter

        elif not res == "auto":
            # if resolution is set, vrange MUST also be set
            raise exceptions.InvalidDeviceParameter
        else:
            # Both are auto
            command += " AUTO"

        with self._lock:
            # print(command)
            self.send_command(command)
            ret = float(self.receive_data())

        return ret

    def lockPanel(self):
        print("lockPanel ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def setLocal(self):
        print("setLocal ERROR NOT IMPLEMENTED")
        raise NotImplementedError
