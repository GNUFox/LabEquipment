import serial


class Prologix:
    """
    Abstraction class for use with the PROLOGIX USB-to-GPIB adaptor
    """
    _tty_connection: serial.Serial

    def __init__(self, serial_device):
        pass

    # TODO: implement prologix
