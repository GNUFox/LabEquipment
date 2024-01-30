from labequipment.device.connection import USBTMCConnection, SerialConnection, DummyConnection

from labequipment.device.PSU import PSU
from labequipment.framework import exceptions

import logging

logger = logging.getLogger('root')


class HP6632B(PSU.PSU):
    _expected_device_type = "6632B"

    _display_mode_normal: bool
    _display_char_max = 14

    def __init__(self, visa_resource: str = "", serial_dev: str = ""):
        """Set up a connection to an HP 6632B PSU using USBTMC (USB to GPIB converter)"""

        super().__init__()
        if not visa_resource == "" and serial_dev == "":
            self._connection = USBTMCConnection(visa_resource=visa_resource)
        elif not serial_dev == "" and visa_resource == "":
            # TODO: implement serial device setup
            raise NotImplementedError
            # self._connection = SerialConnection()
        else:
            self._connection = DummyConnection()
            self._is_dummy_dev = True

        self._display_mode_normal = True

    def connect(self):
        """
        Connect to the instrument and check the *IDN? result,
        if the connection does not work right awa, retry 2 more times
        @return:
        """
        super().connect()
        with self._lock:
            connect_success = self._connection.connect()
            if connect_success == 0:
                retry_count = 3
                while retry_count > 0 and not self._ok:
                    self.send_command("*IDN?")  # TODO: generalize this

                    idn = self.receive_data()
                    retry_count -= 1

                    if idn:
                        name = idn.split(',')[1]
                        if self._check_device_type(name, self._expected_device_type):
                            logger.info("Connected")
                            self.display_normal()
                            self._ok = True
                    else:
                        logger.warning("Retrying connect")

        if not self._ok:
            logger.error("Connected but no answer")
            raise exceptions.DeviceCommunicationError
        # TODO: fix error handling

    def disconnect(self):
        pass

    def set_voltage(self, voltage: float, output_nr=0):
        """
        Set voltage of output
        @param voltage: in V
        @param output_nr:  not used
        @return:
        """
        with self._lock:
            self.send_command(f"VOLT {voltage}")

    def get_measured_voltage(self, output_nr=0) -> float:
        """
        Take an automated voltage measurement, all measurement parameters are set to automatic
        @param output_nr:
        @return: float, measured voltage
        """
        volts = -1
        with self._lock:
            self.send_command("MEAS:VOLT?")
            v_str = self.receive_data()
            try:
                volts = float(v_str)
            except ValueError:
                logger.error(f"VALUE ERROR, can not convert {v_str} to float")
        return volts

    def set_current(self, current: float, output_nr=0):
        """
        Set the current limit
        @param current:  in A
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self.send_command(f"CURR {current}")

    def get_measured_current(self, output_nr=0) -> float:
        """
        Take an automated current measurement, all measurement parameters are set to automatic
        @param output_nr: not used
        @return: float, measured current
        """
        amps = -1
        with self._lock:
            self.send_command("MEAS:CURR?")
            a_str = self.receive_data()
            try:
                amps = float(a_str)
            except ValueError:
                logger.error(f"VALUE ERROR, can not convert {a_str} to float")
        return amps

    def display_text(self, text):
        """
        Display text on the VFD of the instrument (disables voltage + current readout)
        @param text:
        @return:
        """
        if self._display_mode_normal:
            self.send_command("DISPLAY:MODE TEXT")
            self._display_mode_normal = False
        if not len(text) > self._display_char_max:
            self.send_command(f"DISPLAY:TEXT \"{text}\"")

    def display_normal(self):
        """
        Set display to normal mode (voltage + current readout)
        @return:
        """
        self.send_command("DISPLAY:MODE NORMAL")
        self._display_mode_normal = True

    def enable_output(self, output_nr=0) -> None:
        """
        Enable the output
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self.send_command("OUTP ON")

    def disable_output(self, output_nr=0) -> None:
        """
        Disable the output
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self.send_command("OUTP OFF")
