class Error(Exception):
    """Base exception class"""
    pass


class WrongDeviceType(Error):
    """There is a device at the given connection but it's the wrong type"""
    pass


class DeviceCommunicationError(Error):
    """General Error while communicating with the device"""
    pass


class InvalidDeviceParameter(Error):
    """Parameter does not match device constraints (e.g. invalid channel numer)"""
    pass


class InvalidUsage(Error):
    """Invalid function usage"""
    pass


class UiErrorMessage(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class UiStatusMessage(Error):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"
