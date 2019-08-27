"""
SerialConf.py -> Python tool to identify or generate configuration files
Author: Michel Cantacuzene <michel@thesweaterguys.com>
GitHub: michmich112
Copyright: The Sweater Guys
"""

import json
from os import path
from listMenu import y_n_choice,input_handler

defaultFilePath = "serialconf.json"

# Checks for conf file with defaultFilePath or user input filePath with priority on user input
def get_conf_file(file_path = None):
    file_name = file_path or defaultFilePath
    if path.exists(file_name):
        with open(file_name,'r') as confFile:
            return json.load(confFile)
    else:
        print("> [ WARNING ] no file found with path " + file_name)
        return None

# Loads the configuration file if possible,
# Prompts the user to configure ports manually or create a file through cli
def load_config(file = None):
    data = get_conf_file(file)
    if data is None:
        if y_n_choice("Would you like to create a new config file?"):
            data = create_config()
        else:
            print("> Manual Configuration chosen.")
            data = manual_config()
    else:
        print("> Configuration file found")
    return data

# Creates a manual configuration from user input
def manual_config():
    config = {}  # holds the config data
    add_new = True
    while add_new:
        port = input_handler("Port = ", retry=True)
        br = input_handler("Baud Rate (9600) = ", default=9600, acc_type=int, retry=False)
        timeout = input_handler("Timeout (1s) = ",default=1, acc_type=int, retry=False)
        name = input_handler("Custom port name (Optional) = ", default=None, retry=False)
        config[port] = {
            "port":port,
            "baudrate": br,
            "timeout": timeout,
            "name": name
        }
        add_new = y_n_choice("Would you like to add another port configuration?")

    return config

# User input to create and save a new config file
def create_config():
    config = manual_config()
    print("> Writing config to serialconf.json")
    with open(defaultFilePath,'w') as config_file:
        json.dump(config, config_file)
    print("> Config generated. Add this file to your git repository for future use.")
    return config