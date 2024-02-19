from enum import Enum

from labequipment.device.DMM import DMM
from labequipment.device.DMM.DMM import acdc
from labequipment.device.connection import USBTMCConnection, DummyConnection, XyphroUSBGPIBConfig
import logging

from labequipment.framework import exceptions

logger = logging.getLogger('root')


class TriggerType(Enum):
    auto = 1
    external = 2
    single = 3
    hold = 4
    synchronized = 5


class HP3457A(DMM.DMM):
    _expected_device_type = "HP3457A"
    _friendly_name = "HP 3457A Multimeter"
    # DCV 0.0000009,1 no
    # DCV 0.000001,1 yes
    vrange_max = 300
    vrange_min = 1E-6
    curr_range_max = NotImplementedError
    curr_range_min = NotImplementedError
    res_min = 1
    res_max = 100
    nplc_min = 0
    nplc_max = 100

    CONST_AUTO = -1

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

    def voltage(self, dc_ac='dc', vrange=CONST_AUTO, res=CONST_AUTO) -> float:
        """
        Simple voltage measurement (single trigger)

        NOTE: Not suitable for fast measurements

        @param dc_ac:   AC / DC mode
        @param vrange:  maximum voltge range
        @param res:     resolution (% of vrange)
        @return:
        """
        acdc_conf: acdc = acdc.DC
        if dc_ac == 'dc':  # TODO: remove legacy (after fixing DMM)
            acdc_conf = acdc.DC
        elif dc_ac == 'ac':
            acdc_conf = acdc.AC
        self.configure_voltage(dc_ac=acdc_conf, vrange=vrange, res=res)
        self.configure_trigger(TriggerType.single)
        answer = self._connection.receive_data()
        ret: float = 0
        try:
            ret = float(answer)
        except ValueError:
            logger.error(f"Could not convert instrument reply to float: '{answer}'")
        return ret

    def configure_voltage(self, dc_ac: acdc, vrange: float, res: float) -> None:
        """
        Configure instrument for voltage measurement
        @param dc_ac:  AC / DC mode
        @param vrange: maximum voltage range
        @param res:    resolution (% of vrange)
        @return:
        """
        params_ok = True
        if vrange != self.CONST_AUTO:
            if not vrange >= self.vrange_min and vrange <= self.vrange_max:
                params_ok = False
        if res != self.CONST_AUTO:
            if not res >= self.res_min and res <= self.res_max:
                params_ok = False

        if not params_ok:
            logger.error(f"Device parameter error {vrange=} {res=}")
            return

        command_str: str = ""
        if dc_ac == acdc.DC:
            command_str = "DCV"
        elif dc_ac == acdc.AC:
            command_str = "ACV"
        if vrange != self.CONST_AUTO:
            command_str += f"{vrange}"
        if res != self.CONST_AUTO:
            command_str += f",{res}"

        with self._lock:
            self.send_command(command_str)

    def configure_trigger(self, trigger: TriggerType) -> None:
        with self._lock:  # TODO check locking design (deadlock / functions unable to use)
            self.send_command(f"TRIG {trigger.value}")

    def single_trigger_and_get_value(self) -> str:
        self.configure_trigger(TriggerType.single)
        return self._connection.receive_data()

    def tone(self, freq: int, dur: int):
        self.send_command(f"TONE {freq},{dur}")

    def configure_nplc(self, nplc: float):
        if not nplc >= self.nplc_min and nplc <= self.nplc_max:
            logger.error(f"NPLC {nplc} outside of range [{self.nplc_min} {self.nplc_max}")
            return
        with self._lock:
            self._connection.send_command(f"NPLC {nplc}")
