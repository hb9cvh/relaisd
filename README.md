# A driver program to control relay outputs with MQTT
Relayd is a quite simple Python program which is started as daemon 
or as a systemd program. It replaces my old solution with 
node-red on the Raspi, and even works on a RaspiZero with 
raspian light
- MQTT controlled
- MQTT status messages
- free definable, up to 8 ports
- direct or inverse outputs
- Startup setting definable
- Config Utility included

## Preparation and installation
### Linux (raspi buster) 
Install raspian (buster) as usual. It can also be raspian light, because no GUI is needed. 
### Python 3.6 or newer
Is mostly installed automatically. It still needs RPi.GPIO
 >sudo apt update
 >sudo apt install rpi.gpio

### MQTT Server (local or remote)
Here I refer to (install mosquitto[https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/])

### node-red or house automation
Here is a good tutorial (install node-red [http://www.steves-internet-guide.com/installing-node-red/]). I use this to control my devices.
There are many other possibilities. e.g. MQTT Client from the App Store

### Install programs
 >mkdir relaisd
Paste the programs into this directory:

* Relay.py GPIO driver for an output
* Savestat.py Save a variableOrArray on file-system
* relaisd.py MQTT systemd driver for 1 - 8 outputs
* relaisd_conf.py program to configure relaisd
* relaisd.conf example configuration JSON
* relaisd.service entry to start relaisd with systemd

## configuration
Since relaisd has to be usable for different devices, you have to configure it correctly for each use case. To do this start the program relaisd_conf
  
  python3 relaisd_conf.py

Configure relaisd daemon  
Enter file name for this config  
default is -relaisd.conf- : < **demo.conf**   
   --- Global configuration values    
Switch debugging on = 1 or off = 0    
DEBUG : 0 < **0**  
new : 0   
   --- Constants for the WLAN and MQTT connection      
Hostname or IP number of the MQTT server     
_IP Address or Full Qualified Hostname_  
MQHOST : x.x.x.x < **123.123.123.11**     
new : 123.123.123.11   
Username for MQTT logon  
MQUSER : xxxxx < **tester**  
new : tester  
Password for MQTT login  
MQPWD : xxxxxxx < **theodor**  
new : theodor  
MQTT QOS request 0,1,2  
MQQOS : 1 < **1**   
new : 1   
Client name (may be left blank)  
MQCLIENT : relay-1 < **rel**  
new : rel  
MQTT Topic to use  
MQTOPIC : kw/master/ < **kw/relais**  
new : kw/relais  
   --- Define drivers for the relay   
GPIO Numering Default=BOARD or BCM   
press Enter to take default
RELAY_GPIO : GPIO.BOARD < ** _Enter_ **  
List of all relay ports used ( list)  
_Here we have 8 relays in a row_  
RELAIS_PORTS : 5, 6, 13, 16, 19, 20, 21, 26 < ** _Enter_ **  
List of initial states of the relay 0=Off 1=ON  
_We have some relay switching on when daemon starts_  
RELAIS_STATE : 0, 0, 0, 0, 0, 0, 0 < ** 1,1,0,0,0,1,0,0 **                     
new : 1,1,0,0,0,1,0,0  
Relay name (may be left blank) ** _Enter_ **  
Function of the IO output (Normal=0) (Inverse=1)  
_Here we need 1 as the relay driver is inverting_   
RELAY_FUNCT : 1 < **1**   
new : 1  
   ---Define the execution loop timings    
Loop execution interval default = 0.1 sec  
INTERVAL : 0.1 < ** _Enter_ **  
Send relay status every n loops default 3000 = 5 min)  
STATE : 30000 < ** _Enter_ **  

>***** New config *****   
>MQPWD theodor  
>STATE 30000  
>RELAY_GPIO GPIO.BOARD  
>RELAIS_PORTS [5, 6, 13, 16, 19, 20, 21, 26]  
>INTERVAL 0.1  
>RELAY_FUNCT 1  
>MQUSER tester  
>MQCLIENT rel
>MQQOS 1  
>RELAIS_STATE 1,1,0,0,1,0,0  
>MQTOPIC kw/relais  
>MQHOST 123.123.123.11  
>DEBUG 0  
>***** Configuration saved to: demo.config

### Test the config

>python3 relaisd.py demo.conf

If debug was configured with 1, the most important messages of the program are now displayed. Further it is very easy to see or generate the MQTT messages with a MQTT sniffer or with Node-Red.

Cancel the program with CTL_C

now the file must be made executable

>chmod + x relaisd.py  

With this you can start it directly, e.g. ./relaisd.py ./relaisd.conf 

## Create the systemd file

The argument /tmp/relaisd.save is required from version 1.2 onwards if you want the
to restore the state of the relays after an interruption. Without nothing is saved and less is written to the
SD card.

### Starting the daemon
If the systemd.service file is installed, relaisd.service can be started.

    sudo systemctl daemon-reload # load daemon config
    sudo systemctl enable relaisd.service # set it up
    sudo systemctl start relaisd # start the service

Now the whole thing should work ! You can also check if the daemon is running:
   sudo systemctl status relaisd

## Overview of the MQTT interface
With the MQTT protocol simple commands and information can be distributed. Each communication has 2 parts:
topic = topic (here mostly the name of the device e.g. location/device)
payload = command or info (On, Off 32.5 etc)

Relay uses a topic in addition 1 or 2 subtopic's 
Example kw/relais (KurwellenStation kw and relaisplatine which I can switch there). 
### subtopic cmd
Subtopic cmd is a command. Since here several relays (outputs) are available, you have to specify which relay should receive the command. 
Relais 1 or 2 = cmd/1 or cmd/2 

The payload is 1 when switching on, a 0 for switching off.
   kw/relais/cmd/4 1 -> switches relay 4 on

### subtopic stat
That the control center knows if the command has been understood and executed, a feedback is given with topic and payload
   kw/relais/stat/4 1 -> relay 4 switched on
Every 5 min (300sec) the status of each relay is sent.

### subtopic LWT
LWT stands for 'last will'. The last status is set at the MQTT server. This state is stored and returned when you make a query. 
It is :
  kw/relais/LWT Online -> kw/relais system is online
this is sent approx. every 5 min (300s). If the program terminates or disconnects from the MQTT server, the last will be sent to
  kw/relais/LWT Offline -> kw/relais is switched off
so you can also detect a timeout of the relaisd daemon with it

## Node-Red control
Attached is also an example to control an output with tip (on/off).  
File: nodered_relais.nr    
it includes a simple monitoring of the function with error message and grey-out of the display are included:  
File: nodered_timeout.nr  

### Error and/or suggestions
use github of mail to john(at)hb9cvh(dot)ch

Traduction from German to English with help of deepl.com

