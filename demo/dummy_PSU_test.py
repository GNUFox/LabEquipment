import time
from labequipment.device.PSU import dummyPSU

from labequipment.framework.log import setup_custom_logger

setup_custom_logger()


def test():
    psu = dummyPSU.dummyPSU(output_states=[0, 0, 0],
                            get_measured_voltages=[3.3], get_measured_currents=[1],
                            CC_status=[False], CV_status=[True], count_type=1)

    # psu = KEITHLEY_2231A.KEYTHLEY_2231A("/dev/ttyUSB0")

    psu.set_voltage(12, 1)
    psu.set_current(0.5, 1)
    psu.set_voltage(12, 2)
    psu.set_current(0.5, 2)
    psu.set_voltage(5, 3)
    psu.set_current(0.1, 3)

    print("ENABLE ALL")
    psu.enableAllOutputs()

    time.sleep(0.5)
    print_info(psu)

    print("DISABLE 1")
    psu.disable_output(1)

    time.sleep(0.5)
    print_info(psu)

    print("DISABLE ALL")
    psu.disableAllOutputs()

    time.sleep(0.5)
    print_info(psu)

    print("ENABLE 1")
    psu.enable_output(1)

    time.sleep(0.5)
    print_info(psu)

    print("ENABLE ALL")
    psu.enableAllOutputs()

    time.sleep(0.5)
    print_info(psu)

    del psu


def print_info(psu):
    print("==================")
    for i in range(3):
        print(
            f"OP{i + 1} is {'on' if psu.get_output_state(i + 1) else 'off'}; {psu.get_measured_voltage(i + 1)}V; {psu.get_measured_current(i + 1)}A")
    print("==================")


if __name__ == "__main__":
    test()
