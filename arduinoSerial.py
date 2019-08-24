import serial

def openConnection(ser):
    ser.open()
    return ser.is_open

ser = serial.Serial()
ser.baudrate = input("> BaudRate = ")
ser.timeout = input("> Timeout = ")
ser.port = str(raw_input("> Port = "))
print(ser)
print("> Testing connection ... ")
if openConnection(ser):
    print("> [SUCCESS] Connection parameter success")
    ser.close()
else:
    print("> [FAIL] Connection parameter Failure")
    print("> Exiting")
    quit(1)

con = str(raw_input("> Open connection? [y/n]\n"))
if con == "y":
    if openConnection(ser):
        print("> [SUCCESS] Serial Connection to Port: " + ser.port + "  open.")
        print("> Enter \"quit()\" to close connection an exit")
        inp = str(raw_input(">"))
        while inp != "quit()":
            print("> Sending \"" + inp +"\"")
            ser.write(inp+"\n") # Add EOL character
            ser.flush() # Flush input stream
            print("> Received: " + ser.readline())
            inp = str(raw_input(">"))

        print("Exiting serial Connection");
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
