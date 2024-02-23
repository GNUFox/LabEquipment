import os
import sys
import time

from dotenv import load_dotenv

import labequipment.framework.log
from labequipment.device.DMM.HP3457A import HP3457A, acdc, TriggerType

if not load_dotenv():
    raise ValueError(".env file not found")

visa_res = os.getenv("HP3457A_VISA_RES")


def main():
    dmm = HP3457A(visa_resource=visa_res, reset_after_connect=True)
    dmm.connect()

    print("### Quick Voltage measurement: V = ", end='')
    volt = dmm.voltage()
    print(f"{volt}")

    print("### Configured voltage measurement with continuous trigger:\n V = [", end='')
    dmm.configure_voltage(ac_dc_mode=acdc.DC, meas_range=10, res=1)
    dmm.configure_trigger(TriggerType.auto)
    for i in range(10):
        answer = dmm.receive_data()
        v = float(answer)
        print(f"{v} ", end='')
        sys.stdout.flush()
    print("]")

    print("Configuring NPLC for even faster measurement:")
    dmm.configure_nplc(1)
    for i in range(100):
        voltage = float(dmm.receive_data())
        print(f"\r{voltage}          ", end='')
        sys.stdout.flush()


if __name__ == "__main__":
    main()
