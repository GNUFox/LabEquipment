import time
from enum import Enum
from math import trunc

from labequipment.device.connection import USBTMCConnection, DummyConnection
from labequipment.device.AWG import AWG

import threading
import logging

logger = logging.getLogger('root')


class Waveforms(Enum):
    DC = "W0"
    SINE = "W1"
    SQUARE = "W2"
    TRIANGLE = "W3"


class OutputState(Enum):
    OFF = "N0"
    ON = "N1"


class FreqUnits(Enum):
    KILOHERTZ = "KHZ"
    HERTZ = "HZ"


class VoltageUnits(Enum):
    VOLT = "V"
    MILLIVOLT = "MV"


def get_voltage_range(voltage) -> float:
    if voltage >= 1:
        return 1
    elif voltage >= 0.1:
        return 0.1
    elif voltage >= 0.01:
        return 0.01


def _extract_hertz(reply: str) -> float:
    ret: float = 0
    if reply.endswith(FreqUnits.KILOHERTZ.value):
        ret = float(reply[1:-(len(FreqUnits.KILOHERTZ.value))]) * 1E3
    elif reply.endswith(FreqUnits.HERTZ.value):
        ret = float(reply[1:-(len(FreqUnits.HERTZ.value))])
    else:
        logger.error(f"Unexpected reply: {reply}, unit does not match")

    return ret


def _extract_volts(reply: str) -> float:
    ret: float = 0
    if reply.endswith(VoltageUnits.MILLIVOLT.value):
        ret = float(reply[1:-(len(VoltageUnits.MILLIVOLT.value))]) * 1E-3
    elif reply.endswith(VoltageUnits.VOLT.value):
        ret = float(reply[1:-(len(VoltageUnits.VOLT.value))])
    else:
        logger.error(f"Unexpected reply: {reply}, unit does not match")

    return ret


def _extract_output_state(reply: str) -> OutputState:
    ret: OutputState
    try:
        ret = OutputState(reply)
    except ValueError:
        logger.error(f"Unexpected reply: {reply} is not an output state")

    return ret


def _extract_waveform(reply: str) -> Waveforms:
    ret: Waveforms
    try:
        ret = Waveforms(reply)
    except ValueError:
        logger.error(f"Unexpected reply: '{reply}' not in waveforms")

    return ret


def _extract_parameter(param: (list[str], str), param_prefix: str, extract_function):
    param_str = ""
    ret = None

    if isinstance(param, list):
        for i in param:
            if i.startswith(param_prefix):
                param_str = i
                break
        if param_str == "":
            logger.error(f"Parameter '{param_prefix}' not found in parameters: {param}")
            # TODO: ret is error
    elif isinstance(param, str):
        param_str = param
    else:
        logger.error(f"Parameters '{param}' must be list[str] or str datatype")
        # TODO: ret is error
    if param_str != "":
        ret = extract_function(param_str)

    return ret


class ORX_402A(AWG.AWG):
    """
    OR-X  Model 402A - Programmable waveform generator

    This device (at least the instance I had for testing) does not at all respond to query commands '?F' '?*' etc.
    The solution is to keep track of the internal state.
    """
    _friendly_name = "OR-X 402A"

    min_freq = 0.004
    max_freq = 9.99E6
    min_ampl_V = 10E-3
    max_ampl_V = 9.99

    _internal_state_dirty: bool
    _set_freq: float
    _set_ampl: float
    _set_offset: float
    _set_waveform: Waveforms
    _set_output_on: OutputState

    def __init__(self, visa_resource: str = ""):
        super().__init__()
        if not visa_resource == "":
            self._connection = USBTMCConnection(visa_resource=visa_resource)
        else:
            self._is_dummy_dev = True
            self._connection = DummyConnection()

        self._internal_state_dirty = False
        self._set_freq = 0
        self._set_ampl = 0
        self._set_offset = 0
        self._set_waveform = Waveforms.SINE
        self._set_output_on = OutputState.OFF

        self._block_send = threading.Event()
        self._block_send.set()

    def connect(self):
        """
        Connect to the instrument.
        Verification if the connection was successful hast to be done manually.
        This function triggers the instrument to show its GPIB address on the display.
        @return:
        """
        super().connect()
        with self._lock:
            connect_success = self._connection.connect()
            if connect_success == 0:
                # display addr to show connection
                self.send_command("Z488")  # TODO: error handling

                if not self._is_dummy_dev:
                    time.sleep(3)  # Wait after first command / connect otherwise "ERROR 9-1" (Syntax error) happens
                    self.send_command("N0")
                    self._ok = self._get_all_and_ok()
                if not self._ok:
                    logger.debug(f"Connected to {self._friendly_name}")
                else:
                    logger.error("Connection success but no answer")
            else:
                logger.error("Connection failed")

    def set_frequency(self, frequency: float, output_nr=0):
        """
        Set output frequency
        @param frequency: in Hz
        @param output_nr: not used
        @return:
        """
        if not (frequency >= self.min_freq and frequency <= self.max_freq):
            logger.error(f"Frequency {frequency} out of range [{self.min_freq} {self.max_freq}]")
            return

        freq_for_cmd: str
        freq_unit_for_cmd: FreqUnits

        if frequency >= 4E3:  # Only when frequency is greater than 4kHz the KHZ unit is useful in the command sent
            freq_unit_for_cmd = FreqUnits.KILOHERTZ
            frequency = frequency * 1E-3  # Convert to KHZ
        else:
            freq_unit_for_cmd = FreqUnits.HERTZ

        freq_trunc: float
        if frequency >= 1000:
            # no digits after comma
            freq_trunc = trunc(frequency)
        elif frequency >= 100:
            # 1 digit after comma
            freq_trunc = trunc(frequency * 10) / 10
        elif frequency >= 10:
            # 2 digits after comma
            freq_trunc = trunc(frequency * 100) / 100
        elif frequency >= 1:
            # 3 digits after comma
            freq_trunc = trunc(frequency * 1000) / 1000
        else:
            # 4 digits after comma max.
            freq_trunc = trunc(frequency * 1E4) / 1E4

        if int(str(freq_trunc)[0]) >= 4:
            # If first digit is 4, accuracy of frequency setting is reduced to 3 digits
            if freq_trunc % 1 == 0:
                freq_for_cmd = str(freq_trunc)[:-1] + '0'
            else:
                freq_for_cmd = str(round(freq_trunc * 100) / 100)
        else:
            freq_for_cmd = str(freq_trunc)

        with self._lock:
            self.send_command(f"F{freq_for_cmd}{freq_unit_for_cmd.value}")  # F1234KHZ
            self._set_freq = frequency
            self._internal_state_dirty = True

    def get_frequency(self, output_nr=0) -> float:
        """
        Get the currently set frequency
        :param output_nr:  not used
        :return: frequency in Hz (float)
        """
        if self._internal_state_dirty:
            with self._lock:
                self.send_command("?F")
                reply = self.receive_data()

                temp = _extract_parameter(reply, "F", _extract_hertz)
                # TODO: error checking if temp is error_type etc.
                self._set_freq = temp
        return self._set_freq

    def set_waveform(self, waveform: Waveforms, output_nr=0):
        """
        Select the waveform
        @param waveform:  1: Sine, 2: Square, 3: Triangle, 0: DC
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self.send_command(f"{waveform.value}")
            self._set_waveform = waveform
            self._internal_state_dirty = True

    def get_waveform(self, output_nr: int = 0) -> Waveforms:
        """
        Get the currently selected waveform
        :param output_nr: not used
        :return: Waveforms-Enum
        """
        if self._internal_state_dirty:
            with self._lock:
                self.send_command("?W")
                reply = self.receive_data()
                self._set_waveform = _extract_parameter(reply, "W", _extract_waveform)
                # TODO: error checking if temp is error_type etc.
        return self._set_waveform

    def set_amplitude(self, amp: float, output_nr=0):
        """
        Set the output amplitude
        @param amp:  in V
        @param output_nr:  not used
        @return:
        """
        max_ampl: float
        if self._set_offset > 0:
            max_ampl = 2 * (4.99 * get_voltage_range(amp) - self._set_offset)
        else:
            max_ampl = self.max_ampl_V

        if not (amp >= self.min_ampl_V and amp <= max_ampl):
            logger.error(f"Amplitude {amp} out of range [{self.min_ampl_V} {self.max_ampl_V}]")
            return

        amp_for_cmd: str
        amp_unit_for_cmd: VoltageUnits

        if amp >= 1:
            amp_unit_for_cmd = VoltageUnits.VOLT
            amp_for_cmd = f"{(round(amp * 100) / 100):.2f}"
        else:
            amp_for_cmd = f"{((round(amp * 1000) / 1000) * 1E3):.0f}"  # convert to millivolt
            amp_unit_for_cmd = VoltageUnits.MILLIVOLT

        with self._lock:
            self.send_command(f"A{amp_for_cmd}{amp_unit_for_cmd.value}")
            self._set_ampl = amp
            self._internal_state_dirty = True

    def get_amplitude(self, output_nr: int = 0) -> float:
        """
        Get the currentl set amplitude
        :param output_nr:  not used
        :return: amplitude in V (float)
        """
        if self._internal_state_dirty:
            with self._lock:
                self.send_command("?A")
                reply = self.receive_data()
                temp = _extract_parameter(reply, "A", _extract_volts)
                # TODO: error checking if temp is error_type etc.
                self._set_ampl = temp
        return self._set_ampl

    def set_offset(self, offset: int, output_nr: int = 0) -> None:
        """
        Set the offset voltage, must be within limits. limits depend on amplitude setting

        @param offset:  offset in volt
        @param output_nr:  not used
        @return:
        """
        max_offset = 4.99 * get_voltage_range(self._set_ampl) - 0.5 * self._set_ampl
        if not abs(offset) <= max_offset:
            logger.error(f"Offset ({offset}) out of range, max offset: +/-{max_offset}")
            return

        offset_for_cmd: str
        offset_unit_for_cmd: VoltageUnits

        offset_round = round(offset * 100) / 100

        if offset_round >= 1:
            offset_unit_for_cmd = VoltageUnits.VOLT
            offset_for_cmd = f"{offset_round:.2f}"
        else:
            offset_unit_for_cmd = VoltageUnits.MILLIVOLT
            offset_for_cmd = f"{(offset_round * 1E3):.0f}"

        with self._lock:
            self.send_command(f"O{offset_for_cmd}{offset_unit_for_cmd.value}")
            self._set_offset = offset_round  # TODO: check???
            self._internal_state_dirty = True

    def get_offset(self, output_nr: int = 0) -> float:
        """
        Get the currently set offset
        :param output_nr:  not used
        :return: offset in V (float)
        """
        if self._internal_state_dirty:
            with self._lock:
                self.send_command("?O")
                reply = self.receive_data()
                temp = _extract_parameter(reply, "O", _extract_volts)
                # TODO: error checking if temp is error_type etc.
                self._set_offset = temp
        return self._set_offset

    def enable_output(self, output_nr=0) -> None:
        """
        Enable the output
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self._set_output_on = OutputState.ON
            self.send_command(self._set_output_on.value)
            self._internal_state_dirty = True

    def disable_output(self, output_nr=0) -> None:
        """
        Disable the output
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self._set_output_on = OutputState.OFF
            self.send_command(self._set_output_on.value)
            self._internal_state_dirty = True

    def get_output_state(self, output_nr: int = 0) -> OutputState:
        """
        Get the output state
        :param output_nr:  not used
        :return: OutputState-Enum
        """
        if self._internal_state_dirty:
            with self._lock:
                self.send_command("?N")
                reply = self.receive_data()
                self._set_output_on = _extract_parameter(reply, "N", _extract_output_state)
        return self._set_output_on

    def _get_all_and_ok(self) -> bool:
        """
        Used during initial connection, get the most important values to set up tracked parameters (Freq, Ampl, ...)
        This function should work without errors, if error occur it should return false (the "_ok" state)
        :return:  True:  everything worked, instrument is ready for use
                  False: errors occured, instrument is not ready for use
        """
        if not self._lock.locked():
            return False

        self.send_command("?*")
        reply = self.receive_data()
        reply_list = reply.split(';')
        # TODO: add error checking
        self._set_freq = _extract_parameter(reply_list, 'F', _extract_hertz)
        self._set_ampl = _extract_parameter(reply_list, 'A', _extract_volts)
        self._set_offset = _extract_parameter(reply_list, 'O', _extract_volts)
        self._set_waveform = _extract_parameter(reply_list, 'W', _extract_waveform)
        self._set_output_on = _extract_parameter(reply_list, 'N', _extract_output_state)

        return True

    def send_command(self, command) -> None:
        """
        Device specific command processing.
        This device has a rate limit for commands.
        This function will block until it's safe to send the next command after the previous one has been sent
        @param command:  command to send
        @return:
        """
        logger.debug("Waiting for command clearance")
        self._block_send.wait(timeout=0.1)
        self._block_send.clear()
        super().send_command(command)
        r = threading.Timer(0.05, self._reset_command_block)
        r.start()

    def receive_data(self) -> str:
        self._block_send.wait(timeout=1)  # If a command has been issued wait until receive is possible
        self._block_send.clear()
        return super().receive_data()

    def _reset_command_block(self):
        logger.debug("Resetting command block")
        self._block_send.set()
