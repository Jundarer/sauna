#from RPi import GPIO # geht NUR im Raspi!

class sauna:
    def __init__(self):
        # GPIO Variablen
        self.Rel_out = (31, 33, 35, 37)  # GPIO-Pins (N, R, S, T)
        #Def. Leistungs-Stufen
        self.kw0 = (0, 0, 0, 0)
        self.kw1 = (0, 0, 1, 1)
        self.kw2 = (1, 0, 0, 1)
        self.kw3 = (1, 0, 1, 1)
        self.kw4 = (1, 1, 1, 1)
        self.leistungsStufe = (
            self.kw0, self.kw1, self.kw2, self.kw3, self.kw4)
        self.stufenMerker = 0
        self.init_GPIO()

    def init_GPIO(self):
        """Konfiguriert die GPIO pins"""
        # GPIO konfig
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setwarnings(False)
        # for i in Rel_out:
        #     GPIO.setup(i, GPIO.OUT)
        #     GPIO.output(i, False) # Am Anfang alles auf Null!
        # nun sind die out-pins konfiguriert!

        # Ermitteln des Temperatur-Files (Seite 315) gilt NUR für den PI!
        # und der Sensor MUSS angeschlossen sein!
        #os.system("modprobe wire")      # modprobe nicht nötig
        #os.system("modprobe w1-gpio")   # ist in boot-config festgelegt
        #os.system("modprobe w1-therm")
        return
    
    def starten(self, aktuelleTemp, sollTemp):
        """Startet die Sauna mit der gegeben Ziel Temperatur"""
        print("Sauna startet mit dem Ziel {} Grad".format(sollTemp))
    
    def stoppen(self):
        """Stoppt das Heizen der Sauna"""
        print("Sauna gestoppt!")