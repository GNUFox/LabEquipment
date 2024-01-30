# LabEquipment

My attempt at creating an easy-to-use Python module for interaction with Test and Measurement Equipment.  
The devices can be connected by different means ((usb)serial, telnet, USB-to-GPIB-adaptors)

This project is just done for fun and does not claim full coverage of the operating modes/instructions of all supported instruments.
Hence, devices in the "supported devices" support at least the basic commands (Example: frequency, offset, amplitude and waveform of an AWG).


## Supported devices
* OR-X 402A Arbitrary Waveform Generator
* HP6632B PSU
* MARCONI INSTRUMENTS signal generator 2019
* HP8954A Transceiver Interface

### Building in progress
* HP3457A DMM
* HP34401A DMM
* Wavetek 4032 Stabilock Communication tester
* MARCONI INSTRUMENTS modulation meter 2305

## Currently supported connection types

* [Xyphro's UsbGpib adaptor](https://github.com/xyphro/UsbGpib) via python-usbtmc


### Building in progress
* PROLOGIX USB to GPIB adaptor
* Simple Serial (usb serial)
* telnet
