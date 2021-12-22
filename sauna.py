from tkinter import *
from datetime import datetime, timedelta
import os
import sys
import argparse
import sauna_kommunikation
#from RPi import GPIO # geht NUR im Raspi!

# Initialisiert den Argument Parser, welches Parameter aus der Kommandozeile ausliest
parser = argparse.ArgumentParser()
# Parameter "vollbild" wird als true gespeichert, wenn "--vollbild" bei der Ausfuehrung hinzugefuegt wird. Sonst ist es false
parser.add_argument('--vollbild', action='store_true',
                    help='Startet das Programm im Vollbildschirm-Modus')
# Speichert die Parameter in die "args" Variable
args = parser.parse_args()

# Konstanten
OWN_PATH = sys.path[0]
TEMP_UPDATE_INTERVAL=2000

# Helfer Funktion(en)
def canvasBildErsetzen(canvas, neues_bild):
    canvas.delete('all')
    canvas.create_image(5, 5, anchor=NW, image=neues_bild)

# Klasse, welche alles im Zusammenhang mit dem Fenster verwaltet
class kontroll_fenster:
    def __init__(self):
        # Hauptfenster
        self.fenster = Tk()
        # Zeit+Temperatur Variablen
        self.aktuelleZeit = datetime.now()
        self.schaltZeit = datetime.now()
        self.aktuelleTemp = 70
        self.sollTemp = 0
        # Status Variablen
        self.timerAktiv = False         # Hilfsmarke geplant zum stoppen
        # Liest die Programm args aus, um den initialen Vollbild-Modus zu setzen
        self.vollbild = args.vollbild
        # Wird gesetzt, falls die
        self.deviceFile = ""

        self.sauna=sauna_kommunikation.sauna()
        # inits
        self.init()

        self.fenster.bind("<F11>", self.vollbildToggle)
        self.fenster.bind("<Escape>", self.vollbildBeenden)

    def init(self):
        # Metadaten des Fensters setzen
        self.fenster.title(windowTitle)
        self.fenster.geometry("800x400")
        self.fenster.iconbitmap(os.path.join(OWN_PATH,"img","sauna_icon.ico"))
        # Alle Information unter Minuten von der Schaltzeit entfernen
        self.schaltZeit=self.schaltZeit-timedelta(seconds=self.schaltZeit.second,microseconds=self.schaltZeit.microsecond)
        # Falls mit dem Vollbild arg gestartet wurde, Vollbild akitivieren
        if self.vollbild:
            self.vollbildStarten()
        self.initDeviceFile()
        self.initSoll()

    def initSoll(self):
        """alten Sollwert(Temperatur) aus Datei holen"""
        with open(os.path.join(OWN_PATH,"solltemp.ini"), "r+") as f:
            neueTemp = f.read()
            if neueTemp != "":
                self.sollTemp = float(neueTemp)

    def initDeviceFile(self):
        if os.path.isdir("/sys/bus/w1/devices"):
            for d in os.listdir("/sys/bus/w1/devices"):
                if d.startswith("10") or d.startswith("28"):
                    self.deviceFile = "/sys/bus/w1/devices/" + d + "/w1_slave"

    def saveSoll(self, temp):
        """gültige Soll-Temperatur für später sichern."""
        self.sollTemp = temp
        with open(os.path.join(OWN_PATH,"solltemp.ini"), "w+") as f:
            f.write(temp)

    def ausschalten(self):
        """"Stop-Taste gedrückt"""
        self.timerAktiv = False
        aktuelleTemp_label.config(fg="blue4")
        canvasBildErsetzen(sauna_canvas, sauna_img)
        self.sauna.stoppen()

    def starten(self):
        """Starten-Taste gedrückt"""
        self.timerAktiv = True
        aktuelleTemp_label.config(fg="indian red")
        canvasBildErsetzen(sauna_canvas, sauna_warten_img)
        # Sauna bei neuem klicken von Start stoppen (?)
        self.sauna.stoppen()

    # nun gehts in die Hitze
    def regeln(self):
        print("nun soll geregelt werden")
        canvasBildErsetzen(sauna_canvas, sauna_aktiv_img)
        # hier nun das "Regel-Werk"!
        self.sauna.starten(self.aktuelleTemp, self.sollTemp)

    def zeitUpdate(self, timeLabel):
        """Definiert und initalisiert die Zeit updates"""
        # Funktion, die immer wieder aufgerufen wird, um die Zeitanzeige zu updaten
        def update():
            # Zeit updates
            self.aktuelleZeit = datetime.now()
            timeLabel['text'] = self.aktuelleZeit.strftime("%H:%M:%S")
            # Nach 1000ms diese Funktion wieder aufrufen
            timeLabel.after(1000, update)
            # Falls der Timer aktib ist die aktuelle Zeit mit der Schalt-Zeit vergleichen und wenn gleich: regeln
            if self.timerAktiv:
                if self.aktuelleZeit.strftime("%H:%M:%S") == self.schaltZeit.strftime("%H:%M:%S"):
                    self.regeln()
        # Initialer Aufruf der Funktion
        update()

    def tempUpdate(self, tempLabel):
        """Gleiches Prinzip wie in zeitUpdate"""
        def update():
            # Temp updates
            if os.path.isfile(self.deviceFile):
                first, second = ""
                while first.find("YES") == -1:
                    with open(self.deviceFile) as f:
                        first, second = f.readlines()
                tempString = second.split("=")[1]
                tempLabel['text'] = str(int(tempString)/1000)+"\b00B0"
            tempLabel.after(TEMP_UPDATE_INTERVAL, update)
        update()

    def anpassungZeit(self, hours, minutes):
        """Passt die Uhrzeit des sollTime labels relativ mit den gegeben Stunden und Minuten an"""
        self.schaltZeit = self.schaltZeit+timedelta(hours=hours, minutes=minutes)
        schaltZeit_label.config(text=self.schaltZeit.strftime("%H:%M"))

    def initialisiereZeitTemp(self, timeLabel, tempLabel):
        """Initialisiert Zeit und Temp update loops mit den gegeben labels"""
        self.zeitUpdate(timeLabel)
        self.tempUpdate(tempLabel)

    def vollbildToggle(self, event=None):
        """Aktiviert Vollbild falls nicht aktiv und deaktiviert ihn sonst. Der event Parameter wird von tkinter benoetigt."""
        # Umstellen des Boolean
        self.vollbild = not self.vollbild
        self.fenster.attributes("-fullscreen", self.vollbild)

    def vollbildBeenden(self, event=None):
        """Deaktiviert Vollbild"""
        self.vollbild = False
        self.fenster.attributes("-fullscreen", False)

    def vollbildStarten(self, event=None):
        """Aktiviert Vollbild"""
        self.vollbild = True
        self.fenster.attributes("-fullscreen", True)


#Fenster-Überschrift
windowTitle = "Sauna Timer"

# Fenster einrichten
control = kontroll_fenster()

# Groesse der Texte
beschreibungsText_size = 15

# Sollwert-Schieberegler erzeugen
schieberegeler_scale = Scale(
    control.fenster, font=("Arial", 15), from_=95, to=60, tickinterval=5, length=390, width=100, sliderlength=60, command=control.saveSoll)
schieberegeler_scale.set(control.sollTemp)

# Schalt-Zeit-Fenster einrichten und Soll-Zeit anzeigen
schaltZeitText_label = Label(control.fenster, font=("Arial", beschreibungsText_size),
                           text="Startzeit:")
schaltZeit_label = Label(control.fenster, font=("Arial", 35),
                       text=control.schaltZeit.strftime("%H:%M"))

# Zeitkontroll Buttons erzeugen
stdText_label = Label(control.fenster, font=("Arial", 12),
                      text="Stunden:")
minText_label = Label(control.fenster, font=("Arial", 12),
                      text="Minuten:")
stdUp_button = Button(control.fenster, font=("Arial", 28),
                      text="\u25b2", command=lambda: control.anpassungZeit(1, 0))
stdDown_button = Button(control.fenster, font=("Arial", 28),
                        text="\u25bc", command=lambda: control.anpassungZeit(-1, 0))
minUp_button = Button(control.fenster, font=("Arial", 13), height=1, width=6,
                      text="\u25b2", command=lambda: control.anpassungZeit(0, 1))
minDown_button = Button(control.fenster, font=("Arial", 13), height=1, width=6,
                        text="\u25bc", command=lambda: control.anpassungZeit(0, -1))
minUp5_button = Button(control.fenster, font=("Arial", 13), height=1, width=6,
                       text="\u25b2x5", command=lambda: control.anpassungZeit(0, 5))
minDown5_button = Button(control.fenster, font=("Arial", 13), height=1, width=6,
                         text="\u25bcx5", command=lambda: control.anpassungZeit(0, -5))

# Ist-Temperatur Text erzeugen
aktuelleTempText_label = Label(control.fenster,
                               font=("Arial", beschreibungsText_size), text="Temperatur:")
aktuelleTemp_label = Label(control.fenster, fg="blue4",
                           font=("Arial", 60), text=str(control.aktuelleTemp)+"\u00B0")

# Start und Stop Buttons erzeugen
start_button = Button(control.fenster, font=("Arial", 20), activebackground="green4", bg="green3",
                      relief=RAISED, text="Start", command=control.starten)
stop_button = Button(control.fenster, font=("Arial", 20), activebackground="firebrick4", bg="firebrick3",
                     relief=RAISED, text="Stop", command=control.ausschalten)

# Aktuelle Uhrzeit Text erzeugen
aktuelleZeitText_label = Label(control.fenster, font=("Arial", beschreibungsText_size),
                               text="Uhrzeit:")
aktuelleZeit_label = Label(control.fenster, font=("Arial", 35),
                           text=control.aktuelleZeit.strftime("%H:%M:%S"))

# Saunabilder laden
sauna_img = PhotoImage(file=os.path.join(OWN_PATH,"img/","sauna.png"))
sauna_warten_img = PhotoImage(file=os.path.join(OWN_PATH,"img/","sauna_warten.png"))
sauna_aktiv_img = PhotoImage(file=os.path.join(OWN_PATH,"img/","sauna_aktiv.png"))
# Canvas erstellen und das Bild in dem Canvas erstellen
sauna_canvas = Canvas(control.fenster, width=225, height=205)
sauna_canvas.create_image(5, 5, anchor=NW, image=sauna_img)

# Positionierung aller Elemente
schieberegeler_scale.place(x=0, y=0)
aktuelleTempText_label.place(x=170, y=3)
aktuelleTemp_label.place(x=170, y=30, width=125, height=125)

start_button.place(x=170, y=200, width=125, height=70)
stop_button.place(x=170, y=290, width=125, height=70)

schaltZeitText_label.place(x=375, y=3)
schaltZeit_label.place(x=365, y=60)

stdText_label.place(x=350, y=180)
minText_label.place(x=430, y=180)
stdUp_button.place(x=350, y=200)
minUp_button.place(x=430, y=240)
minUp5_button.place(x=430, y=200)
stdDown_button.place(x=350, y=285)
minDown_button.place(x=430, y=285)
minDown5_button.place(x=430, y=325)

aktuelleZeitText_label.place(x=630, y=3)
aktuelleZeit_label.place(x=580, y=60)

sauna_canvas.place(x=550, y=160)
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

# Startet den Loop, um die Zeit und Temperatur zu updaten mit den gegeben Labels
control.initialisiereZeitTemp(aktuelleZeit_label, aktuelleTemp_label)
# Startet den mainloop des Fensters, damit jegliche Updates(Tasten usw.) ausgefuehert werden
control.fenster.mainloop()
