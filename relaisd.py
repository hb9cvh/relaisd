#!/usr/bin/python3

"""  
Relais (switch) control with MQTT connection

Controled by a node-red driven system
Configuration from relaisd.conf (json file). Use relaisd_conf.py
to set or edit the configuration.

Author Johann Maurer
Version  1.1  2020-07-25
- added get Config File Name from 1. calling param
- better configuration from Config File
- better comments
Revision 1.0  2020-07-23

To do
- save relaisstatus localy or via node-red
- set constants via webserver

--- sudo apt install python3-paho-mqtt
"""
 
import time
import paho.mqtt.client as mqtt
import os.path
import glob
import sys
import queue
import json
import logging
import RPi.GPIO as GPIO
from Relais import Relais 

# Local list to store commands comming from mqtt
cmnd_list = queue.Queue() # used as FiFo
# initialise the logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

def log(text = '', mess='') :
    """
    Send text and message to the log when DEBUG
    is set to True
    """
    global CONF
    if  CONF['DEBUG'] == True:
        logging.info(str(text)+': '+str(mess))
        # print (text,mess)

def get_param(pos) :
    """
    Get the command-line argument as pos
    """
    arglist = sys.argv
    return arglist[pos]

def get_config (cfile) :
    """
    Read the configuration file and set the
    configuration info into CONF dict
    """
    try :
        print ('cfile : ',cfile)
        cf = open(cfile,'r')
        jconf = cf.read()
        # print (jconf)
        CONF = json.loads(jconf)
        cf.close()
        return CONF
    except :
        print ('not found file : ',cfile)
        return False
   
# define Values for the relais
def init_GPIO(relais_ports,relais_state) :
    """
    Define a new instance of a relais for every port in the list
    relais_ports. Internaly the relais are numbererd in the given 
    sequence from 0 to length of list  
    """
    GPIO.setwarnings(False)
    log (relais_ports)
    relist=[]
    for i in range(len(relais_ports)):
        log ("init relist = ",str(i))
        relist.append( Relais(relais_ports[i],'rel'+str(i),False, True,GPIO.BCM)) # erstellen Objekt rel1 mit Bezeichnung Sch Auf
        log ("index = "+str(i),relist[i].get_id())
        relist[i].set(relais_state[i])
        log ("relais "+str(i)+' set to ',relais_state[i])
    return relist

def exec_cmnd(cmnd_list,relist) :
    """ 
    Execute the commands in the FiFo queue. Each entry has the 
    form topic and commend. Main-Topic is extended by /cmd/xx
    where xx is the relais number starting at 1 ( internal 0)
    """
    global CONF
    while not cmnd_list.empty():
        cmnd = cmnd_list.get()
        rel = cmnd[0].replace(CONF['MQTOPIC']+'cmd/','')
        cmd = int(cmnd[1])
        relais_nr = int(rel)-1
        log ("exec_cmd ", str(rel) +" = "+str(cmd))
        if cmd == b'On' or cmd == b'1' or cmd == 1 :
            switch_set = True
        elif cmd == b'Off' or cmd == b'0' or cmd == 0:
            switch_set = False
        else :
            log ("exec_cmnd **** ERROR **** unknown command ",str(cnmd))
            return False
        relist[relais_nr].set(switch_set)
        if switch_set : 
            mqtt_sta = 1
        else:
            mqtt_sta = 0
        client.publish (CONF['MQTOPIC']+"stat/"+rel,payload=mqtt_sta, qos=0, retain=False)      
    return

def send_status(relist) :
    """
    Periodically we send the actual status for every relais
    The main topic is extended by "stat/"+ status (0 = off 1 = on)
    """
    global CONF
    # log ("send_status")
    for i in range(len(relist)):
        rstat = relist[i].get()
        if rstat :
            mqtt_sta = 1
        else:
            mqtt_sta = 0
        client.publish (CONF['MQTOPIC']+"stat/"+str(i+1),payload=mqtt_sta, qos=0, retain=False)
        log ("status sent ",str(i+1)+" = "+str(mqtt_sta))
    return 

# ---------- MQTT message Handler

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    """
    As soon as the connection to mqtt server ist done we
    recieve the status information here
    """ 
    global CONF, client_connected
    client_connected = str(rc)
    log ("on connect","Connected with result code "+str(rc))

def on_disconnect (client,userdata,rc ):
    """
    when the client is disconnected we recieve a message.
    rc = 0 we have send a client disconnet
    rc  != 0 we have an error
    """
    global client_connected
    log ("disconnect : ",userdata," return code = ",str(rc))
    client_connected = 0

def on_message(client, userdata, msg):
    """
    This cllback stores each command comming from mqtt and
    put it into the global cmnd_list. This is done very quick
    and the mqtt task can continue
    """
    global cmnd_list
    log (msg.topic,msg.payload)
    cmnd = [msg.topic,msg.payload]
    cmnd_list.put(cmnd)
    return 

def connect_mqtt () :
    """ 
    connect to MQTT broker with all needed information
    """
    global CONF
    client = mqtt.Client(client_id=CONF['MQCLIENT'], clean_session=False, userdata=None, protocol=mqtt.MQTTv311)
    client.username_pw_set(CONF['MQUSER'], password=CONF['MQPWD'])
    client.will_set (CONF['MQTOPIC']+'LWT','Offline',retain=False)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(CONF['MQHOST'], port=1883, keepalive=60)
    client.subscribe(CONF['MQTOPIC']+"cmd/#")
    log("connect MQTT ","client connected")
    return client

def send_stat (relais_nrß) :
    """
    confirm the status of the relais (internal number)
    Called after every execution of a command and used
    by node-red to change the color of push button
    """
    global CONF
    for i in range(0,len(relist)) :
        if relist[i].get() : 
            mqtt_sta = 1
        else:
            mqtt_sta = 0
        rel = str(i+1)
        client.publish (CONF['MQTOPIC']+"stat/"+rel,payload=mqtt_sta, qos=0, retain=False)   


# ----  Main Program ----
#
#------------------------
"""
Main part of the mqtt relais daemon

First part: Read and set configuration varable CONF
            initialise the communication to MQTT server
"""
client_connected = 0
logging.info('relaisd daemon starting')
# read config. -- Is required 
cfile = get_param(1)
# print ('param 1 : ',cfile)
CONF = get_config(cfile) # CONF now a global var
if CONF == False :
    logging.error('relaisd config file '+cfile+' missing ' )
    sys.exit(2)
# 
starting = time.time()

# setup the GPIO channels defined in the list RELAIS_PORTS 
# each defined port must be connected to a relais
relist = init_GPIO(CONF['RELAIS_PORTS'],CONF['RELAIS_STATE']) # init up to 8 relais on these ports
#init MQTT Connection used by this driver
client = connect_mqtt()

"""
start the threaded interface to mqtt
it will run in the background and listen on
the mqtt commands with subscribe topic
"""
client.loop_start()

"""
Second part: Notify the MQTT server that we are online
            send the actual state of the relais
"""
# Inform MQTT broker that we are on line
client.publish (CONF['MQTOPIC']+"LWT",payload='Online', qos=1, retain=False)
# set node-red info at current state
send_status(relist)
"""
Third part: the main loop
        We count the loops, check for messages, start
        execution and send regularly status messages
"""
uptime = 0 #the starting uptime
switch_time = 0
run = True 
while run :
    uptime += 1  # increment counter
    # execute all commands in the list
    if cmnd_list.qsize() > 0 :
        exec_cmnd(cmnd_list,relist)

    if (uptime  > int(CONF['STATE'])): 
        log ('relaisd up for '+str(int(time.time()-starting))+' sec')
        # inform the MQTT server that the comand ist done
        client.publish (CONF['MQTOPIC']+"LWT",payload='Online', qos=1, retain=False)
        log ("sent ",CONF['MQTOPIC']+"LWT  Online")
        send_status(relist)
        # log ("sent relais status")
        uptime = 1
    if client_connected == 0 :
        log ("**** lost client connection ****'")
        run = False
    time.sleep(0.1)
    pass

client.disconnect()
logging.warning('relaisd daemon terminated')
print ('Bye')
exit()
