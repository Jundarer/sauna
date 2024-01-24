import os
from time import *
import threading
import logging

debug = False
# Instantiate the logger
logger = logging.Logger('log.txt')
try:
    from RPi import GPIO
except (ImportError, RuntimeError) as e:
    logger.log("Sauna-Modul wird im Debug-Modus gestartet, da das RPi Modul nicht gefunden wurde oder das Gerät kein Raspi ist.")
    debug = True

AKTUELLE_TEMP_UPDATE_INTERVAL = 2
SAUNA_UPDATE_INTERVAL = 10

class sauna:
    """Steuert die direkte Kommunikation mit der Sauna"""

    def __init__(self):
        self.deviceFile = ""
        self.aktuelleTemp = 70
        self.sollTemp = 0
        self.deltaTemp = 0
        self.ersterStart = True
        # GPIO Variablen
        self.Rel_out = (31, 33, 35, 37)  # GPIO-Pins (N, R, S, T)
        #Def. Leistungs-Stufen
        self.kw0 = (1, 1, 1, 1)
        self.kw1 = (0, 1, 1, 0)
        self.kw2 = (1, 1, 0, 0)
        self.kw3 = (0, 1, 0, 0)
        self.kw4 = (0, 0, 0, 0)
        self.leistungsStufe = (
            self.kw0, self.kw1, self.kw2, self.kw3, self.kw4)
        self.stufenMerker = 0
        self.init_GPIO()
        self.initDeviceFile()
        self.saunaAktiv = False   # True, wenn der Loop aktiv ist        
        self.init_threads()       # Threads

    def init_GPIO(self):
        """Konfiguriert die GPIO pins"""
        # GPIO konfig
        if not debug:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            for i in self.Rel_out:
                GPIO.setup(i, GPIO.OUT)
                GPIO.output(i, True)  # Am Anfang alles auf Null!
                                       # nun sind die out-pins konfiguriert!
                                       # Ermitteln des Temperatur-Files (Seite 315) gilt NUR für den PI!
                                       # und der Sensor MUSS angeschlossen sein!
            os.system("modprobe wire")      # modprobe nicht nötig
            os.system("modprobe w1-gpio")   # ist in boot-config festgelegt
            os.system("modprobe w1-therm")

    def initDeviceFile(self):
        if os.path.isdir("/sys/bus/w1/devices"):
            for d in os.listdir("/sys/bus/w1/devices"):
                if d.startswith("10") or d.startswith("28"):
                    if os.path.isfile("/sys/bus/w1/devices/" + d + "/w1_slave"):
                        self.deviceFile = "/sys/bus/w1/devices/" + d + "/w1_slave"

    def init_threads(self):
        self.aktuelleTempUpdateThread = threading.Thread(
            target=self.tempUpdate, args=())
        self.aktuelleTempUpdateThread.daemon = True
        self.aktuelleTempUpdateDebugThread = threading.Thread(
            target=self.tempUpdateDebug, args=())
        self.aktuelleTempUpdateDebugThread.daemon = True
        self.saunaSteuerungThread = threading.Thread(
            target=self.saunaLoop, args=())
        self.saunaSteuerungThread.daemon = True
        # Thread nur starten, wenn die Temperatur geupdatet werden kann
        if(os.path.isfile(self.deviceFile)):
            self.aktuelleTempUpdateThread.start()
        # Sonst im Debug Modus die Sauna simulieren
        elif debug:
            self.aktuelleTempUpdateDebugThread.start()
        self.saunaSteuerungThread.start()

    def starten(self):
        """Startet die Sauna mit der gegeben Ziel Temperatur"""
        if self.saunaAktiv==False:
            logger.log("Sauna startet mit dem Ziel {} Grad".format(self.sollTemp))
            # Sauna loop thread auf aktiv setzen
            self.saunaAktiv = True

    def stoppen(self):
        """Stoppt das Heizen der Sauna"""
        self.saunaAktiv = False
        self.stufenMerker = 0
        self.updatePorts()
        logger.log("Sauna gestoppt!")

    def tempUpdate(self):
        while(True):
            first, second = "",""
            while first.find("YES") == -1:
                with open(self.deviceFile) as f:
                    file=f.readlines()
                    if(len(file)==2):
                        first, second = file
            tempString = second.split("=")[1]
            neueTemp = int(tempString)/1000
            self.deltaTemp = neueTemp-self.aktuelleTemp
            self.aktuelleTemp = neueTemp
            sleep(AKTUELLE_TEMP_UPDATE_INTERVAL)

    # Simuliert die Sauna (allerdings ohne Traegheit, aber besser als nichts)
    def tempUpdateDebug(self):
        while(True):
            neueTemp = self.aktuelleTemp+(self.stufenMerker/4)-0.2
            logger.log("Alte Temp: " +
                  str(round(self.aktuelleTemp,1))+"\nNeue Temp: "+str(round(neueTemp,1))+"\nStufe: "+str(self.stufenMerker))
            self.deltaTemp = neueTemp-self.aktuelleTemp
            self.aktuelleTemp = neueTemp
            sleep(AKTUELLE_TEMP_UPDATE_INTERVAL)

    def saunaLoop(self):
        # Dieser Loop läuft dauernd, fuehrt aber nur die Logik, wenn die Sauna aktiv ist.
        while (True):
            while self.saunaAktiv:
                # bei dem ersten Start bis +3° auf voller Leistung heizen
                if self.ersterStart:
                    if self.sollTemp-self.aktuelleTemp > -3:
                        self.stufenMerker = 4
                    else:
                        self.ersterStart = False
                # Wenn wir nicht mehr im ersten Start-Modus sind
                if not self.ersterStart:
                # bei mehr als -5° sofort volle Leistung
                    if self.sollTemp-self.aktuelleTemp >= 5:
                        self.stufenMerker = 4
                    # bei mehr als +2° sofort aus
                    elif self.sollTemp-self.aktuelleTemp <= -2:
                        self.stufenMerker = 0
                    # bei mehr als -0.5° erhöhen
                    elif self.sollTemp-self.aktuelleTemp >= 0.5:
                        self.erhöhen()
                    # bei mehr als +0.5° vermindern
                    elif self.sollTemp-self.aktuelleTemp <= -0.5:
                        self.vermindern()
                self.updatePorts()
                if debug:
                    logger.log("Saunaleistung wurde aktualisiert auf: " +
                          str(self.stufenMerker))
                sleep(SAUNA_UPDATE_INTERVAL)
            # Warte bis die Sauna aktiviert wird
            sleep(1)

    def erhöhen(self):
        # falls steigende Temperatur und Unterschied zum Soll <=1.5 runterschalten
        if self.deltaTemp > 0 and self.sollTemp-self.aktuelleTemp <= 1.5:
            self.updateMerker(-1)
        # sonst hochschalten
        else:
            self.updateMerker(1)

    def vermindern(self):
        # falls fallende Temperatur und Unterschied zum Soll >=-1 hochschalten
        if self.deltaTemp < 0 and self.sollTemp-self.aktuelleTemp >= -1:
            self.updateMerker(1)
        # sonst runterschalten
        else:
            self.updateMerker(-1)

    def updateMerker(self, delta):
        if self.stufenMerker+delta >= 0 and self.stufenMerker+delta <= 4:
            self.stufenMerker = self.stufenMerker+delta

    def updatePorts(self):
        if not debug:
            i=0
            for x in self.Rel_out:
                GPIO.output(x, self.leistungsStufe[self.stufenMerker][i])
                i=i+1
