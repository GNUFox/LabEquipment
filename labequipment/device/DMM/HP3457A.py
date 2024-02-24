from enum import IntEnum, Enum

from labequipment.device.DMM.DMM import DMM
from labequipment.device.DMM.DMM import acdc as dmm_acdc
from labequipment.device.connection import USBTMCConnection, DummyConnection, XyphroUSBGPIBConfig
import logging

from labequipment.framework import exceptions

logger = logging.getLogger('root')


class acdc(dmm_acdc):
    DC = 0
    AC = 1


class TriggerType(IntEnum):
    auto = 1
    external = 2
    single = 3
    hold = 4
    synchronized = 5


class Terminals(IntEnum):
    disconnect = 0
    front = 1
    rear_or_card = 2


class ErrorCodes(Enum):
    HARDWARE = "Hardware Error"                    # 1
    CALIBRATION = "CAL or ACAL error"              # 3
    TRIGGER_TO_FAST = "Trigger too fast"           # 4
    SYNTAX = "Syntax error"                        # 8
    UNKNOWN_CMD = "Unknown command received"       # 16
    UNKNOWN_PARAM = "Unknown parameter received"   # 32
    PARAM_RANGE = "Parameter out of range"         # 64
    PARAM_MISSING = "Required parameter missing"   # 128
    PARAM_IGNORED = "Parameter ignored"            # 256
    OUT_OF_CAL = "Out of calibration"              # 512
    AUTOCAL_REQ = "Autocalibration required"       # 1024


class HP3457A(DMM):
    _expected_device_type = "HP3457A"
    _friendly_name = "HP 3457A Multimeter"
    # DCV 0.0000009,1 no
    # DCV 0.000001,1 yes
    vrange_max = 300
    vrange_min = 1E-6
    curr_range_max = 1.5
    curr_range_min = 300E-6
    res_min = 1
    res_max = 100
    nplc_min = 0
    nplc_max = 100

    _reset_after_connect: bool = False

    def __init__(self, visa_resource="", reset_after_connect=False):
        super().__init__()
        self._reset_after_connect = reset_after_connect
        if not visa_resource == "":
            self._connection: USBTMCConnection = USBTMCConnection(visa_resource=visa_resource)
        else:
            self._connection = DummyConnection()
            self._is_dummy_dev = True

    def connect(self):
        super().connect()
        with self._lock:
            connect_success = self._connection.connect()

            if connect_success == 0:
                if isinstance(self._connection, USBTMCConnection):
                    self._connection.xyphro_usb_gpib_adaptor_settings(XyphroUSBGPIBConfig.SET_READ_TERM_LF)
                self.send_command("ID?")
                idn = self.receive_data()
                if idn:
                    if self._check_device_type(idn, self._expected_device_type):
                        logger.info("connected")
                        self._ok = True
                        if self._reset_after_connect:
                            logger.info("Resetting instrument")
                            self.send_command("RESET")
                if not self._ok:
                    logger.error("Connected but no answer")

    def voltage(self, ac_dc_mode: acdc = acdc.DC, meas_range: float | int = DMM.CONST_AUTO,
                res: float | int = DMM.CONST_AUTO) -> float:
        """
        Simple voltage measurement (single trigger)

        NOTE: Not suitable for fast measurements

        @param ac_dc_mode:   AC / DC mode
        @param meas_range:   maximum voltage range
        @param res:          resolution (% of range)
        @return:
        """
        answer: str = ""
        with self._lock:
            self.configure_voltage(ac_dc_mode=ac_dc_mode, meas_range=meas_range, res=res)
            self.configure_trigger(TriggerType.single)
            answer = self.receive_data()
        ret: float = 0
        try:
            ret = float(answer)
        except ValueError:
            logger.error(f"Could not convert instrument reply to float: '{answer}'")
        return ret

    def configure_voltage(self, ac_dc_mode: acdc = acdc.DC, meas_range: float | int = DMM.CONST_AUTO,
                          res: float | int = DMM.CONST_AUTO):
        """
        Configure instrument for voltage measurement
        @param ac_dc_mode:   AC / DC mode
        @param meas_range:   maximum voltage range
        @param res:          resolution (% of range)
        @return:
        """
        params_ok = True
        if meas_range != self.CONST_AUTO:
            if not meas_range >= self.vrange_min and meas_range <= self.vrange_max:
                params_ok = False
        if res != self.CONST_AUTO:
            if not res >= self.res_min and res <= self.res_max:
                params_ok = False

        if not params_ok:
            logger.error(f"Device parameter error {meas_range=} {res=}")
            return

        command_str: str = ""
        if ac_dc_mode == acdc.DC:
            command_str = "DCV"
        elif ac_dc_mode == acdc.AC:
            command_str = "ACV"
        if meas_range != self.CONST_AUTO:
            command_str += f" {meas_range}"
        if res != self.CONST_AUTO:
            command_str += f",{res}"

        with self._lock:
            self.send_command(command_str)

    def current(self, ac_dc_mode: acdc = acdc.DC, meas_range: float | int = DMM.CONST_AUTO,
                res: float | int = DMM.CONST_AUTO) -> float:
        """
        Simple current measurement (single trigger)

        NOTE: Not suitable for fast measurements

        @param ac_dc_mode:   AC / DC mode
        @param meas_range:   maximum current range
        @param res:          resolution (% of range)
        @return:
        """
        answer: str = ""
        with self._lock:
            self.configure_current(ac_dc_mode=ac_dc_mode, meas_range=meas_range, res=res)
            self.configure_trigger(TriggerType.single)
            answer = self.receive_data()
        ret: float = 0
        try:
            ret = float(answer)
        except ValueError:
            logger.error(f"Could not convert instrument reply to float: '{answer}'")
        return ret

    def configure_current(self, ac_dc_mode: acdc = acdc.DC, meas_range: float | int = DMM.CONST_AUTO,
                          res: float | int = DMM.CONST_AUTO):
        """
        Configure instrument for voltage measurement
        :param ac_dc_mode:  AC / DC mode
        :param meas_range:  maximum current range
        :param res:         resolution (% of range)
        :return:
        """
        params_ok = True
        if meas_range != self.CONST_AUTO:
            if not meas_range >= self.curr_range_min and meas_range <= self.curr_range_max:
                params_ok = False
        if res != self.CONST_AUTO:
            if not res >= self.res_min and res <= self.res_max:
                params_ok = False

        if not params_ok:
            logger.error(f"Device parameter error {meas_range=} {res=}")
            return

        command_str: str = ""
        if ac_dc_mode == acdc.DC:
            command_str = "DCI"
        elif ac_dc_mode == acdc.AC:
            command_str = "ACI"
        if meas_range != self.CONST_AUTO:
            command_str += f" {meas_range}"
        if res != self.CONST_AUTO:
            command_str += f",{res}"

        with self._lock:
            self.send_command(command_str)

    def configure_impedance(self, fixed: bool):
        with self._lock:
            self.send_command(f"FIXEDZ {1 if fixed else 0}")

    def get_impedance_fixed(self):
        fixed = False
        with self._lock:
            self.send_command("FIXEDZ?")
            answer = self.receive_data()
            try:
                i = int(answer.split('.')[0])
                if i == 1:
                    fixed = True
                elif i == 0:
                    fixed = False
                else:
                    logger.error(f"Unexpected value {i}")
            except ValueError:
                logger.error("Could not convert {}")

        return fixed

    def diode(self):
        raise NotImplementedError

    def frequency(self):
        raise NotImplementedError  # TODO: implement

    def fResistance(self):
        raise NotImplementedError

    def period(self):
        raise NotImplementedError   # TODO: implement

    def resistance(self):
        raise NotImplementedError  # TODO: implement

    def temperature(self):
        raise NotImplementedError

    def configure_trigger(self, trigger: TriggerType):
        """
        Configure Trigger type
        :param trigger:  see TriggerType-enum
        :return:
        """
        with self._lock:
            self.send_command(f"TRIG {trigger.value}")

    def single_trigger_and_get_value(self) -> str:
        """
        Switch to Trigger type "single" which triggers a measurement
        :return:  answer from the instrument as a string (needs to be parsed / converted for further processing)
        """
        answer: str = ""
        with self._lock:
            self.configure_trigger(TriggerType.single)
            answer = self.receive_data()
        return answer

    def tone(self, freq: int, dur: int):
        self.send_command(f"TONE {freq},{dur}")

    def configure_nplc(self, nplc: float):
        """
        Confgure NPLC (Number of Powerline cycles) for measurements
        :param nplc: float: [ 0 - 100 ]
        :return:
        """
        # TODO: allow only specific NPLC values (see manual)
        if not nplc >= self.nplc_min and nplc <= self.nplc_max:
            logger.error(f"NPLC {nplc} outside of range [{self.nplc_min} {self.nplc_max}")
            return

        if nplc > 0.005:
            match nplc:
                case 0.005:
                    pass
                case 0.1:
                    pass
                case 1:
                    pass
                case 10:
                    pass
                case 100:
                    pass
                case _:
                    logger.error("NPLC needs to be <=0.005 0.005, 0.1, 1, 10 or 100")
                    return
        with self._lock:
            self.send_command(f"NPLC {nplc}")

    def get_nplc(self) -> float:
        raise NotImplementedError

    def get_nplc_from_device(self) -> float:
        nplc: float = 0
        answer: str = ""
        with self._lock:
            self.send_command("NPLC?")
            answer = self.receive_data()
            if answer:
                try:
                    nplc = float(answer)
                except ValueError:
                    logger.error(f"Could not convert answer {answer} to float")

        return nplc

    def configure_terminals(self, terminals: Terminals):
        """
        Select terminal sor add-in card
        :param terminals:  see Terminals-enum
        :return:
        """
        with self._lock:
            self._connection.send_command(f"TERM {terminals.value}")

    def get_error_codes(self) -> list[ErrorCodes] | None:
        """
        Get the error codes from the instrument
        See Manual page 194 (section 4-52 Command reference)
        Quick reference: page 16 "ERR?"

        :return: list[ErrorCodes] or None
        """
        err_str: str | None = None
        with self._lock:
            self.send_command("ERR?")
            err_str = self.receive_data()

        if err_str:
            err_code: int = 0
            try:
                err_code = int(err_str.split('.')[0])
            except ValueError:
                logger.error(f"Could not parse string '{err_str}' as error code")
                return None

            idx = 1
            errors: list[ErrorCodes] = []
            for el in ErrorCodes:
                if idx & err_code:
                    errors.append(el)
                idx = idx << 1
            return errors
        else:
            return None
