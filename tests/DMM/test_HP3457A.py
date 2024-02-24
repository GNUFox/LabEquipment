import os
from unittest import TestCase
from dotenv import load_dotenv
import labequipment.framework.log
from labequipment.device.DMM import HP3457A
from labequipment.device.DMM.HP3457A import TriggerType, Terminals, acdc, ErrorCodes

from tests.testutils import ask_user_if_ok

if not load_dotenv():
    raise ValueError(".env file not found")

visa_res = os.getenv("HP3457A_VISA_RES")

triggers = dict()
for e in TriggerType:
    triggers[e] = f"TRIG {e.value}"

terminals = dict()
for e in Terminals:
    terminals[e] = f"TERM {e.value}"


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


class TestHP3457A_HARDWARE(TestHP3457A):

    def test_error_codes(self):
        """
        Deliberatly send wrong commands / cause errors to happen to check error code retrieval
        :return:
        """
        self.dmm.send_command("jfölksafkjs")
        errors = self.dmm.get_error_codes()
        self.assertEqual(errors, [ErrorCodes.UNKNOWN_CMD])

        self.dmm.send_command("DCV BLA,BLUPP")
        errors = self.dmm.get_error_codes()
        self.assertEqual(errors, [ErrorCodes.UNKNOWN_PARAM, ErrorCodes.PARAM_IGNORED])

        self.dmm.send_command("DCV 999,999")
        errors = self.dmm.get_error_codes()
        self.assertEqual(errors, [ErrorCodes.PARAM_RANGE])

        self.dmm.send_command("DCV 10,10,10")
        errors = self.dmm.get_error_codes()
        self.assertEqual(errors, [ErrorCodes.PARAM_IGNORED])

        # Don't know how to provoke other errors

    def test_NPLC(self):
        nplc = 10
        self.dmm.configure_nplc(nplc)
        answer = self.dmm.get_nplc_from_device()
        self.assertEqual(nplc, answer)

    def test_fixedz(self):
        self.dmm.configure_impedance(fixed=True)
        fixed = self.dmm.get_impedance_fixed()
        self.assertEqual(fixed, True)

        self.dmm.configure_impedance(fixed=False)
        fixed = self.dmm.get_impedance_fixed()
        self.assertEqual(fixed, False)


class TestHP3457A_INTERACTIVE(TestHP3457A):

    def test_voltage(self):
        measured_voltage = self.dmm.voltage()
        print(f"Measured Voltage: {measured_voltage}\n")
        self.assertEqual(ask_user_if_ok(), True)

    def test_current(self):
        measured_current = self.dmm.current()
        print(f"Measured Current: {measured_current}\n")
        self.assertEqual(ask_user_if_ok(), True)




class TestSetCommands(TestHP3457A_DUMMY):
    def test_voltage(self):
        self.dmm.voltage()
        sent_commands = self.dmm._connection.get_last_commands_list()
        self.assertEqual(sent_commands, ["DCV", "TRIG 3"])

    def test_configure_voltage(self):
        self.dmm.configure_voltage(ac_dc_mode=acdc.DC, meas_range=self.dmm.CONST_AUTO, res=self.dmm.CONST_AUTO)
        self.dmm.configure_voltage(ac_dc_mode=acdc.DC, meas_range=10, res=1)
        commands = self.dmm._connection.get_last_commands_list()
        self.assertEqual(commands, ["DCV", "DCV 10,1"])

    def test_configure_trigger(self):
        for trigger, expected in triggers.items():
            self.dmm.configure_trigger(trigger)
            self.assertEqual(self.dmm._connection.get_last_command(), expected)

    def test_configure_terminals(self):
        for term, expected in terminals.items():
            self.dmm.configure_terminals(term)
            self.assertEqual(self.dmm._connection.get_last_command(), expected)

    def test_configure_nplc(self):
        self.dmm.configure_nplc(1)
        self.assertEqual(self.dmm._connection.get_last_command(), "NPLC 1")
