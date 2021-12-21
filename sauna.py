from tkinter import *
from datetime import datetime, timedelta
import time
#from RPi import GPIO # geht NUR im Raspi!
import os

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
        self.sollZeit = datetime.now()
        self.aktuelleTemp = 0
        self.sollTemp = 0
        # Status Variablen
        self.timerAktiv = False         # Hilfsmarke geplant zum stoppen
        self.vollbild = False
        # Wird gesetzt, falls die
        self.deviceFile = ""
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

        # inits
        self.initDeviceFile()
        self.initSoll()

        self.fenster.bind("<F11>", self.vollbildToggle)
        self.fenster.bind("<Escape>", self.vollbildBeenden)

    def initSoll(self):
        # alten Sollwert(Temperatur) aus Datei holen
        # Pfad muß auf die Maschine angepasst werden!!
        # with open("/home/pi/temp.txt") as f:
        with open("solltemp.ini", "r+") as f:
            neueTemp = f.read()
            if neueTemp != "":
                self.sollTemp = float(neueTemp)

    def initDeviceFile(self):
        if os.path.isdir("/sys/bus/w1/devices"):
            for d in os.listdir("/sys/bus/w1/devices"):
                if d.startswith("10") or d.startswith("28"):
                    self.deviceFile = "/sys/bus/w1/devices/" + d + "/w1_slave"

    # gültige Soll-Temperatur für später sichern.
    def saveSoll(self, temp):
        self.sollTemp = temp
        with open("solltemp.ini", "w+") as f:
            f.write(temp)

    # Stop-Taste gedrückt.
    def ausschalten(self):
        self.timerAktiv = False
        curTemp_label.config(bg="blue", fg="red")
        canvasBildErsetzen(sauna_canvas, sauna_img)

    # Start-Taste gedrückt!
    def starten(self):
        self.timerAktiv = True
        curTemp_label.config(bg="green", fg="red")
        canvasBildErsetzen(sauna_canvas, sauna_aktiv_img)

    # nun gehts in die Hitze
    def regeln(self):
        print("nun soll geregelt werden")
        # hier nun das "Regel-Werk"!

    def zeitUpdate(self, timeLabel):
        # Funktion, die immer wieder aufgerufen wird, um die Zeitanzeige zu updaten
        def update():
            # Zeit updates
            self.aktuelleZeit = datetime.now()
            timeLabel['text'] = self.aktuelleZeit.strftime("%H:%M:%S")
            # Nach 1000ms diese Funktion wieder aufrufen
            timeLabel.after(1000, update)
            # Falls der Timer am laufen ist mit der Soll-Zeit vergleichen und wenn gleich regeln
            if self.timerAktiv:
                if self.aktuelleZeit.strftime("%H:%M:%S") == self.sollZeit.strftime("%H:%M:%S"):
                    self.regeln()
        # Initialer Aufruf der Funktion
        update()

    def tempUpdate(self, tempLabel):
        # Gleiches Prinzip wie in timeUpdate
        def update():
            # Temp updates
            if os.path.isfile(self.deviceFile):
                first, second = ""
                while first.find("YES") == -1:
                    with open(self.deviceFile) as f:
                        first, second = f.readlines()
                tempString = second.split("=")[1]
                tempLabel['text'] = str(int(tempString)/1000)
            tempLabel.after(3000, update)
        update()

    # Passt die Uhrzeit des sollTime labels relativ mit den gegeben Stunden und Minuten an
    def anpassungZeit(self, hours, minutes):
        self.sollZeit = self.sollZeit+timedelta(hours=hours, minutes=minutes)
        sollTime_label.config(text=self.sollZeit.strftime("%H:%M"))

    # Initialisiert Zeit und Temp update loops mit den gegeben labels
    def initialisiereZeitTemp(self, timeLabel, tempLabel):
        self.zeitUpdate(timeLabel)
        self.tempUpdate(tempLabel)

    def vollbildToggle(self, event=None):
        self.vollbild = not self.vollbild  # Just toggling the boolean
        self.fenster.attributes("-fullscreen", self.vollbild)
        return "break"

    def vollbildBeenden(self, event=None):
        self.vollbild = False
        self.fenster.attributes("-fullscreen", False)
        return "break"


#Fenster-Überschrift
windowTitle = "Sauna Timer"

# Fenster einrichten
control = kontroll_fenster()
control.fenster.title(windowTitle)
control.fenster.geometry("800x400")

# Groesse der Texte
beschreibungsText_size = 15

# Sollwert-Schieberegler einrichten
schieberegeler_scale = Scale(
    control.fenster, from_=95, to=60, tickinterval=5, length=390, width=100, sliderlength=60, command=control.saveSoll)
schieberegeler_scale.set(control.sollTemp)
# soll_button = Button(control.fenster, font=("arial", 16),
#                      text='Soll-Temp', command=lambda: saveSoll(soll_button))
# soll_button.grid(column=0, row=4)
# bei Klick: neue Temperatur übernehmen

# Schalt-Zeit-Fenster einrichten und Soll-Zeit anzeigen
sollTime_text = Label(control.fenster, font=("Arial", beschreibungsText_size),
                      text="Startzeit:")
sollTime_label = Label(control.fenster, font=("Arial", 25),
                       text=control.sollZeit.strftime("%H:%M"))

#
std_up_but = Button(control.fenster, font=("Arial", 20),
                    text="\u25b2", command=lambda: control.anpassungZeit(1, 0))
std_down_but = Button(control.fenster, font=("Arial", 20),
                      text="\u25bc", command=lambda: control.anpassungZeit(-1, 0))
min_up_but = Button(control.fenster, font=("Arial", 20),
                    text="\u25b2", command=lambda: control.anpassungZeit(0, 1))
min_down_but = Button(control.fenster, font=("Arial", 20),
                      text="\u25bc", command=lambda: control.anpassungZeit(0, -1))

# Ist-Temperatur-Fenster erzeugen
curTemp_text = Label(control.fenster,
                     font=("Arial", beschreibungsText_size), text="Temperatur:")
#plazierung in anderer Zeile definieren, damit die Funktion nicht Grid aufruft
curTemp_label = Label(control.fenster, bg="blue", fg="red",
                      font=("Arial", 40), text=control.aktuelleTemp)
#plazierung in anderer Zeile definieren, damit die Funktion nicht Grid aufruft

start_button = Button(control.fenster, font=("Arial", 20), bg="green",
                      relief="sunken", text="Start", command=control.starten)
stop_button = Button(control.fenster, font=("Arial", 20), bg="red",
                     relief="sunken", text="Stop", command=control.ausschalten)

# Uhr-Fenster einrichten und Lokalzeit anzeigen
curTime_text = Label(control.fenster, font=("Arial", beschreibungsText_size),
                     text="Uhrzeit:")
curTime_label = Label(control.fenster, font=("Arial", 25),
                      text=control.aktuelleZeit.strftime("%H:%M:%S"))

sauna_img = PhotoImage(file='sauna.png')
sauna_aktiv_img = PhotoImage(file='sauna_aktiv.png')
sauna_canvas = Canvas(control.fenster, width=225, height=205)
sauna_canvas.create_image(5, 5, anchor="nw", image=sauna_img)

schieberegeler_scale.place(x=0, y=0)
curTemp_text.place(x=170, y=3)
curTemp_label.place(x=170, y=50, width=125, height=125)

start_button.place(x=170, y=200, width=125, height=70)
stop_button.place(x=170, y=285, width=125, height=70)

sollTime_text.place(x=375, y=3)
sollTime_label.place(x=375, y=50)

std_up_but.place(x=360, y=190)
std_down_but.place(x=360, y=260)
min_up_but.place(x=430, y=190)
min_down_but.place(x=430, y=260)

curTime_text.place(x=630, y=3)
curTime_label.place(x=600, y=50)

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
control.initialisiereZeitTemp(curTime_label, curTemp_label)
# Startet den mainloop des Fensters, damit jegliche Updates(Tasten usw.) ausgefuehert werden
control.fenster.mainloop()
