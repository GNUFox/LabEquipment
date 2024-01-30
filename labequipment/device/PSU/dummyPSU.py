from labequipment.device.PSU import PSU
from labequipment.framework import exceptions
import abc
import logging

logger = logging.getLogger('root')

# TODO: remove old stuff
class dummyPSU(PSU.PSU):

    def __init__(self, output_states=None,
                 get_voltages=[0], get_currents=[0],
                 get_measured_voltages=None, get_measured_currents=None,
                 CC_status=None, CV_status=None, count_type=1):
        """initialize a dummy / placeholder PSU with predefined values  
        
        output_states [(bool), ...]:            list of output states.
                                                The length of this list defines the number of outputs the PSU has  
        get_voltages [(float), ...]:            list of set voltages  
        get_currents [(float), ...]:            list of set currents  
        get_measured_voltages [(float), ...]:   list of measured voltages  
        get_measured_currents [(float), ...]:   list of measured currents
        CC_status [(bool), ...]:                list of CC_status  
        CV_status [(bool)], ...]:                list of CV_status
        count_type:                             Define where output counting starts (0 or 1)
        
        The length of the output_states list defines the amount of outputs the PSU has.  
        Each list that follows must be smaller or equal to that size.  
        If the list is shorter than the output_states list,  
        it will be expanded to the full size by padding with the last value.  
        Even if it's only a single value, the argument MUST always be a list (e.g. get_voltages = [1.23])  
          
        Example:   
        output_states = [false, false, false] # PSU has 3 outputs  
        get_voltages = [1.0] # only one entry given
        ==> get_voltages = [1.0, 1.0, 1.0] # Same voltage is set for every output
        """

        logger.info("Setting up dummy PSU")
        logger.info(f"{vars()}")

        _max_outputs = len(output_states)

        # check if all arguments have correct size / length
        for arg in vars().values():
            print(arg)
            if arg is None:
                raise exceptions.InvalidDeviceParameter
            elif isinstance(arg, list):
                if len(arg) > _max_outputs:
                    raise exceptions.InvalidDeviceParameter

        self.output_states = output_states
        self.get_voltages = get_voltages
        self.get_currents = get_currents
        self.get_measured_voltages = get_measured_voltages
        self.get_measured_currents = get_measured_currents
        self.CC_status = CC_status
        self.CV_status = CV_status

        # Padding for value lists
        last = get_voltages[-1]
        while len(self.get_voltages) < _max_outputs:
            self.get_voltages.append(last)

        last = get_currents[-1]
        while len(self.get_currents) < _max_outputs:
            self.get_currents.append(last)

        last = get_measured_voltages[-1]
        while len(self.get_measured_voltages) < _max_outputs:
            self.get_measured_voltages.append(last)

        last = get_measured_currents[-1]
        while len(self.get_measured_currents) < _max_outputs:
            self.get_measured_currents.append(last)

        last = CC_status[-1]
        while len(self.CC_status) < _max_outputs:
            self.CC_status.append(last)

        last = CV_status[-1]
        while len(self.CV_status) < _max_outputs:
            self.CV_status.append(last)

        self.offset = count_type

    def set_voltage(self, voltage, output_nr):
        logger.debug(f"SET OP {output_nr} Volt {voltage}")
        self.get_voltages[output_nr - self.offset]

    def get_voltage(self, output_nr):
        logger.debug(f"GET OP {output_nr} Volt")
        return self.get_voltages[output_nr - self.offset]

    def get_measured_voltage(self, output_nr):
        logger.debug(f"MEAS OP {output_nr} Volt")
        return self.get_measured_voltages[output_nr - self.offset]

    def set_current(self, current, output_nr):
        logger.debug(f"SET OP {output_nr} Ampere {current}")
        self.get_currents[output_nr - self.offset]

    def get_current(self, output_nr):
        logger.debug(f"GET OP {output_nr} Ampere")
        return self.get_currents[output_nr - self.offset]

    def get_measured_current(self, output_nr):
        logger.debug(f"MEAS OP {output_nr} Ampere")
        return self.get_measured_currents[output_nr - self.offset]

    def enable_output(self, output_nr):
        logger.debug(f"SET OP {output_nr} State enabled")
        self.output_states[output_nr - self.offset] = True

    def disable_output(self, output_nr):
        logger.debug(f"SET OP {output_nr} State disabled")
        self.output_states[output_nr - self.offset] = False

    def get_output_state(self, output_nr):
        logger.debug(f"GET OP {output_nr} State")
        return self.output_states[output_nr - self.offset]

    def get_cc_status_live(self, output_nr):
        logger.debug(f"GET OP {output_nr} CC_State")
        return self.CC_status[output_nr - self.offset]

    def get_cv_status_live(self, output_nr):
        logger.debug(f"GET OP {output_nr} CV_State")
        return self.CV_status[output_nr - self.offset]

    def lock_panel(self):
        pass

    def set_local(self):
        pass

    def _send_command(self, command):
        pass

    def _receive_data(self):
        pass

    def __getattr__(self, name):
        def function(*args):
            print(f"undefined function '{name}'")

        return function
