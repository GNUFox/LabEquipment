from enum import IntEnum, Enum

from labequipment.device.connection import USBTMCConnection, DummyConnection
import labequipment.framework.log

from labequipment.device.AWG import AWG

from math import trunc

import logging

logger = logging.getLogger('root')


class FreqUnits(Enum):
    MEGAHERTZ = "MZ"
    KILOHERTZ = "KZ"
    HERTZ = "HZ"


class VoltageUnits(Enum):
    MICROVOLT = "UV"
    MILLIVOLT = "MV"
    VOLT = "VL"


class ModFrequencies(IntEnum):
    F0k3 = 0
    F0k4 = 1
    F1k0 = 2
    F3k0 = 3
    F6k0 = 4
    ext = 6


def _convert_freq_units(f: float) -> (float, FreqUnits):
    """
    Convert Frequency (in Hz) to combination of number and frequency unit

    units:
    HZ : Hertz
    KZ : Kilohertz
    MZ : Megahertz

    @param f: frequency in Hz
    @return: converted_frequency, unit
    """
    f_conv: float
    f_unit: FreqUnits
    if f >= 1E6:
        # Megahertz
        f_conv = f / 1E6
        f_unit = FreqUnits.MEGAHERTZ
    elif f >= 1E3:
        # Kilohertz
        f_conv = f / 1E3
        f_unit = FreqUnits.KILOHERTZ
    else:
        f_conv = f
        f_unit = FreqUnits.HERTZ
    return f_conv, f_unit


def _convert_volt_units(v: float) -> (float, VoltageUnits):
    """
    Convert Voltage (in V) to combination of number and voltage unit

    units:
    UV : Microvolts
    MV : Millivolts
    VL : Volts

    @param v: voltage in V
    @return:  converted_voltage, unit
    """
    v_conv: float
    v_unit: VoltageUnits

    if v >= 1:
        # VOLTS
        v_conv = v
        v_unit = VoltageUnits.VOLT
    elif v >= 1E-3:
        # MILLIVOLTS
        v_conv = v / 1E-3
        v_unit = VoltageUnits.MILLIVOLT
    else:
        # MICROVOLTS
        v_conv = v / 1E-6
        v_unit = VoltageUnits.MICROVOLT

    return v_conv, v_unit


class MARCONI_2019(AWG.AWG):
    """
    MARCONI INSTRUMENTS  signal generator 2019

    NOTE:
    Instrument does not behave as described in the manual.
    Can not set some parameters (RF Level) and then enable output. Setting RF Level automatically enables output.
    """
    freq_min = 80E3  # minimum frequency in kHz
    freq_max = 1040000E3  # maximum frequency in kHz
    ampl_v_min = 0.1E-6  # minimum amplitude in V
    amp_v_max = 1  # maximum amplitude in V
    ampl_db_min = -127  # minimum amplitude in dB
    amp_db_max = 13  # maximum amplitude in dbB
    dev_min = 10  # minimum FM deviation in Hz
    dev_max = 1E6  # maximum FM deviation in Hz
    mod_idx_min = 0  # minimum AM mod. index
    mod_idx_max = 0.99  # maximum AM mod. index
    internal_mod_freq = {0: 300, 1: 400, 2: 1000, 3: 3000, 4: 6000}  # internal modulation frequencies
    state_string_length = 42

    _set_cf: float  # currently set carrier frequency
    _set_amp: float  # currently set amplitude
    _set_amp_unit: str  # currently set amplitude unit  # TODO: use enum / type
    _set_fm_dev: float  # currently set FM deviation
    _set_am_mod_idx: float  # currently set AM modulation index
    _set_int_mod_freq: ModFrequencies  # currently selected mod. frequency or external mod. source
    _fm_on: bool
    _ext_fm_src: bool
    _fm_alc_on: bool
    _am_on: bool
    _ext_am_src: bool
    _am_alc_on: bool
    _pulse_mod_on: bool
    _carrier_on: bool
    _ext_std: bool
    _offset_on: bool

    def __init__(self, visa_resource: str = ""):
        super().__init__()
        if not visa_resource == "":
            self._connection = USBTMCConnection(visa_resource=visa_resource)
        else:
            self._connection = DummyConnection()
            self._is_dummy_dev = True

    def connect(self):
        """
        Connect to the instrument and check the length of the received data.
        There is no ID or answer, the instrument always responds with its state string that has a constant length.
        @return:
        """
        super().connect()
        with self._lock:
            connect_success = self._connection.connect()
            if connect_success == 0:
                rx = self.receive_data()  # 010400000000000000000060210608020000000000
                if len(rx) == self.state_string_length:
                    self._ok = True
                else:
                    self._ok = False

        if not self._ok:
            logger.error("Connection failed")

    def set_frequency(self, frequency: float, output_nr: int = 0) -> None:
        """
        Set frequency of RF output
        @param frequency:  in Hz
        @param output_nr: not used
        @return:
        """
        if not (frequency >= self.freq_min and frequency <= self.freq_max):
            logger.error(f"Frequency  {frequency} outside range [{self.freq_min} {self.freq_max}]")
            return

        f_unit: FreqUnits

        frequency, f_unit = _convert_freq_units(frequency)

        f_str = str(trunc(frequency * 1E8) / 1E8)  # Truncate Frequency to max. 5 digits

        with self._lock:
            self.send_command(f"CF {f_str} {f_unit.value}")

    def get_frequency(self, output_nr: float = 0) -> float:
        return self._set_cf  # TODO: check with values from device whenever updated (cache)

    def set_amplitude(self, amp: float, output_nr: int = 0, unit: str = "db", keep_output_off: bool = False) -> None:
        """
        Set output RF level

        !! IMPORTANT !!: Issuing this command activates the output, set keep_output_off to true to prevent this.

        @param amp: in V or dB depending on the value of <unit>,
                    check limits at top of file or in instrument documentation
        @param output_nr:  not used
        @param unit: unit of the amplitude: 'db' for decibels [default] or 'v'  for volts
        @param keep_output_off:  keep output off after setting level
        @return:
        """
        unit = unit.lower()

        amp_str: str
        if unit == "v":
            if not (amp >= self.ampl_v_min and amp <= self.amp_v_max):
                logger.error(f"Amplitude {amp}V outside voltage range [{self.ampl_v_min} {self.amp_v_max}]")
                return

            self._set_amp = amp
            self._set_amp_unit = unit

            voltage_unit: VoltageUnits
            amp, voltage_unit = _convert_volt_units(amp)

            # TODO: check if all cases are accounted for
            if amp >= 200:
                # Allow no digits after comma
                amp_str = str(trunc(amp))
            elif amp >= 100 or amp >= 20:
                # allow only one digit after comma
                amp_str = str(trunc(amp * 10) / 10)
            elif amp >= 10 or amp >= 2 or amp < 1:
                # only allow two digits after comma
                amp_str = str(trunc(amp * 100) / 100)
            else:
                # allow three digits after comma
                amp_str = str(trunc(amp * 1000) / 1000)

            if keep_output_off:
                amp_str += ', OF'
            with self._lock:
                self.send_command(f"LV {amp_str} {voltage_unit.value}")
        elif unit == "db":
            if not (amp >= self.ampl_db_min and amp <= self.amp_db_max):
                logger.error(f"Amplitude {amp} db outside decibel range [{self.ampl_db_min} {self.amp_db_max}]")
                return

            self._set_amp = amp
            self._set_amp_unit = unit

            amp_str = str(trunc(amp))

            with self._lock:
                self.send_command(f"LV {amp_str} DB{', OF' if keep_output_off else ''}")
        else:
            logger.error("Unit must be v (volts) or db (decibels)")

    def get_amplitude(self, output_nr: int = 0) -> float:
        return self._set_amp

    def enable_output(self, output_nr: int = 0) -> None:
        """
        Enable the output
        @param output_nr: not used
        @return:
        """
        with self._lock:
            self.send_command("LV ON")

    def disable_output(self, output_nr: int = 0) -> None:
        """
        Disable the output
        @param output_nr:  not used
        @return:
        """
        with self._lock:
            self.send_command("LV OF")  # Need to switch to RF output level or frequency command to turn output off
            # Otherwise ony the modulation or other parameter would be disabled

    def get_output_state(self, output_nr: int = 0) -> bool:
        return self._carrier_on

    def set_fm(self, deviation: float):
        """
        Set the FM deviation
        @param deviation:  in Hz
        @return:
        """

        if not (deviation >= self.dev_min or deviation <= self.dev_max):
            logger.error(f"FM Deviation {deviation} not in range [{self.dev_min} {self.dev_max}]")
            return
        dev_unit: FreqUnits

        deviation, dev_unit = _convert_freq_units(deviation)

        dev_str: str
        if deviation >= 100:
            # no digits after comma
            dev_str = str(trunc(deviation))
        elif deviation >= 10:
            # Allow one digit after comma
            dev_str = str(trunc(deviation * 10) / 10)
        else:  # deviation >= 1
            # Allow two digits after comma
            dev_str = str(trunc(deviation * 100) / 100)

        with self._lock:
            self.send_command(f"FM {dev_str} {dev_unit.value}")
            self._fm_on = True
            self._am_on = False

    def set_am(self, mod_idx: float = 0.85):
        """
        Set the AM modulation index
        @param mod_idx:  modulation index 0 - 0.99
        @return:
        """
        # TODO: CHECK with device
        if not (mod_idx >= self.mod_idx_min and mod_idx <= self.mod_idx_max):
            logger.error(f"AM modulation index {mod_idx} out of range [{self.mod_idx_min} {self.mod_idx_max}]")
            return

        mod_idx_str = str(trunc(mod_idx * 100))
        with self._lock:
            self.send_command(f"AM {mod_idx_str} PC")
            self._fm_on = False
            self._am_on = True

    def set_modulation_src(self, mod_src: ModFrequencies = ModFrequencies.F1k0):
        """
        Set the modulation source (internal or external)
        @param mod_src:  mod frequency index (see enum at top of file)
        @return:
        """
        mod_src_str: str
        if mod_src != ModFrequencies.ext:
            mod_src_str = f"{'FM' if self._fm_on and not self._am_on else 'AM'} IT, M{mod_src.value}"
        else:
            mod_src_str = f"{'FM' if self._fm_on and not self._am_on else 'AM'} XT"

        with self._lock:
            self.send_command(mod_src_str)

    def set_alc(self, on_off: bool = True):
        with self._lock:
            self.send_command(f"A{1 if on_off else 0}")
            if self._fm_on:
                self._fm_alc_on = on_off
            else:
                self._am_alc_on = on_off

    def get_alc(self) -> bool:
        return self._fm_alc_on if (self._fm_on and not self._am_on) else self._am_alc_on

    def _decode_state_string(self, state_str: str):
        """
        Decode the state string sent by the instrument and update the internal states
        It contains various values representing the current operating mode
        See Manual Chap. 3, Page 15

        AAAAAAAAAA BBBBBBBB CC DDDDDD EE FF GG PRSTUVWXYZ

        A: Carrier frequency in decahertz
        B: FM deviation in decahertz
        C: AM modulation index in percent
        D: RF level in dB relative to half the minimum level with fixed decimal point (DDD.DDD)
        E: RF level logarithmic units (00 - 06)
        F: RF level linear units (07, 07)
        G: Internal modulation oscillator frequency (00 - 04)

        The remaining positions are binary flags
        P: FM ON
        R: EXT FM source selected
        S: FM ALC ON
        U: EXT AM source selected
        V: AM ALC ON
        W: PULSE MOD ON
        X: CARRIER ON
        Y: EXT STD (freq. source) selected
        Z: OFFSET ON

        @param state_str:  state string received from the instrument
        @return:
        """
        # TODO : error fixing here
        if state_str == "":
            return
        if not state_str.isnumeric():
            return
        if not len(state_str) == self.state_string_length:
            return

        # This can be solved more elegant (struct + datatype sizes + binary),
        # but since it's only used once and not subject to change I will leave it this way
        cf_str = state_str[0:10]
        fm_dev_str = state_str[10:18]
        am_mod_idx_str = state_str[18:20]
        rf_lvl_db_str = state_str[20:26]
        rf_lvl_log_units_str = state_str[26:28]
        rf_lvl_lin_units_str = state_str[28:30]
        mod_osc_freq_str = state_str[30:32]
        flags_str = state_str[32:]

        cf = int(cf_str) * 10
        fm_dev = int(fm_dev_str) * 10
        am_mod_idx = int(am_mod_idx_str) / 100

        # TODO: rf level decoding

        mod_osc_freq_i = int(mod_osc_freq_str)
        mod_osc_freq_enum: ModFrequencies
        if mod_osc_freq_i in iter(ModFrequencies):
            if mod_osc_freq_i != ModFrequencies.ext:
                mod_osc_freq_enum = ModFrequencies(mod_osc_freq_i)
            else:
                logger.error(f"Got wrong value for internal mod oscillator index: {mod_osc_freq_i}")

        # TODO: decode flags

        # If everything decoded successfully set the internal values
        self._set_cf = cf
        self._set_fm_dev = fm_dev
        self._set_int_mod_freq = mod_osc_freq_enum if True else ModFrequencies.ext  # TODO: ext source is split in AM / FM, check device behaviour

    def read_state_string(self):
        state_str: str = ""
        with self._lock:
            state_str = self.receive_data()

        self._decode_state_string(state_str)

    # TODO: implement device error retrieval (SRQ mask etc.) + second level functions if needed
