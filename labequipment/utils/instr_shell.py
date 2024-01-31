import sys
import argparse
import labequipment.framework.log
from labequipment.device import device
from labequipment.device.connection import USBTMCConnection, XyphroUSBGPIBConfig

import logging

logger = logging.getLogger('root')


class MyParser(argparse.ArgumentParser):

    def print_help(self, file=...):
        super().print_help()
        print("\nshell commands:\n")
        print("[INSTR COMMAND]            Send a command to an instrument")
        print("r[INSTR COMMAND]           Send a command to an instrument and expect an answer")
        print("                           If [INSTR COMMAND] is omitted, only expect an answer without asking")
        print("                           Example: r*IDN?")
        print("raw,<NUM>[,INSTR COMMAND]  Send a command to an instrument and expect a raw answer")
        print("                           <NUM> = number of bytes to receive must be given")
        print("                           [INSTR COMMAND] is optional and must be separated by a comma fom <NUM>")
        print("                           Example: raw,16,*IDN?")
        print("reconnect                  Reconnect the instrument (resets the connection)")
        print("xyph,<XYPHRO COMMAND>      Send a configuration command to the xyphro UsbGpib adaptor")
        print("                           <XYPHRO COMMAND> must be given")
        print("                           See https://github.com/xyphro/UsbGpib?tab=readme-ov-file#setting-parameters")
        print("\n")
        print("Example instrument interaction:\n")
        print("HOST: r*IDN?")
        print("INSTR: >HEWLETT-PACKARD,34401A,0,10-5-2<")
        print("HOST: CONF:VOLT:DC")
        print("HOST: INIT:IMM")
        print("HOST: rFETCH?")
        print("INSTR: >+4.82800000E-06<")
        print("\n")


class GenericInstrument(device.device):
    _connection: USBTMCConnection

    # TODO: add other connection types
    def __init__(self, visa_resource=""):
        super().__init__()
        if not visa_resource == "":
            if not visa_resource.endswith("::INSTR"):
                visa_resource += "::INSTR"
            self._connection = USBTMCConnection(visa_resource=visa_resource)

    def connect(self):
        connect_success = self._connection.connect()
        if connect_success == 0:
            print(f"Connection to {self._connection.get_visa_res()}")
            self._ok = True

    def receive_data_raw(self, n_bytes: int = -1) -> bytes:
        return self._connection.receive_data_raw(n_bytes)

    def send_xyphro(self, x: XyphroUSBGPIBConfig):
        return self._connection.xyphro_usb_gpib_adaptor_settings(x)


if __name__ == "__main__":
    parser = MyParser(description="Simple shell for instrument interaction")
    parser.add_argument('-v', '--visa-resource', type=str, dest='vres')
    args = parser.parse_args()

    visa_res_str = ""

    if args.vres:
        visa_res_str = args.vres
    else:
        print("Need visa resource with -v / --visa-resource or enter resource now: ")
        try:
            visa_res_str = input()
            if visa_res_str.lower() == "exit":
                sys.exit()
        except EOFError:
            sys.exit()
        if not visa_res_str:
            sys.exit()

    instr = GenericInstrument(visa_res_str)
    instr.connect()

    user_in = ""
    reply_expected = False
    instr_command = True
    xyphro_command = False
    command = ""
    xyphro_command_ref: XyphroUSBGPIBConfig
    no_bytes = 0
    terminator_add = ""
    while 1:
        try:
            user_in = input('HOST: ')
        except EOFError:
            break
        if user_in.lower() == "exit":
            break
        if user_in.lower() == "reconnect":
            instr.disconnect()
            del instr
            instr = GenericInstrument(visa_res_str)
            instr.connect()
            instr_command = False
        else:
            instr_command = True

        if instr_command:
            if user_in.startswith('r'):
                xyphro_command = False
                reply_expected = True
                if user_in.startswith('raw'):
                    user_in = user_in.split(',')
                    if len(user_in) == 3:
                        command = user_in[2]
                        no_bytes = int(user_in[1])
                    elif len(user_in) == 2 and not user_in[1].isnumeric():
                        # command without bytes, keep using previous setting
                        command = user_in[1]
                    elif len(user_in) == 2:
                        # Bytes
                        no_bytes = int(user_in[1])
                        command = ""
                    else:
                        # only 'raw', keep using previous no_bytes and no command
                        command = ""
                elif user_in == "r":
                    # just read (not raw)
                    command = ""
                else:
                    command = user_in[1:]
                    no_bytes = 0
            elif user_in.startswith("help"):
                parser.print_help()
                user_in = ""
                command = ""
                reply_expected = False
                xyphro_command = False
            elif user_in.startswith("xyph"):
                user_in = user_in.split(',')
                reply_expected = False
                command = ""
                if len(user_in) == 2:
                    # xyphro usb command
                    try:
                        xyphro_command_ref = XyphroUSBGPIBConfig(user_in[1])
                        xyphro_command = True
                    except ValueError:
                        print("Error, unknown command")
                else:
                    print("Error, command needs to be xypth,<command>")
            elif user_in.startswith("msgterm"):
                user_in = user_in.split(',')
                reply_expected = False
                xyphro_command = False
                command = ""
                if len(user_in) == 2:
                    match user_in[1]:
                        case 'lf':
                            terminator_add = '\n'
                        case 'cr':
                            terminator_add  = '\r'
                        case 'no':
                            terminator_add = ""
                        case _:
                            print("Error, terminator must be 'lf', 'cr', 'no'")
                else:
                    print("Syntax Error: 'msgterm,<term>'")
            else:
                reply_expected = False
                command = user_in

            if not command == "":
                instr.send_command(command)
            elif xyphro_command:
                print(f"Xyphro command reply: '{instr.send_xyphro(xyphro_command_ref)}'")

            if reply_expected:
                if no_bytes == 0:
                    print(f"INSTR: >{instr.receive_data()}<")
                else:
                    print(f"INSTR RAW [{no_bytes}]: >{instr.receive_data_raw(no_bytes)}<")

    print("Exiting")
    instr.disconnect()
