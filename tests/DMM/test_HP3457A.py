import os
from unittest import TestCase
from dotenv import load_dotenv
import labequipment.framework.log
from labequipment.device.DMM import HP3457A
from labequipment.device.DMM.HP3457A import TriggerType

load_dotenv()

visa_res = os.getenv("HP3457A_VISA_RES")

triggers = dict()
for e in TriggerType:
    triggers[e] = f"TRIG {e.value}"


class TestHP3457A(TestCase):
    def setUp(self):
        self.dmm = HP3457A.HP3457A(visa_resource=visa_res)
        self.dmm.connect()
        self.assertEqual(self.dmm.get_ok(), True)


class TestHP3457A_DUMMY(TestCase):
    def setUp(self):
        self.dmm = HP3457A.HP3457A()
        self.dmm.connect()
        self.assertEqual(self.dmm.get_ok(), True)
        self.dmm._connection.clear_last_command_list()


class TestSetCommands(TestHP3457A_DUMMY):
    def test_voltage(self):
        self.dmm.voltage()
        sent_commands = self.dmm._connection.get_last_commands_list()
        self.assertEqual(sent_commands, ["DCV", "TRIG 3"])

    def test_configure_voltage(self):
        self.fail()

    def test_configure_trigger(self):
        for trigger, expected in triggers.items():
            self.dmm.configure_trigger(trigger)
            self.assertEqual(self.dmm._connection.get_last_command(), expected)

    def test_tone(self):
        self.fail()

    def test_configure_nplc(self):
        self.dmm.configure_nplc(1)
        self.assertEqual(self.dmm._connection.get_last_command(), "NPLC 1")
