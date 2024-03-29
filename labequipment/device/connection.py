from abc import abstractmethod, ABCMeta
from enum import Enum

from telnetlib import Telnet
import usbtmc
from usbtmc.usbtmc import UsbtmcException
from usb.core import USBTimeoutError, USBError
import serial

import logging

logger = logging.getLogger('root')


# noinspection SpellCheckingInspection
class XyphroUSBGPIBConfig(Enum):
    GET_VER = '!ver?'
    SET_READ_TERM_CR = '!term cr'
    SET_READ_TERM_LF = '!term lf'
    SET_READ_TERM_EOI = '!term eoi'
    STORE_READ_TERM = '!term store'
    GET_READ_TERM = '!term?'
    SET_AUTO_ID_ON = '!autoid on'
    SET_AUTO_ID_OFF = '!autoid off'
    SET_AUTO_ID_DLY_5S = '!autoid slow'
    SET_AUTO_ID_DLY_15S = '!autoid slower'
    SET_AUTO_ID_DLY_30S = '!autoid slowest'
    GET_AUTO_ID = '!autoid?'
    SET_USB_SER_LEN_20 = '!string short'
    SET_USB_SER_LEN_NORM = '!string normal'
    GET_USB_SER_LEN = '!string?'
    RESET = '!reset'


# TODO: implement visa stuff? find library??
# TODO: maybe implement data parsing / conversion in parent class because all subclasses might need that
class Connection(metaclass=ABCMeta):
    connection_ok: bool

    @property
    @abstractmethod
    def _destination(self) -> str:
        pass

    @abstractmethod
    def connect(self) -> int:
        pass

    def disconnect(self):
        pass

    @abstractmethod
    def send_command(self, command: str) -> int:
        logger.debug(f"[{type(self).__name__}] [{self._destination}] Sending command '{command}'")
        return 0

    @abstractmethod
    def receive_data(self) -> str | None:
        pass

    def receive_data_raw(self, n_bytes: int = -1) -> bytes | None:
        pass

    def get_last_command(self) -> str:
        pass

    def get_last_commands_list(self) -> list:
        pass

    def clear_last_command_list(self):
        pass


class DummyConnection(Connection):
    """
    Create a dummy connection that never fails and always returns the required data
    """
    _destination = "DUMMY"
    _last_commands: list

    def connect(self) -> int:
        self._last_commands = []
        return 0

    def send_command(self, command: str) -> int:
        super().send_command(command)
        self._last_commands.append(command)
        return 0

    def receive_data(self, dummy_data="DUMMY") -> str:
        return dummy_data

    def get_last_command(self) -> str:
        return self._last_commands[-1]

    def get_last_commands_list(self) -> list:
        return self._last_commands

    def clear_last_command_list(self):
        self._last_commands = []


class TelnetConnection(Connection):
    """
    Establish a telnet connection to the device.
    This is most likely a custom connection that does not follow any standards aside from telnet
    """
    _tn_connection: Telnet
    _destination = ""

    def __init__(self, host):
        self._host = host
        self._ip = host.split(':')[0]
        self._port = int(host.split(':')[1])

    def connect(self) -> int:
        success = 1
        try:
            self._tn_connection = Telnet(self._ip, self._port)
            success = 0
        except:  # TODO: fix Telnet exceptions ConnectionRefused ??
            logger.error(f"[{type(self).__name__}] Failed to connect to {self._host}")

        return success

    def disconnect(self):
        self._tn_connection.close()

    def send_command(self, command: str):
        if self._tn_connection:
            super().send_command(command)
            try:
                self._tn_connection.write(f"{command}\n".encode('ascii'))
            except EOFError:
                logger.error("Sending command failed")
        else:
            logger.error("Sending command failed, not connected")

    def receive_data(self, terminator=b'\n') -> str:
        data = ""
        if self._tn_connection:
            try:
                data = self._tn_connection.read_until(terminator).decode('ascii')[:-2]  # TODO: better input handling
            except EOFError:
                logger.error("Reading TELNET data failed")
            logger.debug(f"Received data '{data}'")
        else:
            logger.error(f"Can not receive data, not connected")
        return data


class SerialConnection(Connection):
    _tty_connection: serial.Serial
    _destination = ""

    # TODO: implement serial
    def __init__(self, tty_connection: serial.Serial):
        self._tty_connection = tty_connection

    def connect(self) -> int:
        try:
            self._tty_connection.open()
        except serial.SerialException:
            logger.error(f"Could not connect to serial device: {self._tty_connection.port}")

    def disconnect(self):
        pass

    def send_command(self, command: str):
        pass

    def receive_data(self) -> str:
        pass


class USBTMCConnection(Connection):
    """
    Establish a USBTMC connection to the device using VISA-resource string or usbtmc-id and serial number.
    If id + serial are used a VISA resource string will be guessed.
    Using the VISA-resource string is more reliable
    """
    _usbtmc_connection: usbtmc.Instrument
    _visa_resource_string: str = ""
    _destination = ""

    def __init__(self, visa_resource: str = "", usbtmc_id: str = "", serial_no: str = ""):
        if not visa_resource == "" and usbtmc_id == "" and serial_no == "":
            # VISA RESOURCE STRING
            if visa_resource.startswith("USB"):  # TODO: check visa string format maybe?
                if not visa_resource.endswith("::INSTR"):
                    visa_resource = visa_resource + "::INSTR"
                self._visa_resource_string = visa_resource
                # TODO: maybe add "::INSTR" at the end?
                #  when user scans with vish or other tools they may not get ::INSTR
        elif not usbtmc_id == "" and not serial_no == "" and visa_resource == "":
            # only usbtmc_id and serial number given try to construct visa resource string
            a = usbtmc_id.split(':')[0]
            b = usbtmc_id.split(':')[1]
            self._visa_resource_string = f"USB::0x{a}::0x{b}::{serial_no}::INSTR"
        else:
            logger.error("Invalid usage, must give either visa resource or id + serial_no")
            # TODO: check if exception raising is ok here???

    def connect(self) -> int:
        success = 1
        if not self._visa_resource_string == "":
            try:
                self._usbtmc_connection = usbtmc.Instrument(self._visa_resource_string)
                self._usbtmc_connection.open()
                self._destination = self._visa_resource_string
                success = 0
            except UsbtmcException:
                logger.error(f"[{type(self).__name__}] USBTMC communication error on {self._visa_resource_string}")
        return success

    def disconnect(self):
        logger.debug("Disconnect usbtmc")
        self._usbtmc_connection.close()

    def send_command(self, command: str) -> int:
        super().send_command(command)
        success = 1
        try:
            self._usbtmc_connection.write(f"{command}")
            success = 0
        except UsbtmcException:
            logger.error("Sending command failed")
        except USBError:
            logger.error("USBError while sending USBTMC command")

        return success

    def receive_data(self) -> str | None:
        data = None
        try:
            data = self._usbtmc_connection.read()
        except UsbtmcException:
            logger.error("UsbtmcException while reading USBTMC data")
        except USBTimeoutError:
            logger.error("Timeout while reading USBTMC data")
        except USBError:
            logger.error("USBError while reading USBTMC data")

        return data

    def receive_data_raw(self, n_bytes: int = -1) -> bytes | None:
        data = None
        try:
            data = self._usbtmc_connection.read_raw(n_bytes)
        except UsbtmcException:
            logger.error("Reading Raw USBTMC data failed")
        except USBTimeoutError:
            logger.error("Timeout while reading Raw USBTMC data")

        return data

    def get_visa_res(self) -> str:
        return self._visa_resource_string

    def xyphro_usb_gpib_adaptor_settings(self, command: XyphroUSBGPIBConfig) -> str | None:
        answer = None
        try:
            self._usbtmc_connection.pulse()
            if command.value.endswith('?'):
                answer = self._usbtmc_connection.ask(command.value)
            else:
                self._usbtmc_connection.write(command.value)
        except UsbtmcException:
            logger.error("Sending xyphro gpib command failed")

        return answer


class PrologixUSBAdaptor(SerialConnection):
    _destination = ""

    def __init__(self, tty_device: str = ""):
        self._tty_device = tty_device

        # TODO: set parameters correctly for PROLOGIX (or check if they can be omitted (usbserial auto??)
        tty_connection = serial.Serial()
        tty_connection.baudrate = 9600
        tty_connection.timeout = 1
        tty_connection.write_timeout = 1
        tty_connection.port = self._tty_device
        tty_connection.bytesize = serial.EIGHTBITS
        tty_connection.parity = serial.PARITY_NONE
        tty_connection.stopbits = serial.STOPBITS_ONE
        super().__init__(tty_connection)

    def send_command(self, command: str):
        pass  # TODO: implement

    def send_adaptor_command(self, command: str):
        pass  # TODO: implement


class PrologixUSBConnection(Connection):
    """
    Establish a connection to the device using the PROLOGIX USB to GPIB Adaptor
    """
    # TODO: when using PROLOGIX there can only be as many instances as there are adaptors + needs to be global?

    gpib_address: int
    _destination = ""

    def __init__(self, gpib_address):
        self.GPIB_address = gpib_address

    # TODO: implement
