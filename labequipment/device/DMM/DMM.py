from labequipment.device import device
from abc import ABCMeta
import logging

logger = logging.getLogger('root')


class acdc(metaclass=ABCMeta):
    DC = "DC"
    AC = "AC"


class DMM(device.device, metaclass=ABCMeta):
    CONST_AUTO: int = -1
    CONST_MIN: int = -2
    CONST_MAX: int = -3

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

    def current(self, ac_dc_mode: acdc = acdc.DC, meas_range: float | int = CONST_AUTO, res: float | int = CONST_AUTO):
        """
        Measure current with auto-range and no configured resolution (standard behaviour)

        :param ac_dc_mode:  AC / DC mode
        :param meas_range:  maximum current range
        :param res:         resolution (usually in the same units as the measurement function,
                            eg. 0.00001 for 6 digits when the range is 1
        :return:            measured current or None
        """

        ret = 0
        command = f"MEAS:CURR:{ac_dc_mode}?"

        ok, range_and_res = self._get_command_from_range_and_res(meas_range, res)
        if ok:
            command += range_and_res
        else:
            return ret

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

    def voltage(self, ac_dc_mode: acdc = acdc.DC, meas_range: float | int = CONST_AUTO, res: float | int = CONST_AUTO):
        """
        Measure voltage with auto-range and no configured resolution (default behaviour)

        :param ac_dc_mode:  AC / DC mode
        :param meas_range:  maximum voltage range
        :param res:         resolution (usually in the same units as the measurement function,
                            eg. 0.00001 for 6 digits when the range is 1
        :return:            measured voltage or None
        """
        ret = 0
        command = f"MEAS:VOLT:{ac_dc_mode}?"

        ok, range_and_res = self._get_command_from_range_and_res(meas_range, res)
        if ok:
            command += range_and_res
        else:
            return ret

        with self._lock:
            self.send_command(command)
            ret = float(self.receive_data())

        return ret

    def lockPanel(self):
        print("lockPanel ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def setLocal(self):
        print("setLocal ERROR NOT IMPLEMENTED")
        raise NotImplementedError

    def _get_command_from_range_and_res(self, meas_range, res):
        command = ""
        ok = True

        meas_range_auto = False
        res_auto = False
        match meas_range:
            case self.CONST_AUTO:
                meas_range_auto = True
            case self.CONST_MAX:
                command += " MAX"
            case self.CONST_MIN:
                command += " MIN"
            case _:
                if meas_range > 0:
                    command += f" {meas_range}"
                else:
                    logger.error(f"Invalid use range: {meas_range} is not greater than 0 ")
                    ok = False
        match res:
            case self.CONST_AUTO:
                res_auto = True
            case self.CONST_MAX:
                command += ", MAX"
            case self.CONST_MIN:
                command += ", MIN"
            case _:
                if res > 0:
                    command += f", {res}"
                else:
                    logger.error(f"Invalid use: resolution: {res} is not greater than 0 ")
                    ok = False

        if not res_auto and meas_range_auto:
            logger.error("Invalid use: if resolution is set, range MUST also be set")
            ok = False
        if res_auto and meas_range_auto:
            command += " AUTO"

        return ok, command
