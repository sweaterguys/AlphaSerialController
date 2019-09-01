"""
ListMenu.py -> Python menu tools and functions
Author: Michel Cantacuzene <michel@thesweaterguys.com>
GitHub: michmich112
Copyright: The Sweater Guys
"""

# function that takes in an array of values and prompts the user to select one
# returns selected value
def menu(values, message=None):
    print("> " + (message or "Please select an option."))
    for i in range(len(values)):
        print("[" + str(i) + "] " + str(values[i]))
    choice = input_handler("enter a number between 0 and " + str(len(values)-1)+": ", acc_type=int,retry=True)
    while choice>=len(values) or choice<0 :
        choice = input_handler("enter a number between 0 and " + str(len(values) - 1) + ": ", acc_type=int, retry=True)
    return values[choice]

# Method to handle a yes or no choice returning the choice as a boolean
def y_n_choice(message):
    tmp = str(raw_input("> " + message + "[y/n]\n"))
    while tmp != 'y' and tmp != 'Y' and tmp != 'n' and tmp != 'N':
        print("> Please answer with y (yes) or n (no).")
        tmp = str(raw_input("> " + message + "[y/n]\n"))
    return tmp == 'y' or tmp == 'Y'

# Returns the default if a reject value is entered and retry is false
# Prompts the user to input a value that is not in the reject list and is of the correct type is retry is True
def input_handler(message, default=None, acc_type = None, reject=[""], retry=True):
    val = str(raw_input("> " + message))
    conf = acc_type is None
    if val in reject and not retry: # return default if no need to retry and the input matches the retry
        return default
    while (val in reject) and retry:
        print("> Value " + val + " is not permitted, please retry")
        val = str(raw_input("> " + message))
    while not conf:
        try:
            val = acc_type(val) # cast the value and except an error
            conf = True
        except ValueError as e:
            print(e)
            print("> Value " + val + " is not permitted, please retry")
            val = str(raw_input("> " + message))
    return val
