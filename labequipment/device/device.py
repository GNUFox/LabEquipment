import abc
from abc import abstractmethod

from labequipment.device.connection import Connection

from threading import RLock
import logging

logger = logging.getLogger('root')


class device(metaclass=abc.ABCMeta):
    _lock: RLock
    _ok: bool  # Set to True after the device is connected properly
    _expected_device_type: str = NotImplemented
    _friendly_name: str = "Friendly name n/a"
    _is_dummy_dev: bool

    _connection: Connection = NotImplemented

    @abstractmethod
    def __init__(self):
        self._lock = RLock()
        self._ok = False
        self._is_dummy_dev = False

    def __del__(self):
        self.disconnect()

    @abstractmethod
    def connect(self):
        logger.debug(f"Connecting to {self._friendly_name}")
        if self._is_dummy_dev:
            self._ok = True
            logger.debug(f"Dummy connected")

    def disconnect(self):
        if self._ok:
            self._connection.disconnect()

    def _check_device_type(self, answer, expected):
        """
        check whether the device type is what is being expected
        :param answer:    answer returned by the instrument
        :param expected:  expected answer (device type)
        :return:   True: if ok, False: if not ok
        """
        if self._is_dummy_dev:
            return True
        if not answer == expected:
            logger.error(f"[{type(self).__name__}] Wrong device type, expected {expected} got '{answer}'")
            return False
        else:
            return True

    def send_command(self, command: str):
        self._connection.send_command(command)

    def receive_data(self) -> str | None:
        return self._connection.receive_data()

    def receive_data_raw(self, n_bytes: int = -1) -> bytes:
        return self._connection.receive_data_raw(n_bytes)

    def get_ok(self) -> bool:
        return self._ok

    def set_dummy(self):
        self._is_dummy_dev = True

    def test_get_last_command(self) -> str:
        """
        Only used for testing in conjunction with DummyConnection
        @return:  the last command sent to the instrument
        """
        if self._is_dummy_dev:
            return self._connection.get_last_command()
