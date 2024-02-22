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
        @param meas_range:   maximum voltge range
        @param res:          resolution (% of vrange)
        @return:
        """

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
                          res: float | int = DMM.CONST_AUTO) -> None:
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
                res: float | int = DMM.CONST_AUTO):
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

    def configure_trigger(self, trigger: TriggerType) -> None:
        with self._lock:  # TODO check locking design (deadlock / functions unable to use)
            self.send_command(f"TRIG {trigger.value}")

    def single_trigger_and_get_value(self) -> str:
        self.configure_trigger(TriggerType.single)
        return self.receive_data()

    def tone(self, freq: int, dur: int):
        self.send_command(f"TONE {freq},{dur}")

    def configure_nplc(self, nplc: float):
        if not nplc >= self.nplc_min and nplc <= self.nplc_max:
            logger.error(f"NPLC {nplc} outside of range [{self.nplc_min} {self.nplc_max}")
            return
        with self._lock:
            self.send_command(f"NPLC {nplc}")

    def configure_terminals(self, terminals: Terminals):
        with self._lock:
            self._connection.send_command(f"TERM {terminals.value}")

    def get_error_codes(self) -> list[ErrorCodes] | None:
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
