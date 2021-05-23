#!/usr/bin/python3
"""
Relais.py

A class to control relais or other users to 
switch on and off
The class instatiate an relais object defined by
- Pin (the selected IOpin of the system)
- name (a given name to identify the device)
- iniStatus (Status of the device (True = on, False = off))
- inverse (on some drivers we have to set output LOW
    to switch on (inverse=True))
- GPIO port definition to use

Usage:
from Relais import Relais
motor = Relais.init(PinNR, "Motor1",False,True) with your parameters!
print ("myMotorID = ", motor.get_id()) 
motor.set(True)  # start motor or use motor.set(1)
motor.set(False) # stop it or use motor.set(0)
print ("motor is ",motor.get()) # Return True if ON or False if OFF

Author Johann Maurer 
Version 1.1  15.07.2020 iniStatus,inverse,onoff now accept True/False or 1/0
Version 1.0  03.07.2020

ToDo
- Destructor to remove 
"""

import RPi.GPIO as GPIO
import time

# set debugging
DEBUGR = False

class Relais():
    def __init__(self,pin,name="",iniStatus=False,inverse=False,mode=GPIO.BOARD):
        """
        Init local varables used for this class
        Set IOpin and init output
        """
        self.pin = pin
        if name == "" :  name = "P-"+str(pin)
        self.name = name
        self.status = bool(iniStatus)
        self.inverse = bool(inverse)
        self.mode = mode
        GPIO.setmode(self.mode)
        GPIO.setup(pin, GPIO.OUT)
        if self.status != self.inverse : # != ist XOR
            GPIO.output(self.pin, GPIO.HIGH) #
        else:
            GPIO.output(self.pin, GPIO.LOW)
        if DEBUGR: print("init Relais: ",self.name, self.status)

    def get(self):
        """
        Return the status of the device (not IOPin voltage!)
        False = Off  True = On
        """
        if DEBUGR: print("Status Relais: ",self.name,self.status)
        return self.status

    def get_id(self):
        """
        Return the name of this device 
        """
        if DEBUGR : print("get_id = ",self.name)
        return self.name

    def set(self,onoff) :
        """
        Set the output to the requesed value
        True = ON,  False = OFF or
        1 = ON,0 = OFF
        """
        onoff = bool(onoff)
        if self.status == onoff :
            # Output is allredy in the requesed stat
            if DEBUGR: print("Relais already set ", self.name,self.status)
        if onoff != self.inverse : # != is XOR
            GPIO.output(self.pin, GPIO.HIGH)  # Set output to high
        else:
            GPIO.output(self.pin, GPIO.LOW)  # Set output to low
        self.status = onoff  # save actual status
        if DEBUGR: print("Set Relais: ",self.name, self.status)
        return self.status
# end class Relais

