import os
import time

from dotenv import load_dotenv

from labequipment.device.SWITCH import HP894A
from labequipment.framework.log import setup_custom_logger
setup_custom_logger()

if not load_dotenv():
    raise ValueError(".env file not found")

visa_res = os.getenv("HP8954A_VISA_RES_VISA_RES")


def rx_tx_test():
    sw = HP894A.HP8954A(visa_resource=visa_res)
    sw.connect()

    if not sw.get_ok():
        return

    sw.transmit_key_on()
    time.sleep(0.5)
    sw.transmit_key_off()
    time.sleep(0.5)
    sw.receive_mode()
    time.sleep(0.5)
    sw.rf_monitor_select(sw.RFMon.Mon2)


def aux_relays_test():
    sw = HP894A.HP8954A(visa_resource=visa_res)

    sw.connect()
    if not sw.get_ok():
        return

    for m in sw.aux_relays:
        sw.set_aux_relay(rly=m, state=True)

    for m in sw.aux_relays:
        sw.set_aux_relay(rly=m, state=False)

    sw.set_aux_relay(0, True)
    sw.set_aux_relay(0, False)

    rly = dict()
    j = 0
    for i in sw.aux_relays.items():
        rly[i[0]] = not i[1] if j % 2 else i[1]
        j += 1

    sw.set_multiple_relays(rly)


if __name__ == "__main__":
    rx_tx_test()
