#!/usr/bin/env python3
# coding=utf-8

""" File name: ModBus_RTU_master.py Author: Zenkin Artemii Date created: 6/20/2018 Date last modified: 6/23/2018 Python Version: 3
"""

import minimalmodbus
import serial
import time
import os

debug = False

parity = 'N'
bytesize = 8
stopbits = 1
timeout = 0.05

register = {
    'temperature': 258,
    'humidity': 259,
    'network_address_of_the_device': 4,
    'exchange_rate': 5,
    'device_response_delay': 6,
    'number_of_stopbits': 7,
    'software_version': 16
}

function = {
    'read': 3,
    'write': 6
}

decimals_number = {
    0: 0,
    1: 1,
    2: 2
}

class HTT100:

    sensors_count = 0

    def __init__(self, port, slave_adress, baudrate, parity, bytesize, stopbits, timeout):
        minimalmodbus.BAUDRATE = baudrate
        minimalmodbus.PARITY = parity
        minimalmodbus.BYTESIZE  = bytesize
        minimalmodbus.STOPBITS  = stopbits
        minimalmodbus.TIMEOUT = timeout
        try: 
            self.instrument = minimalmodbus.Instrument(port, slave_adress, mode='rtu')
        except:
            print("No connection to " + str(port) + " or permission denied")
        else:
            self.instrument.mode = minimalmodbus.MODE_RTU # set rtu mode
        HTT100.sensors_count += 1
        self.index = HTT100.sensors_count
        if debug:
            print("    ---------------------------")
            print("    |      SENSOR "+str(HTT100.sensors_count)+"   INFO    |")
            print("    ---------------------------")
            print("  ", "Port: ".ljust(20), str(port).ljust(40))
            print("  ", "Slave adress: ".ljust(20), str(slave_adress).ljust(40))
            print("  ", "Boudrate: ".ljust(20), str(baudrate).ljust(40))
            print("  ", "Parity: ".ljust(20), str(parity).ljust(40))
            print("  ", "Bytesize: ".ljust(20), str(bytesize).ljust(40))
            print("  ", "Stopbits: ".ljust(20), str(stopbits).ljust(40))
            print("  ", "Timeout: ".ljust(20), str(timeout).ljust(40))
            print("")


    def __del__(self):
        if debug:
            print('Сенсор {0} отключен'.format(self.index))
        HTT100.sensors_count -= 1
        if debug:
            if HTT100.sensors_count == 0:
                print('Все датчики отключены')
            else:
                print('Осталось {0:d} работающих датчиков'.format(HTT100.sensors_count))


    def get_temperature(self):
        try:
            self.temperature = self.instrument.read_register(register['temperature'], decimals_number[2], function['read'], signed=True)
            return self.temperature
        except:
            print("no connection")


    def get_humidity(self):
        try:
            self.humidity = self.instrument.read_register(register['humidity'], decimals_number[2], function['read'])
            return self.humidity
        except:
            print("no connection")


    def get_network_address_of_the_device(self):
        try:
            self.network_address_of_the_device = self.instrument.read_register(register['network_address_of_the_device'], decimals_number[0], function['read'])
            return self.network_address_of_the_device
        except:
            print("no connection")

    def get_exchange_rate(self):
        try:
            self.exchange_rate = self.instrument.read_register(register['exchange_rate'], decimals_number[0], function['read'])
            return self.exchange_rate
        except:
            print("no connection")


    def get_device_response_delay(self):
        try:
            self.device_response_delay = self.instrument.read_register(register['device_response_delay'], decimals_number[0], function['read'])
            return self.device_response_delay
        except:
            print("no connection")


    def get_number_of_stopbits(self):
        try:
            self.number_of_stopbits = self.instrument.read_register(register['number_of_stopbits'], decimals_number[0], function['read'])
            return self.number_of_stopbits
        except:
            print("no connection")


    def get_software_version(self):
        try:
            self.software_version = self.instrument.read_register(register['software_version'], decimals_number[0], function['read'])
            return self.software_version
        except:
            print("no connection")


    def get_device_information(self):
        try:
            print("    network_address_of_the_device: " + str(self.get_network_address_of_the_device()) + "\n"
              + "    exchange_rate: "               + str(self.get_exchange_rate())                 + "\n" 
              + "    device_response_delay: "       + str(self.get_device_response_delay())         + "\n"
              + "    number_of_stopbits: "          + str(self.get_number_of_stopbits())            + "\n"
              + "    software_version: "            + str(self.get_software_version())              + "\n")
        except:
            print("no connection to " + str(port))
