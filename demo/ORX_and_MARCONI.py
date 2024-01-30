import os
import time

from dotenv import load_dotenv

from labequipment.device.AWG import MARCONI_2019, ORX_402A
from labequipment.device.AWG.ORX_402A import Waveforms
from labequipment.device.AWG.MARCONI_2019 import ModFrequencies
import labequipment.framework.log

load_dotenv()

marconi_visa_res = os.getenv("MARCONI_VISA_RES")
orx_visa_res = os.getenv("ORX_VISA_RES")


def main():
    marconi = MARCONI_2019.MARCONI_2019(visa_resource=marconi_visa_res)
    awg = ORX_402A.ORX_402A(visa_resource=orx_visa_res)

    marconi.connect()
    awg.connect()

    awg.set_amplitude(1)
    awg.set_waveform(Waveforms.SINE)
    awg.set_frequency(1000)
    awg.enable_output()

    marconi.set_frequency(433.5E6)
    marconi.set_fm(3.5E3)
    marconi.set_amplitude(-85, unit="db")
    marconi.set_modulation_src(ModFrequencies.ext)

    time.sleep(0.5)

    for i in range(300, int(6e3), 10):
        awg.set_frequency(i)

    time.sleep(0.5)
    awg.disable_output()
    marconi.disable_output()


if __name__ == "__main__":
    main()
