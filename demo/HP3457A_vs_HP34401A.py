import os
import sys
import time

from dotenv import load_dotenv

import labequipment.framework.log
from labequipment.device.DMM.HP3457A import HP3457A, acdc, TriggerType
from labequipment.device.DMM.HP34401A import HP34401A

load_dotenv()
visa_res_hp3457a = os.getenv("HP3457A_VISA_RES")
visa_res_hp34401a = os.getenv("HP34401A_VISA_RES")


def main():
    hp3457a = HP3457A(visa_resource=visa_res_hp3457a, reset_after_connect=True)
    hp34401a = HP34401A(visa_resource=visa_res_hp34401a)
    hp3457a.connect()
    hp34401a.connect()

    print("### Quick Voltage measurement:", end='')
    volt_a = hp3457a.voltage()
    volt_b = hp34401a.voltage()
    print(f"{volt_a} {volt_b} - diff: {volt_b - volt_a}")

    hp3457a.configure_voltage(dc_ac=acdc.DC, vrange=hp3457a.CONST_AUTO, res=hp3457a.CONST_AUTO)
    hp3457a.configure_trigger(TriggerType.single)
    # TODO: implement hp34401a configure volt.
    voltages = []
    for i in range(10):
        voltages.append([float(hp3457a.single_trigger_and_get_value()), hp34401a.voltage()])

    print(voltages)


if __name__ == "__main__":
    main()