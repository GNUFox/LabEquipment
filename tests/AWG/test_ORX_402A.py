import os
from unittest import TestCase
from dotenv import load_dotenv
import labequipment.framework.log
from labequipment.device.AWG import ORX_402A
from labequipment.device.AWG.ORX_402A import Waveforms, OutputState

load_dotenv()

visa_res = os.getenv("VISA_RES")

frequencies = {
    1.234: "F1.234HZ",
    1234e3: "F1234KHZ",
    1234: "F1234HZ",
    4320e3: "F4320KHZ",
    4320: "F4.32KHZ",
    5430e3: "F5430KHZ",
    5430: "F5.43KHZ",
    9870e3: "F9870KHZ",
    9870: "F9.87KHZ"
}
amplitudes = {
    1: "A1.00V",
    999E-3: "A999MV",
    1.234: "A1.23V",
    0.9: "A900MV",
    0.01: "A10MV"
}
amplitudes_hw = {
    1: "A1.00V",
    999E-3: "A999MV",
    1.23: "A1.23V",
    0.9: "A900MV",
    0.01: "A10MV"
}
waveforms = {
    Waveforms.DC: "W0",
    Waveforms.SINE: "W1",
    Waveforms.SQUARE: "W2",
    Waveforms.TRIANGLE: "W3"
}
offsets = {
    1.00: "O1.00V",
    1.001: "O1.00V",
    0.1: "O100MV",
    0.01: "O10MV",
    0: "O0MV",
    3.99: "O3.99V",
    3.999: "O4.00V",
    3.993: "O3.99V"
}
offsets_hw = {
    1.00: "O1.00V",
    0.1: "O100MV",
    0.01: "O10MV",
    0: "O0MV",
    3.99: "O3.99V",
    4.00: "O4.00V",
}


class TesetORX_402A(TestCase):
    def setUp(self):
        self.awg = ORX_402A.ORX_402A(visa_resource=visa_res)
        self.awg.connect()
        self.assertEqual(self.awg.get_ok(), True)


class TestORX_402A_DUMMY(TestCase):
    def setUp(self):
        self.awg = ORX_402A.ORX_402A()
        self.awg.connect()
        self.assertEqual(self.awg.get_ok(), True)


class TestHWLoopackSetCommands(TesetORX_402A):
    def test_set_frequency(self):
        for i in frequencies.items():
            self.awg.set_frequency(i[0])
            self.assertEqual(self.awg.get_frequency(), i[0])

    def test_set_amplitude(self):
        for i in amplitudes_hw.items():
            self.awg.set_amplitude(i[0])
            self.assertEqual(self.awg.get_amplitude(), i[0])

    def test_set_offset(self):
        self.awg.set_amplitude(1)
        for i in offsets_hw.items():
            self.awg.set_offset(i[0])
            self.assertEqual(self.awg.get_offset(), i[0])

    def test_set_output(self):
        self.awg.enable_output()
        self.assertEqual(self.awg.get_output_state(), OutputState.ON)
        self.awg.disable_output()
        self.assertEqual(self.awg.get_output_state(), OutputState.OFF)

    def test_set_waveform(self):
        for i in waveforms.items():
            self.awg.set_waveform(i[0])
            self.assertEqual(self.awg.get_waveform(), i[0])


class TestSetCommands(TestORX_402A_DUMMY):
    def test_set_frequency(self):
        for i in frequencies.items():
            self.awg.set_frequency(i[0])
            self.assertEqual(self.awg.test_get_last_command(), i[1])

    def test_set_amplitude(self):
        for i in amplitudes.items():
            self.awg.set_amplitude(i[0])
            self.assertEqual(self.awg.test_get_last_command(), i[1])

    def test_set_offset(self):
        self.awg.set_amplitude(1)
        for i in offsets.items():
            self.awg.set_offset(i[0])
            self.assertEqual(self.awg.test_get_last_command(), i[1])

    def test_set_output(self):
        self.awg.enable_output()
        self.assertEqual(self.awg.test_get_last_command(), "N1")
        self.awg.disable_output()
        self.assertEqual(self.awg.test_get_last_command(), "N0")

    def test_set_waveform(self):
        for i in waveforms.items():
            self.awg.set_waveform(i[0])
            self.assertEqual(self.awg.test_get_last_command(), i[1])
