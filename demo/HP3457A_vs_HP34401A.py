import os
import time

from dotenv import load_dotenv

from labequipment.device.DMM.HP3457A import HP3457A, acdc, TriggerType, Terminals
from labequipment.device.DMM.HP34401A import HP34401A
from labequipment.device.PSU.HP6632B import HP6632B
from labequipment.framework.log import setup_custom_logger
setup_custom_logger()

if not load_dotenv():
    raise ValueError(".env file not found")

visa_res_hp3457a = os.getenv("HP3457A_VISA_RES")
visa_res_hp34401a = os.getenv("HP34401A_VISA_RES")
visa_res_hp6632b = os.getenv("HP_PSU_VISA_RES")


def main():
    hp3457a = HP3457A(visa_resource=visa_res_hp3457a, reset_after_connect=True)
    hp34401a = HP34401A(visa_resource=visa_res_hp34401a)

    psu = HP6632B(visa_resource=visa_res_hp6632b)
    hp3457a.connect()
    hp34401a.connect()
    psu.connect()

    if not (psu.get_ok() and hp3457a.get_ok() and hp34401a.get_ok()):
        return

    psu.set_voltage(1)
    psu.set_current(0.05)
    psu.enable_output()
    time.sleep(0.5)
    psu_volts = psu.get_measured_voltage()

    print(f"PSU set to {psu_volts} V")

    hp3457a.configure_terminals(Terminals.rear_or_card)

    print("### Quick Voltage measurement:", end='')
    volt_a = hp3457a.voltage(meas_range=3)
    volt_b = hp34401a.voltage(meas_range=3)
    print(f"{volt_a} {volt_b} - diff: {volt_b - volt_a}")

    hp3457a.configure_voltage(ac_dc_mode=acdc.DC, meas_range=3)
    hp3457a.configure_trigger(TriggerType.single)
    # TODO: implement hp34401a configure volt.
    voltages = []
    for i in range(50):
        voltages.append([float(hp3457a.single_trigger_and_get_value()), hp34401a.voltage(meas_range=3)])

    print(voltages)

    psu.disable_output()


if __name__ == "__main__":
    main()
