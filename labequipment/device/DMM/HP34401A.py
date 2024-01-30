from labequipment.device.DMM import DMM
from labequipment.device.connection import USBTMCConnection, DummyConnection
import logging

logger = logging.getLogger('root')


class HP34401A(DMM.DMM):
    _expected_device_type = "34401A"

    def __init__(self, visa_resource: str = "", serial_dev: str = ""):
        super().__init__()
        if not visa_resource == "":
            self._connection = USBTMCConnection(visa_resource=visa_resource)
        elif not serial_dev == "":
            raise NotImplementedError  # TODO: implement serial
        else:
            self._connection = DummyConnection()
            self._is_dummy_dev = True

    def connect(self):
        super().connect()

        with self._lock:
            connect_success = self._connection.connect()
            if connect_success == 0:
                self.send_command("*IDN?")

                idn = self.receive_data()

                if idn:
                    name = idn.split(',')[1]
                    if self._check_device_type(name, self._expected_device_type):
                        logger.info("Connected")
                        self._ok = True

                if not self._ok:
                    logger.error("Connected but no answer")

    # TODO: check manual for further functions to implement
