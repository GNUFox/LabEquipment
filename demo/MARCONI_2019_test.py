import time
import os
from dotenv import load_dotenv

from labequipment.device.AWG import MARCONI_2019
from labequipment.device.AWG.MARCONI_2019 import ModFrequencies
import labequipment.framework.log

if not load_dotenv():
    raise ValueError(".env file not found")

default_carrier_freq = 433.525E6
default_fm_dev = 2.5E3
default_am_mod_idx = 0.85
default_rf_lvl = -85  # dBm

visa_res = os.getenv("MARCONI_VISA_RES")


def test():
    awg = MARCONI_2019.MARCONI_2019()
    awg.connect()

    awg.set_frequency(123.1234567890123E3)
    awg.set_frequency(433.500E6)
    awg.set_amplitude(1, unit="v")
    awg.set_amplitude(1.2345E-6, unit="V")  # 1.234 UV
    awg.set_amplitude(12.345E-3, unit="V")  # 12.34 MV
    awg.set_amplitude(52.345E-3, unit="V")  # 52.3 MV

    awg.set_amplitude(1.2345E-3, unit="V")  # 1.234 MV
    awg.set_amplitude(2.2345E-3, unit="V")  # 2.23 MV
    awg.set_amplitude(0.1234E-3, unit="V")  # 123.4 UV
    awg.set_amplitude(0.1234E-2, unit="V")  # 1234 UV or 1.234 MV
    awg.set_amplitude(0.2234E-2, unit="V")  # 2.23 MV
    awg.set_amplitude(234.5E-6, unit="V")  # 234 UV
    awg.set_amplitude(-75, unit="db")

    print("------------")

    awg.set_fm(1E6)
    awg.set_fm(0.99999999999E6)
    awg.set_fm(1E3)
    awg.set_fm(1.23456E3)
    awg.set_fm(123456)
    awg.set_fm(12345)
    awg.set_fm(1234)

    awg.disable_output()


def fm_dev_sweep_test():
    awg = MARCONI_2019.MARCONI_2019(visa_resource=visa_res)
    awg.connect()

    awg.set_frequency(default_carrier_freq)
    awg.set_fm(default_fm_dev)
    awg.set_modulation_src(ModFrequencies.F1k0)
    awg.set_amplitude(default_rf_lvl, unit="db")

    for j in range(3):
        for i in range(100, 3000, 50):
            awg.set_fm(i)

        for i in reversed(range(100, 3000, 50)):
            awg.set_fm(i)


def am_test():
    awg = MARCONI_2019.MARCONI_2019(visa_resource=visa_res)
    awg.connect()

    awg.set_frequency(default_carrier_freq)
    awg.set_am(default_am_mod_idx)
    awg.set_modulation_src(ModFrequencies.F0k4)
    awg.set_amplitude(amp=default_rf_lvl, unit="db")
    time.sleep(2)

    awg.disable_output()


def am_ext_mod_test():
    awg = MARCONI_2019.MARCONI_2019(visa_resource=visa_res)
    awg.connect()

    awg.set_frequency(default_carrier_freq)
    awg.set_am(default_am_mod_idx)
    awg.set_modulation_src(ModFrequencies.ext)
    awg.set_amplitude(amp=default_rf_lvl, unit="db")
    awg.set_alc(True)
    time.sleep(2)
    awg.set_alc(False)
    time.sleep(2)

    awg.disable_output()


def state_string_test():
    str1 = "010400000000000000000060210608020000000000"
    str2 = "AAAAAAAAAABBBBBBBBCCDDDDDDEEFFGGPRSTUVWXYZ"
    str3 = "111111111122222222334444445566776543210123"

    awg = MARCONI_2019.MARCONI_2019()

    # awg._decode_state_string(str1)
    awg.read_state_string()


if __name__ == "__main__":
    am_ext_mod_test()
