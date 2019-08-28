"""
serial_cli.py -> Python serial cli tool
Author: Michel Cantacuzene <michel@thesweaterguys.com>
GitHub: michmich112
Copyright: The Sweater Guys
"""

from os import path
from time import  sleep
from listMenu import y_n_choice
import serial.serialutil

VERSION = 0.1

class SerialCli:

    def __init__(self, ser):
        self.ser = ser
        self.commands = {
            "stream" : {
                "desc": "Stream a file line by line to the serial port.",
                "args": {}, # TODO add proper args : print result and EOL
                "lambda": self.stream
            },
            "grbl" : {
                "desc": "Stream a gcode file to a grbl interpreter through serial.",
                "args": {"-s":"Settings mode","--rx=":"Set RX Buffer Size (in bits)."},
                "lambda": self.stream_grbl
            },
            "listen" : {
                "desc": "Listen and print serial output",
                "args": {},
                "lambda": self.listen
            },
            "converse" : {
                "desc": "Start a Write and Read conversation through serial",
                "args": {},
                "lambda": self.converse
            },
            "help": {
                "desc": "Display the help menu",
                "args": {},
                "lambda": self.help
            },
            "exit": {
                "desc": "Exit the Serial Cli",
                "args": {},
                "lambda": self.exit
            }
        }

        # open serial port if not open
        if not self.ser.is_open:
            try:
                ser.open()
            except serial.serialutil.SerialException as e:
                print(str(e))
                raise Exception(str(e))


    # Main control method for the CLI tool
    def cli(self):
        print(">> Port: " + str(self.ser.port) + "\n>> Name: " + str(self.ser.name) + "\n>> Baud Rate: " + str(self.ser.baudrate))
        print("> Serial CLI V"+str(VERSION)+" started")
        print("> Use \'help\' to get help and \'exit\' to exit the serial cli.")
        try:
            ex = False
            while not ex:
                command = str(raw_input("> "))
                if command.split(' ')[0] in self.commands.keys() and command.split(' ')[0] != "exit":
                    # TODO handle args
                    self.commands[command.split(' ')[0]]["lambda"]()
                elif command.split(' ')[0] == "exit":
                    ex = self.exit()
            print("> Exiting Serial CLI")
        except KeyboardInterrupt:
            print("> Keyboard Interrupt Detected")
            print("> Exiting Serial CLI")


    # Allows the user to stream a file over serial
    def stream(self, res=False, eol=True):
        try:
            print("> File Stream [START]")
            filename = get_filename_from_user()
            print("> Starting File Stream")
            with open(filename, 'r') as f:
                for line in f:
                    l = line.strip()  # Strip all EOL characters for consistency
                    print 'Sending: ' + l,
                    self.ser.write(l + ('\n' if eol else ''))  # Send data add eol if argument is passed
                    self.ser.flush() # flush output buffer
                    if res:
                        response = self.ser.readline()  # Wait for grbl response with carriage return
                        print ' : ' + response.strip()
        except KeyboardInterrupt:
            print("> Keyboard Interrupt Detected")
            print("> Stopping file stream to port " + str(self.ser.port))
            print("> File Stream [END]")

    # Allows optimized streaming of g-code files to GRBL interpreter
    def stream_grbl(self, settings=False, rx_buffer_size=128):
        try:
            print("> G-Code/GRBL Stream [START]")
            filename = get_filename_from_user()
            if y_n_choice("Start G-Code/GRBL stream?"):

                # Taken from https://github.com/grbl/grbl/blob/master/doc/script/stream.py
                # Original author Sungeun K. Jeon

                with open(filename,'r') as f:
                    # Stream g-code to grbl
                    l_count = 0
                    if settings:
                        # Send settings file via simple call-response streaming method. Settings must be streamed
                        # in this manner since the EEPROM accessing cycles shut-off the serial interrupt.
                        print("> SETTINGS MODE: Streaming" + filename + " to " + str(self.ser.port))
                        for line in f:
                            l_count += 1  # Iterate line counter
                            # l_block = re.sub('\s|\(.*?\)','',line).upper() # Strip comments/spaces/new line and capitalize
                            l_block = line.strip()  # Strip all EOL characters for consistency
                            print('>> SND: ' + str(l_count) + ':' + l_block)
                            self.ser.write(l_block + '\n')  # Send g-code block to grbl
                            grbl_out = self.ser.readline().strip()  # Wait for grbl response with carriage return
                            print('>> REC:' + grbl_out)
                    else:
                        # Send g-code program via a more agressive streaming protocol that forces characters into
                        # Grbl's serial read buffer to ensure Grbl has immediate access to the next g-code command
                        # rather than wait for the call-response serial protocol to finish. This is done by careful
                        # counting of the number of characters sent by the streamer to Grbl and tracking Grbl's
                        # responses, such that we never overflow Grbl's serial read buffer.
                        g_count = 0
                        c_line = []
                        # periodic() # Start status report periodic timer
                        for line in f:
                            l_count += 1  # Iterate line counter
                            # l_block = re.sub('\s|\(.*?\)','',line).upper() # Strip comments/spaces/new line and capitalize
                            l_block = line.strip()
                            c_line.append(len(l_block) + 1)  # Track number of characters in grbl serial read buffer
                            grbl_out = ''
                            while sum(c_line) >= rx_buffer_size - 1 | self.ser.inWaiting():
                                out_temp = self.ser.readline().strip()  # Wait for grbl response
                                if out_temp.find('ok') < 0 and out_temp.find('error') < 0:
                                    print(">> Debug: " +  out_temp ) # Debug response
                                else:
                                    grbl_out += out_temp;
                                    g_count += 1  # Iterate g-code counter
                                    grbl_out += str(g_count);  # Add line finished indicator
                                    del c_line[0]  # Delete the block character count corresponding to the last 'ok'
                            print(">> SND: " + str(l_count) + " : " + l_block)
                            self.ser.write(l_block + '\n')  # Send g-code block to grbl
                            print(">> BUF:" + str(sum(c_line)) + "REC:" + grbl_out)
            else:
                print("> G-Code/GRBL Stream [CANCELED]")
        except KeyboardInterrupt:
            print("> Keyboard Interrupt Detected")
            print("> Stopping G-Code/GRBL stream to port " + str(self.ser.port))
            print("> G-Code/GRBL Stream [END]")


    # Allows the user to listen to outputs of the serial port
    def listen(self):
        try:
            print("> Listen [START]")
            while True:
                dat = str(self.ser.readline())
                if dat != "":
                    print(dat)
        except KeyboardInterrupt:
            print("> Listen [END]")

    # Allows the user to converse over serial
    def converse(self):
        try:
            print("> Converse [START]")
            print("> Enter \"quit()\" to exit")
            inp = str(raw_input(">"))
            while inp != "quit()":
                print("> Sending \"" + inp + "\"")
                self.ser.write(inp + "\n")  # Add EOL character
                self.ser.flush()  # Flush input stream
                print("> Received: " + self.ser.readline())
                inp = str(raw_input(">"))
            print("> Stopping conversation with port " + str(self.ser.port))
            print("> Converse [END]")
        except KeyboardInterrupt:
            print("> Keyboard Interrupt Detected")
            print("> Stopping conversation with port " + str(self.ser.port))
            print("> Converse [END]")

    # Prints the help menu for the serial Cli
    def help(self):
        print(">> Help menu. Here are the commands you can use in Serial CLI V" + str(VERSION))
        for key in self.commands.keys():
            print(">>> " + str(key) + " : " +str(self.commands[key]["desc"]))


    # Allows the user to exit the cli, closing the serial port in the process
    def exit(self):
        self.ser.close()
        return True




def get_filename_from_user():
    f = str(raw_input("> File path: "))
    exists = path.exists(f)
    while not exists:
        print("> Incorrect file path: " + f)
        f = str(raw_input("> File path: "))
    return f

def grbl_init(ser):
    # Wake up grbl
    print("> Initializing grbl...\r")
    ser.write("\r\n\r\n")

    # Wait for grbl to initialize and flush startup text in serial input
    sleep(2)
    ser.flushInput()
    print("> Initializing grbl [SUCCESS]")