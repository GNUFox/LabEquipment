from labequipment.device import device
from labequipment.device.connection import USBTMCConnection, DummyConnection
import labequipment.framework.log

from enum import IntEnum

import logging

logger = logging.getLogger('root')


class HP8954A(device.device):
    _expected_device_type = "8954A"

    class RFMon(IntEnum):
        Mon1 = 1
        Mon2 = 2

    _set_transmit_key: bool  # True = on, False = off
    _set_tx_or_rx: bool  # True = on, False = off
    _set_rf_monitor: RFMon

    aux_relays = {1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False,
                  'A': False, 'B': False, 'C': False, 'D': False, 'E': False, 'F': False, 'G': False}

    def __init__(self, visa_resource: str = ""):
        super().__init__()
        if not visa_resource == "":
            self._connection = USBTMCConnection(visa_resource=visa_resource)
        else:
            self._connection = DummyConnection()
            self._is_dummy_dev = True

    def connect(self):
        super().connect()
        connect_success = self._connection.connect()

        if connect_success == 0:
            with self._lock:
                self._connection.send_command("ID")
                idn = self._connection.receive_data()
                if len(idn) >= len(self._expected_device_type):
                    idn = idn[0:len(self._expected_device_type)]

                if self._check_device_type(idn, self._expected_device_type):
                    logger.info("Connected")
                    self._ok = True

    def transmit_key_on(self):
        with self._lock:
            self.send_command("K1")
            self._set_transmit_key = True
            self._set_tx_or_rx = True

    def transmit_key_off(self):
        with self._lock:
            self.send_command("K0")
            self._set_transmit_key = False

    def transmit_mode(self):
        with self._lock:
            self.send_command("XM")
            self._set_tx_or_rx = True

    def receive_mode(self):
        with self._lock:
            self.send_command("RC")
            self._set_transmit_key = False
            self._set_tx_or_rx = False

    def rf_monitor_select(self, rf_mon: RFMon):
        with self._lock:
            self.send_command(f"F{rf_mon.value}")

    def set_aux_relay(self, rly: (int, str), state: bool):
        """
        Set the auxiliary relay state open / close
        @param rly:  1-9 for relays A2K1 - A2K9, A-G for relays A2K10 - A2K16
        @param state: true: open / false: close
        @return:
        """
        if isinstance(rly, str):
            rly = rly.upper()
        if not rly in self.aux_relays and not rly == 0:
            logger.error(f"ERROR : Relay {rly} not in relays: {self.aux_relays}")

        with self._lock:
            self.send_command(f"{'V' if state else 'U'}{rly}")

    def set_multiple_relays(self, multi_relays: dict):
        """
        Set multiple auxiliary relays
        @param multi_relays:  dict containing relay reference and boolean state
                              example: {2: True, 'A': False, 5: False}
        @return:
        """
        for item in multi_relays.items():
            self.set_aux_relay(item[0], item[1])

    def get_tx_rx(self) -> bool:
        return self._set_tx_or_rx

    def get_tx_key(self) -> bool:
        return self._set_transmit_key

    def get_rf_monitor(self) -> RFMon:
        return self._set_rf_monitor
