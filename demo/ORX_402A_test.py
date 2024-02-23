import os
import time

from dotenv import load_dotenv

import labequipment.framework.log
from labequipment.device.AWG import ORX_402A
from labequipment.device.AWG.ORX_402A import Waveforms

if not load_dotenv():
    raise ValueError(".env file not found")

visa_res = os.getenv("ORX_VISA_RES")


def main():
    awg = ORX_402A.ORX_402A(visa_resource=visa_res)
    awg.connect()

    awg.set_frequency(1234e3)
    awg.set_frequency(1234)
    awg.set_frequency(4321e3)
    awg.set_frequency(4321)
    awg.set_frequency(5432e3)
    awg.set_frequency(5432)
    awg.set_frequency(9876e3)
    awg.set_frequency(9876)

    awg.set_amplitude(1)
    awg.enable_output()
    awg.get_frequency()
    awg.set_waveform(Waveforms.SQUARE)
    time.sleep(0.5)
    awg.set_frequency(2345)
    time.sleep(0.5)
    awg.set_waveform(Waveforms.SINE)
    time.sleep(0.5)

    for i in range(100, 3000, 20):
        awg.set_frequency(i)

    awg.disable_output()


if __name__ == "__main__":
    main()
