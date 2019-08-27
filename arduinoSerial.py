#!/usr/bin/env python

"""
ArduinoSerial.py -> Python serial help tool to stream data to serial components
Author: Michel Cantacuzene <michel@thesweaterguys.com>
GitHub: michmich112
Copyright: The Sweater Guys
"""

import serial
import serial.tools.list_ports
import serial.serialutil
import serialConf
from listMenu import menu

def open_connection(ser):
    ser.open()
    return ser.is_open

def test_connection(ser):
    print("> Testing connection ... ")
    print(ser)
    if open_connection(ser):
        print("> [PASS] Connection parameter success")
        ser.close()
        return True
    else:
        print("> [FAIL] Connection parameter Failure")
        return False

def test_configuration(conf):
    print("> Testing serial configuration(s)")
    for p in conf:
        print("> Testing configuration for " + conf[p]["name"] or conf[p]["port"])
        try:
            s = serial.Serial(port=conf[p]["port"], baudrate= conf[p]["baudrate"], timeout=conf[p]["timeout"])
            test_connection(s)
        except serial.serialutil.SerialException as e:
            print (e)

def connect_manual_serial(ser):
    con = str(raw_input("> Open connection? [y/n]\n"))
    if con == "y":
        if open_connection(ser):
            print("> [SUCCESS] Serial Connection to Port: " + ser.port + "  open.")
            print("> Enter \"quit()\" to close connection an exit")
            inp = str(raw_input(">"))
            while inp != "quit()":
                print("> Sending \"" + inp +"\"")
                ser.write(inp+"\n") # Add EOL character
                ser.flush() # Flush input stream
                print("> Received: " + ser.readline())
                inp = str(raw_input(">"))

            print("Exiting serial Connection")
            ser.close()
            print("> Connection to port " +ser.port + " closed.")
            print("> Exiting")
            quit(1)
        else:
            print("> [FAIL] Failre to connect to Port: " + ser.port + ".")
            print(ser)
            print("> Exiting")
            quit(1)
    else:
            print("> Exiting")
            quit(0)

# Allows the user to choose a port within the selected configuration
# Returns the serial object with the  proper configuration loaded
def choose_port_and_connect(conf):
    p = menu(conf.keys(), "Please select a port to open")
    try:
        s = serial.Serial(port=conf[p]["port"], baudrate=conf[p]["baudrate"], timeout=conf[p]["timeout"])
        if test_connection(s):
            connect_manual_serial(s)
        else:
            print("> Impossible to connect to serial port " + p)
    except serial.serialutil.SerialException as e:
        print("> Impossible to connect to serial port " + p)
        print(e)

def main():
    conf = serialConf.load_config()
    test_configuration(conf)
    choose_port_and_connect(conf)

if __name__ == '__main__':
    main()