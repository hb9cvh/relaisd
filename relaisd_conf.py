#!/usr/bin/python3
"""
relaisd_conf.py

Configuration of the initial values for relaisd

Relaisd need a lot of parameters and read this from a json file
This programm ask for all needed params and save the values
in the file relaisd.conf

"""
import json

def conf_text () :
    conftext = [
    '**Global configuration values',
    'Switch debuging on = 1 or off = 0',
    'DEBUG' ,
    '**Constants for the WLAN and MQTT connection',
    'Hostname or IP-Number of the MQTT server',
    'MQHOST' ,
    'Username for MQTT logon',
    'MQUSER' ,
    'Password for MQTT login',
    'MQPWD',
    'MQTT QOS request 0,1,2',
    'MQQOS' ,
    'Client name (may be left blank)',
    'MQCLIENT',
    # main topic for this allication
    'MQTT Topic to use',
    'MQTOPIC' ,
    '**Define drivers for the relais',
    # for my tests I use 8 relais
    'GPIO Numering Default=BOARD or BCM ',
    'RELAIS_GPIO' ,
    'List of all relaisports used [list]',
    'RELAIS_PORTS',
    'List of initial states of the relais 0=Off 1=ON',
    'RELAIS_STATE' ,
    'Relais-name (may be left blank)',
    'Function of the IO output (Normal=0) (Inverse=1)',
    'RELAIS_FUNCT' ,
    # define the interval between each scanning loop
    '**Define the execution loop timings',
    'Loop execution intervall default = 0.1 sec',
    'INTERVAL' ,
    'Send Relais status every n loops default 3000 = 5 Min)',
    'STATE' ,
    ]
    return conftext

# define defauls
def conf_defaults() :
    conf = {
    'DEBUG' : 0,
    'MQHOST' : "x.x.x.x",
    'MQUSER' : 'xxxxxxx',
    'MQPWD'  : "xxxxxxx",
    'MQQOS'  : 1,
    'MQCLIENT' : "relais-1",
    'MQTOPIC' : "kw/master/",
    'RELAIS_GPIO' : 'GPIO.BOARD',
    'RELAIS_PORTS' : [5,6,13,16,19,20,21,26],
    'RELAIS_STATE' : [0,0,0,0,0,0,0,0],
    'RELAIS_FUNCT' : 1,
    'INTERVAL' : 0.1,
    'STATE'  : 30000,
    }
    return conf

def edit_conf(conf,conftext) :
    # print (conftext)
    CONF = conf

    for i in range(0,len(conftext)) :
        te = conftext[i]
        if te[0:1] == '*' :
            print ('   *'+te+'  ***')
            continue
        if len(te) > 15 :
            print (te)
            continue
        else :
            cval = str(conf[te])
            if cval[0] == '[' :
                cval = list_to_string(cval)
            inp = input(te+' : '+cval+' < ')
            if len(inp) < 1 :
                CONF[te] = conf[te]
            else :
                print ('new : ',inp)
                CONF[te] = inp
    return CONF

def get_config (cfile='relaisd.conf') :
    # get configuration
    try :
        cf = open(cfile,'r')
        conf = json.loads(cf.read())
        cf.close()
        return conf
    except :
        # not found
        return False

def put_config (conf,cfile='relaisd.conf') :
    # save configuration
    try:
        cf = open(cfile,'w')
        cf.write(json.dumps(conf))
        cf.close()
        return True
    except :
        return False

def list_to_string (string) :
    # print(string)
    string = string.replace('[','')
    string = string.replace(']','')
    string = string.replace("'",'')
    # print (string)
    return string

def conv_config (conf) :
    """
    Some data musst be convertet to be of correct
    data type for the relaisd program
    """
    for x in conf :
        cval = conf[x]
        print (x,cval)
        if x == 'DEBUG' or x == 'RELAIS_FUNCT' :
            conf[x] = int(cval)
            continue
        if x == 'RELAIS_PORTS'  or x =='RELAIS_STATE':
            # make shure that the lists elements are of type int
            # print (type(cval),' : ',cval)
            if type(cval).__name__ == 'str':
                # print ('handle as a string')
                lval = cval.split(',') # lval is now a list
                # print ('lval ',lval)
                for i in range(0,len(lval)) :
                    lval[i] = int(lval[i])
                cval = lval
            # print (type(cval),' : ',cval)
            conf[x] = cval
            continue
        if x == 'RELAIS_GPIO' :
            cval = cval.replace('GPIO.','')
            if cval == 'BOARD' or 'BCM' :
                conf[x] = 'GPIO.'+cval
            continue
    return conf

#####
print ('Configure relaisd daemon')
print ('Enter file name for this config')
cfile = 'relaisd.conf'
fname = input('default is -relaisd.conf- :')
if len(fname) > 0 :
    cfile = fname
conf = get_config(cfile)
if conf == False :
    conf = conf_defaults()
    put_config (conf)
conftext = conf_text()
conf = edit_conf(conf,conftext)
print ('*****  New config  *****')
conf = conv_config(conf)
if put_config(conf,cfile) == False :
    print ('ERROR: Could not write config to ',cfile,' !!')
    sys.exit(1)
else :
    # print (conf)
    print ('***** Configuration saved to: ',cfile)

print ('Thanks ')

