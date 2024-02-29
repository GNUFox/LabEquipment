import os
import time
from dotenv import load_dotenv

from labequipment.device.PSU import HP6632B
from labequipment.framework.log import setup_custom_logger
setup_custom_logger()

if not load_dotenv():
    raise ValueError(".env file not found")

visa_res = os.getenv("HP_PSU_VISA_RES")


def test():
    psu = HP6632B.HP6632B(visa_resource=visa_res)
    # psu = HP6632B.HP6632B()

    psu.connect()
    psu.set_current(0.4)
    # psu.set_voltage(12)
    psu.enable_output()

    volts = []
    amps = []
    for i in range(120):
        psu.set_voltage(i / 10)
        time.sleep(0.1)
        volts.append(psu.get_measured_voltage())
        amps.append(psu.get_measured_current())

    print(volts)
    print(amps)

    time.sleep(1)
    psu.disable_output()


def show_text():
    psu = HP6632B.HP6632B(visa_resource=visa_res)
    psu.connect()
    string = "HELLO THIS IS A SCROLLING TEXT              "
    max_chars = psu._display_char_max

    i = max_chars
    text_begin = 0
    while i > max_chars - len(string):
        i -= 1
        text_end = max_chars - i
        if i >= 0:
            disp_str = ' ' * i
            disp_str += string[text_begin:text_end]
        else:
            text_begin = -i
            disp_str = string[text_begin:text_end]

        print(f"{i=} {text_begin=} {text_end=}")
        print(f"'{disp_str}'")
        psu.display_text(disp_str)
        time.sleep(0.1)

    for j in range(4):
        for i in (range(10) if j % 2 else reversed(range(10))):
            dip = str(i) * max_chars
            psu.display_text(dip)
            time.sleep(0.1)

    time.sleep(0.5)
    psu.display_text(" " * max_chars)


if __name__ == "__main__":
    test()
