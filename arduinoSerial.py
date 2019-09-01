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
from listMenu import menu, y_n_choice
from serial_cli import SerialCli, get_filename_from_user
from re import findall


def open_connection(ser):
    if not ser.is_open:
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
            s = serial.Serial(port=conf[p]["port"], baudrate=conf[p]["baudrate"], timeout=conf[p]["timeout"])
            test_connection(s)
        except serial.serialutil.SerialException as e:
            print (e)


@DeprecationWarning
def connect_manual_serial(ser):
    con = str(raw_input("> Open connection? [y/n]\n"))
    if con == "y":
        if open_connection(ser):
            print("> [SUCCESS] Serial Connection to Port: " + ser.port + "  open.")
            print("> Enter \"quit()\" to close connection an exit")
            inp = str(raw_input(">"))
            while inp != "quit()":
                print("> Sending \"" + inp + "\"")
                ser.write(inp + "\n")  # Add EOL character
                ser.flush()  # Flush input stream
                print("> Received: " + ser.readline())
                inp = str(raw_input(">"))

            print("Exiting serial Connection")
            ser.close()
            print("> Connection to port " + ser.port + " closed.")
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
    ex = False
    while not ex:
        p = menu(conf.keys(), "Please select a port to connect to")
        try:
            s = serial.Serial(port=conf[p]["port"], baudrate=conf[p]["baudrate"], timeout=conf[p]["timeout"])
            if test_connection(s):
                # connect_manual_serial(s)
                SerialCli(s).cli()
            else:
                print("> Impossible to connect to serial port " + p)
        except serial.serialutil.SerialException as e:
            print("> Impossible to connect to serial port " + p)
            print(e)


def parse_swtr_line(l):
    return findall("\"([^\"]*)\"", l)


def get_ports_for_swtr_file(filename):
    p = 0
    with open(filename, 'r') as f:
        for l in f:
            if len(parse_swtr_line(l)) > p: p = len(parse_swtr_line(l))
    return p


def multi_stream(conf):
    print("> Multi Stream From file")
    filename = get_filename_from_user()
    print("> Analyzing SWTR file ...")
    num_ports = get_ports_for_swtr_file(filename)
    if num_ports < 1:
        print("> [ERROR] Empty SWTR file")
    else:
        # TODO enable configuration edition
        print("> Need " + str(num_ports) + " port(s) to execute SWTR file")
        ports = []
        conf_ser = {}
        for key in conf.keys():  # open only one instance of all the conf ports -> messy TODO clean this up
            try:
                conf_ser[key] = serial.Serial(port=conf[key]["port"], baudrate=conf[key]["baudrate"],
                                          timeout=conf[key]["timeout"])
            except Exception as e:
                print e
        for i in range(num_ports):  # select the ports to be used
            ports.append(SerialCli(conf_ser[menu(conf_ser.keys(), "Select port number " + str(i + 1))]))
        if y_n_choice("Start Multi Stream on file " + filename):
            print("> [START] Starting Multi Stream")
            with open(filename, 'r') as f:
                for line in f:
                    data = parse_swtr_line(line)
                    for n in range(num_ports):
                        data[n] = data[n].replace("\\n","\n")
                        if data[n] != "null": ports[n].direct(data[n])
            print("> [END] Multi Stream finished")
        else:
            print("> [CANCELLED] Multi Stream Cancelled")


def service_menu(conf):
    ex = False
    options = ["Serial Cli", "Multi Stream from file", "Cancel"]
    while not ex:
        choice = menu(options)
        if choice == "Serial Cli":
            choose_port_and_connect(conf)
        elif choice == "Multi Stream from file":
            multi_stream(conf)
        elif choice == "Cancel":
            ex = True
        else:
            print("> Invalid choice/configuration")


def main():
    try:
        conf = serialConf.load_config()
        test_configuration(conf)
        # choose_port_and_connect(conf)
        service_menu(conf)
    except KeyboardInterrupt:
        print("> Keyboard Interrupt detected. Exiting.")
        quit(1)


if __name__ == '__main__':
    main()
