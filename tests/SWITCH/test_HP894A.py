import os
from unittest import TestCase
from dotenv import load_dotenv

from labequipment.device.SWITCH.HP894A import HP8954A
from tests.testutils import ask_user_if_ok
from labequipment.framework.log import setup_custom_logger
setup_custom_logger()


if not load_dotenv():
    raise ValueError(".env file not found")

visa_res = os.getenv("HP8954A_VISA_RES")


class TestHP8954A(TestCase):
    def setUp(self):
        self.switch = HP8954A(visa_resource=visa_res)
        self.switch.connect()
        self.assertEqual(self.switch.get_ok(), True)

        # Always start in RX mode and F1
        self.switch.receive_mode()
        self.switch.rf_monitor_select(HP8954A.RFMon.Mon1)
        print("TX switch is of ( Mode: Receive, Transmit Key: Off)\n RF monitor is F1")
        self.assertEqual(ask_user_if_ok(), True)


class TestHP8954A_INTERACTIVE(TestHP8954A):
    def test_transmit_key_on_off(self):
        self.switch.transmit_key_on()
        print("TX switch is on ( Mode: Transmit, Transmit Key: On)")
        self.assertEqual(ask_user_if_ok(), True)
        self.switch.transmit_key_off()
        print("TX switch is of ( Mode: Transmit, Transmit Key: Off)")
        self.assertEqual(ask_user_if_ok(), True)
        self.switch.receive_mode()
        print("TX switch is of ( Mode: Receive, Transmit Key: Off)")
        self.assertEqual(ask_user_if_ok(), True)

    def test_transmit_mode(self):
        self.switch.transmit_mode()
        print("TX switch is of ( Mode: Transmit, Transmit Key: Off)")
        self.assertEqual(ask_user_if_ok(), True)
        self.switch.receive_mode()
        print("TX switch is of ( Mode: Receive, Transmit Key: Off)")
        self.assertEqual(ask_user_if_ok(), True)

    def test_rf_monitor_select(self):
        self.switch.rf_monitor_select(HP8954A.RFMon.Mon2)
        print("RF monitor 2 selected")
        self.assertEqual(ask_user_if_ok(), True)
        self.switch.rf_monitor_select(HP8954A.RFMon.Mon1)
        print("RF monitor 1 selected")
        self.assertEqual(ask_user_if_ok(), True)
