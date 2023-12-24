# -*- coding: utf-8 -*-
"""Sauna Timer für Touchbildschirme
Programmiert für die Vechelder Sauna von Quirin und Dietmar
Frohe Weihnachten! 
"""

from tkinter import *
from datetime import datetime, timedelta
import os
import sys
import argparse
import sauna_kommunikation
import atexit

# Initialisiert den Argument Parser, welches Parameter aus der Kommandozeile ausliest
parser = argparse.ArgumentParser()
# Parameter "vollbild" wird als true gespeichert, wenn "--vollbild" bei der Ausfuehrung hinzugefuegt wird. Sonst ist es false
parser.add_argument('--vollbild', action='store_true',
                    help='Startet das Programm im Vollbildschirm-Modus')
# Speichert die Parameter in die "args" Variable
args = parser.parse_args()

# Konstanten
OWN_PATH = sys.path[0]
FONT_STANDARD = "Arial"
TEMP_MIN = 60
TEMP_MAX = 95
TEMP_UPDATE_INTERVAL = 1000  # Veränderung benötigt Anpassung aller Koordinaten!
BILDSCHIRM_DIMENSION = "800x480"

# Statustexte
TEXT_TEMPERATUR = "Temperatur:"
TEXT_SOLL_UHRZEIT = "Startzeit:"
TEXT_IST_UHRZEIT = "Uhrzeit:"
TEXT_WARTEN = "Warten auf Startzeit..."
TEXT_INAKTIV = "Timer nicht aktiv"
TEXT_REGELN = "Sauna wird geheizt!"
TEXT_GRAD = "\u00B0"
TEXT_HITZESTUFE = "Ofenleistung: "

# Helfer Funktion(en)
def canvasBildErsetzen(canvas, neues_bild):
    """Ersetzt ein Bild innerhalb eines Canvas"""
    canvas.delete('all')
    canvas.create_image(5, 5, anchor=NW, image=neues_bild)


class kontroll_fenster:
    """Kontrolliert alle Elemente innerhalb eines Fensters"""

    def __init__(self):
        # Hauptfenster
        self.fenster = Tk()
        # Zeit+Temperatur Variablen
        self.aktuelleZeit = datetime.now()
        self.schaltZeit = datetime.now()
        self.sollTemp = 0
        # Status Variablen
        self.timerAktiv = False         # Hilfsmarke geplant zum stoppen
        # Liest die Programm args aus, um den initialen Vollbild-Modus zu setzen
        self.vollbild = args.vollbild
        # Wird gesetzt, falls die
        self.deviceFile = ""

        self.sauna = sauna_kommunikation.sauna()
        # inits
        self.config()

    def config(self):
        """Konfiguriert das Fenster und sonst alles was keine einfach Variable ist"""
        # Metadaten des Fensters setzen
        self.fenster.title(windowTitle)
        self.fenster.geometry(BILDSCHIRM_DIMENSION)
        self.fenster.bind("<F11>", self.vollbildToggle)
        self.fenster.bind("<Escape>", self.vollbildBeenden)

        # Alle Information unter Minuten von der Schaltzeit entfernen
        self.schaltZeit = self.schaltZeit - \
            timedelta(seconds=self.schaltZeit.second,
                      microseconds=self.schaltZeit.microsecond)
        # Falls mit dem Vollbild arg gestartet wurde, Vollbild akitivieren
        if self.vollbild:
            self.vollbildStarten()
        self.initSoll()

    def initSoll(self):
        """alten Sollwert(Temperatur) aus Datei holen"""
        with open(os.path.join(OWN_PATH, "solltemp.ini"), "r+") as f:
            neueTemp = f.read()
            if neueTemp != "":
                self.sollTemp = float(neueTemp)
                # Der Sauna von dem Update der Temperatur Bescheid geben
                self.sauna.sollTemp = self.sollTemp

    def updateSoll(self, temp):
        """Soll-Temperatur updaten und speichern"""
        self.sollTemp = float(temp)
        # Der Sauna von dem Update der Temperatur Bescheid geben
        self.sauna.sollTemp = self.sollTemp
        schieberegelerText_label.config(text=str(temp)+TEXT_GRAD)
        # Neue Koordinaten des Reglers holen und den Text an diese Koordinaten anpassen
        newCoords = schieberegeler_scale.coords()
        schieberegelerText_label.place(x=newCoords[0]+50, y=newCoords[1]-17)
        # Speichern der neuen Temperatur in der .ini
        with open(os.path.join(OWN_PATH, "solltemp.ini"), "w+") as f:
            f.write(temp)

    def ausschalten(self):
        """"Stop-Taste gedrückt"""
        self.timerAktiv = False
        self.anpassungStatus(sauna_img, TEXT_INAKTIV, "blue4")
        self.sauna.stoppen()
        start_button.config(state=NORMAL)

    def starten(self):
        """Starten-Taste gedrückt"""
        if self.timerAktiv == True:
            return True
        self.timerAktiv = True
        self.anpassungStatus(
            sauna_warten_img, TEXT_WARTEN, "indian red")
        start_button.config(state=DISABLED)

    # nun gehts in die Hitze
    def regeln(self):
        """Initiert das regeln der Temperatur"""
        self.anpassungStatus(sauna_aktiv_img, TEXT_REGELN, "orange red")
        # hier nun das "Regel-Werk"!
        self.sauna.starten()

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
                if self.aktuelleZeit.strftime("%H:%M") == self.schaltZeit.strftime("%H:%M"): # sec. entfernt!
                    self.regeln()
        # Initialer Aufruf der Funktion
        update()

    def tempUpdate(self, tempLabel):
        """Gleiches Prinzip wie in zeitUpdate"""
        def update():
            # Temp updates
            tempLabel.config(text=str(int(self.sauna.aktuelleTemp))+TEXT_GRAD)
            tempLabel.after(TEMP_UPDATE_INTERVAL, update)
            # Hitzestufe update
            self.updateHitzestufe(self.sauna.stufenMerker)
        update()

    def anpassungZeit(self, hours, minutes):
        """Passt die Uhrzeit des sollTime labels relativ mit den gegeben Stunden und Minuten an"""
        self.schaltZeit = self.schaltZeit + \
            timedelta(hours=hours, minutes=minutes)
        schaltZeit_label.config(text=self.schaltZeit.strftime("%H:%M"))

    def anpassungStatus(self, neuesBild, neuerText, neueTempFarbe):
        """Wrapper Funktion, um alles was vom aussehen her sich bei einer Statusveränderung verändert anzupassen"""
        canvasBildErsetzen(sauna_canvas, neuesBild)
        statusText_label.config(text=neuerText)
        aktuelleTemp_label.config(fg=neueTempFarbe)

    def initialisiereZeitTemp(self, timeLabel, tempLabel):
        """Initialisiert Zeit und Temp update loops mit den gegeben labels"""
        self.zeitUpdate(timeLabel)
        self.tempUpdate(tempLabel)

    def vollbildToggle(self, event=None):
        """Aktiviert Vollbild falls nicht aktiv und deaktiviert ihn sonst. Der event Parameter wird von tkinter benötigt."""
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

    def updateHitzestufe(self, neueStufe):
        hitzeStufe_label.config(text=TEXT_HITZESTUFE+str(neueStufe))


#Fenster-Überschrift
windowTitle = "Sauna Timer"

# Fenster einrichten
control = kontroll_fenster()

@atexit.register
def shutdown():
    control.sauna.stoppen()
# Grösse der Texte
beschreibungsText_size = 18

# Sollwert-Schieberegler erzeugen
schieberegeler_scale = Scale(
    control.fenster, font=(FONT_STANDARD, 15), from_=TEMP_MAX, to=TEMP_MIN, tickinterval=5, length=390, width=100, sliderlength=60, command=control.updateSoll, showvalue=False)
schieberegeler_scale.set(control.sollTemp)

schieberegelerText_label = Label(control.fenster, font=(FONT_STANDARD+" bold", 18),
                                 text=str(schieberegeler_scale.get())+TEXT_GRAD)

# Schalt-Zeit-Fenster einrichten und Soll-Zeit anzeigen
schaltZeitText_label = Label(control.fenster, font=(FONT_STANDARD, beschreibungsText_size),
                             text=TEXT_SOLL_UHRZEIT)
schaltZeit_label = Label(control.fenster, font=(FONT_STANDARD, 35),
                         text=control.schaltZeit.strftime("%H:%M"))

# Zeitkontroll Buttons erzeugen
stdText_label = Label(control.fenster, font=(FONT_STANDARD, 12),
                      text="Stunden:")
minText_label = Label(control.fenster, font=(FONT_STANDARD, 12),
                      text="Minuten:")
stdUp_button = Button(control.fenster, font=(FONT_STANDARD, 28),
                      text="\u25b2", command=lambda: control.anpassungZeit(1, 0))
stdDown_button = Button(control.fenster, font=(FONT_STANDARD, 28),
                        text="\u25bc", command=lambda: control.anpassungZeit(-1, 0))
minUp_button = Button(control.fenster, font=(FONT_STANDARD, 13), height=1, width=6,
                      text="\u25b2", command=lambda: control.anpassungZeit(0, 1))
minDown_button = Button(control.fenster, font=(FONT_STANDARD, 13), height=1, width=6,
                        text="\u25bc", command=lambda: control.anpassungZeit(0, -1))
minUp5_button = Button(control.fenster, font=(FONT_STANDARD, 13), height=1, width=6,
                       text="\u25b2x5", command=lambda: control.anpassungZeit(0, 5))
minDown5_button = Button(control.fenster, font=(FONT_STANDARD, 13), height=1, width=6,
                         text="\u25bcx5", command=lambda: control.anpassungZeit(0, -5))

# Ist-Temperatur Text erzeugen
aktuelleTempText_label = Label(control.fenster,
                               font=(FONT_STANDARD, beschreibungsText_size), text=TEXT_TEMPERATUR)
aktuelleTemp_label = Label(control.fenster, fg="blue4",
                           font=(FONT_STANDARD, 60), text=str(control.sauna.aktuelleTemp)+TEXT_GRAD)

# Start und Stop Buttons erzeugen
start_button = Button(control.fenster, font=(FONT_STANDARD, 20), activebackground="green4", bg="green3",
                      relief=RAISED, text="Start", command=control.starten)
stop_button = Button(control.fenster, font=(FONT_STANDARD, 20), activebackground="firebrick4", bg="firebrick3",
                     relief=RAISED, text="Stop", command=control.ausschalten)

# Aktuelle Uhrzeit Text erzeugen
aktuelleZeitText_label = Label(control.fenster, font=(FONT_STANDARD, beschreibungsText_size),
                               text=TEXT_IST_UHRZEIT)
aktuelleZeit_label = Label(control.fenster, font=(FONT_STANDARD, 35),
                           text=control.aktuelleZeit.strftime("%H:%M:%S"))

# Statustext
statusText_label = Label(control.fenster, font=(FONT_STANDARD+"bold", 18),
                         text=TEXT_INAKTIV, width=18)

# Hitze-Stufe
hitzeStufe_label = Label(control.fenster, font=(FONT_STANDARD+"bold", 18),
                         text=TEXT_HITZESTUFE+"0", width=18)

# Saunabilder laden
sauna_img = PhotoImage(file=os.path.join(OWN_PATH, "img/", "sauna.png"))
sauna_warten_img = PhotoImage(file=os.path.join(
    OWN_PATH, "img/", "sauna_warten.png"))
sauna_aktiv_img = PhotoImage(file=os.path.join(
    OWN_PATH, "img/", "sauna_aktiv.png"))

# heatbar0_img = PhotoImage(file=os.path.join(
#     OWN_PATH, "img/", "heatbar0.png"))
# heatbar1_img = PhotoImage(file=os.path.join(
#     OWN_PATH, "img/", "heatbar1.png"))
# heatbar2_img = PhotoImage(file=os.path.join(
#     OWN_PATH, "img/", "heatbar2.png"))
# heatbar3_img = PhotoImage(file=os.path.join(
#     OWN_PATH, "img/", "heatbar3.png"))
# heatbar4_img = PhotoImage(file=os.path.join(
#     OWN_PATH, "img/", "heatbar4.png"))

# Canvas erstellen und das Bild in dem Canvas erstellen
sauna_canvas = Canvas(control.fenster, width=225, height=197)
sauna_canvas.create_image(5, 5, anchor=NW, image=sauna_img)

# Positionierung aller Elemente
beschreibungsTextY = 3
schieberegeler_scale.place(x=0, y=0)
schieberegelerText_label.place(x=130, y=345)

aktuelleTempText_label.place(x=180, y=beschreibungsTextY)
aktuelleTemp_label.place(x=185, y=30, width=125, height=125)

start_button.place(x=185, y=200, width=125, height=70)
stop_button.place(x=185, y=290, width=125, height=70)

schaltZeitText_label.place(x=375, y=beschreibungsTextY)
schaltZeit_label.place(x=362, y=60)

stdText_label.place(x=350, y=180)
minText_label.place(x=430, y=180)
stdUp_button.place(x=350, y=200)
minUp_button.place(x=430, y=240)
minUp5_button.place(x=430, y=200)
stdDown_button.place(x=350, y=285)
minDown_button.place(x=430, y=285)
minDown5_button.place(x=430, y=325)

aktuelleZeitText_label.place(x=630, y=beschreibungsTextY)
aktuelleZeit_label.place(x=580, y=60)

statusText_label.place(x=530, y=350)

hitzeStufe_label.place(x=200, y=400)

sauna_canvas.place(x=550, y=150)


# Startet den Loop, um die Zeit und Temperatur zu updaten mit den gegeben Labels
control.initialisiereZeitTemp(aktuelleZeit_label, aktuelleTemp_label)
# Startet den mainloop des Fensters, damit jegliche Updates(Tasten usw.) ausgefuehert werden
control.fenster.mainloop()
