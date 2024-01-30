from labequipment.framework.globals import GlobalDefaults
from datetime import datetime
import threading
import logging

logger = logging.getLogger('root')


class Datalogging():
    def __init__(self, name):
        self._lock = threading.Lock()
        self.logilfepath = f"{GlobalDefaults.HTOL_log_basepath}/{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{name}.log"
        try:
            self.logfile = open(self.logilfepath, 'w')
        except:
            logger.error("Couldn't open Datalogging file")

    def __del__(self):
        self.logfile.flush()
        self.logfile.close()

    def write_to_log(self, string):
        with self._lock:
            self.logfile.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}; {string}\n")
            self.logfile.flush()
