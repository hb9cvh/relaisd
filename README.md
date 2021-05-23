# Ein Driver-Programm um Relais-Ausgänge mit MQTT zu steuern
Relaisd ist ein recht einfaches Python Programm welches als daemon 
oder neu als systemd Programm gestartet wird. Es ersetzt meine Lösung mit 
node-red auf dem Raspi, funktioniert sogar auf einem RaspiZero mit 
raspian light
- MQTT gesteuert
- MQTT statusmeldungen
- frei definierbar bis zu 8 ports
- Direkte oder inverse Ausgänge
- Starteinstellung definierbar
- Config Utility beiliegend

## Vorbereitung und installation
### Linux (raspi buster) 
Installieren von raspian (buster) wie üblich. Es kann auch raspian light sein, denn es wird kein GUI benötigt. 
### Python 3.6 oder neuer
Ist meist automatisch installiert. Es braucht noch RPi.GPIO
 >sudo apt update
 >sudo apt install rpi.gpio

### MQTT Server (lokal oder remote)
Hier verweise ich auf (install mosquitto[https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/])

### node-red oder Haus Automation
Hier eine gute Anleitung (install Node-Red [http://www.steves-internet-guide.com/installing-node-red/]) Damit steuere ich meine Geräte.
Es gibt noch viele andere Möglichkeiten. z.B. MQTT Client vom App Store

### Programme installieren
 >mkdir relaisd
Einfügen der Programme in dieses Verzeichnis:

* Relais.py        GPIO treiber für einen Ausgang
* Savestat.py      Save a variableOrArray on file-system
* relaisd.py       MQTT systemd driver für 1 - 8 Ausgänge
* relaisd_conf.py  Programm um relaisd zu configurieren
* relaisd.conf     Beispiel configuration JSON
* relaisd.service  Eintrag um relaisd mit systemd zu starten

## Konfiguration
Da relaisd für verschiedene Geräte benutzbar sein muss, muss man es für jeden Anwendungsfall richtig einstellen. Dazu das Programm relaisd_conf starten
  
  python3 relaisd_conf.py

Configure relaisd daemon  
Enter file name for this config  
default is -relaisd.conf- : <   **demo.conf**   
   --- Global configuration values    
Switch debuging on = 1 or off = 0    
DEBUG : 0 <   **0**  
new :  0   
   --- Constants for the WLAN and MQTT connection      
Hostname or IP-Number of the MQTT server     
_IP Address or Full Qualified Hostname_  
MQHOST : x.x.x.x <   **123.123.123.11**     
new :  123.123.123.11   
Username for MQTT logon  
MQUSER : xxxxxxx <   **tester**  
new :  tester  
Password for MQTT login  
MQPWD : xxxxxxx <   **theodor**  
new :  theodor  
MQTT QOS request 0,1,2  
MQQOS : 1 <   **1**   
new :  1   
Client name (may be left blank)  
MQCLIENT : relais-1 <   **rel**  
new :  rel  
MQTT Topic to use  
MQTOPIC : kw/master/ <   **kw/relais**  
new :  kw/relais  
   --- Define drivers for the relais   
GPIO Numering Default=BOARD or BCM   
_press Enter to take default_
RELAIS_GPIO : GPIO.BOARD <  ** _Enter_ **  
List of all relaisports used ( list)  
_Here we have 8 Relais in a row_  
RELAIS_PORTS : 5, 6, 13, 16, 19, 20, 21, 26 <  ** _Enter_ **  
List of initial states of the relais 0=Off 1=ON  
_We have some relais switching on when daemon starts_  
RELAIS_STATE : 0, 0, 0, 0, 0, 0, 0, 0 <  ** 1,1,0,0,0,1,0,0 **                     
new :  1,1,0,0,0,1,0,0  
Relais-name (may be left blank)  ** _Enter_ **  
Function of the IO output (Normal=0) (Inverse=1)  
_Here we need 1 as the relais driver is inverting_   
RELAIS_FUNCT : 1 <   **1**   
new :  1  
   ---Define the execution loop timings    
Loop execution intervall default = 0.1 sec  
INTERVAL : 0.1 <    ** _Enter_ **  
Send Relais status every n loops default 3000 = 5 Min)  
STATE : 30000 <   ** _Enter_ **  

>*****  New config  *****   
>MQPWD theodor  
>STATE 30000  
>RELAIS_GPIO GPIO.BOARD  
>RELAIS_PORTS [5, 6, 13, 16, 19, 20, 21, 26]  
>INTERVAL 0.1  
>RELAIS_FUNCT 1  
>MQUSER tester  
>MQCLIENT rel
>MQQOS 1  
>RELAIS_STATE 1,1,0,0,0,1,0,0  
>MQTOPIC kw/relais  
>MQHOST 123.123.123.11  
>DEBUG 0  
>***** Configuration saved to:  demo.config

### Test der config

>python3 relaisd.py  demo.conf

Wenn Debug mit 1 configuriert wurde, so wird nun das wichtigste vom Programm angezeigt. Weiter ist es dann sehr einfach mit einem MQTT-Sniffer oder mit Node-Red die MQTT Messages zu sehen oder zu generieren

Abbrechen des Programms mit CTL_C

nun muss noch das noch als Exec Programm markiert werden  

>chmod + x relaisd.py  

Damit kann man es direkt starten, zB. ./relaisd.py ./relaisd.conf 

## Erstellen der systemd Datei

ein Beispiel ist im File relaisd.service abgelegt. Die Argumentliste bei ExecStart muss alles auf einer Zeile sein, mit dem  \  wurde dies im Text nur angedeutet.

```
[Unit]
Description=mqtt_driven_relais_driver
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi/relaisd/relaisd.py /home/pi/relaisd/relaisd.conf /tmp/relaisd.save

[Install]
WantedBy=multi-user.target
```
Dieses File muss nun mit **sudo** unter /etc/systemd/system/relaisd.service 
abgespeichert werden.
ACHTUNG: ExecStart= und alle 3 Argumente müssen auf einer Zeile stehen!
_Das Argument /tmp/relaisd.save wird ab Version 1.2 benötigt_, wenn man
will, dass der Zusand der Relais nach einem Unterbruch wieder hergestellt
wird. Ohne wird nichts gespeichert und es wird wesentlich weniger auf die
SD-Karte geschrieben.

### Starten des Daemons
Ist die systemd.service Datei installiert, so kann relaisd.service gestartet werden.

    sudo systemctl daemon-reload  # daemon config laden
    sudo systemctl enable relaisd.service  # Einrichten
    sudo systemctl start relaisd  # starten

Nun sollte das ganze funktionieren ! Man kann auch prüfen ob der Daemon läuft:
   sudo systemctl status relaisd

## Uebersicht der MQTT Schnittstelle
Mit dem MQTT Protokoll können einfache Befehle und Informationen verteilt werden. Jede kommunikation hat 2 Teile:
topic = Thema (Hier meist die Bezeichnung des Geräts zB. ort/gerät)
payload = Befehl oder Info (On, Off 32.5 usw)

Relaisd verwendet ein topic dazu 1 oder 2 subtopic's 
Beispiel kw/relais (KurwellenStation kw und relaisplatine die ich da schalten kann). 
### subtopic cmd
Subtopic cmd ist ein Befehl. Da hier mehrere Relais (Ausgänge) zur Verfügung stehen, wird noch angegeben welches Relais den Befehl erhalten soll. Also cmd/1 oder cmd/2 

Die payload ist 1 wenn Eingeschaltet werden soll, eine 0 zum Ausschalten.
   kw/relais/cmd/4  1  -> schaltet das Relais 4 ein

### subtopic stat
Damit die Steuerzentrale weiss, dass der Befel verstanden und ausgeführt wurde, erfolgt eine Rückmeldung ebenso mit topic und payload
   kw/relais/stat/4  1  -> relais 4 eingeschaltet
Alle 5 Min (300sec) wird der Zusand jedes Relais versendet.

### subtopic LWT
LWT steht für den 'letzten Willen'. Dabei wird bei dem MQTT Server der letzte Staus gesetzt. Dieser Status wird gespeichert und zurück gegeben wenn man eine Abfrage macht. Hier ist das ganz einfach:
  kw/relais/LWT   Online   -> kw/relais system ist online
das wird ca. alle 5 Min (300s) gesendet. Wenn das Programm sich beendet oder sich vom MQTT Server trennt, so wird der letze Wille auf
  kw/relais/LWT  Offline   -> kw/relais ist ausgeschaltet
somit kann man damit auch ein Timeout des relaisd daemons feststellen

## Node-Red Steuerung
Anbei sind auch ein Beispiel zum steuern eines Ausgangs mit tip (on/off) beigelegt.  
File: nodered_relais.nr    
und eine einfache Überwachung der Funktion mit Fehlermeldung und grey-out der Anzeige dabei:  
File: nodered_timeout.nr  

### Fehler und/oder Anregungen
