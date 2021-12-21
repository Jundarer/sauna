from tkinter import *
from time import *
from threading import Thread
# from RPi import GPIO # geht NUR im Raspi!
import os

# nur für die erste Definition
global StarMark, Stunde, Minute, Uhrzeit, msg2_tst
global Einschalten, StUhrzeit, stopMark


Ist = 56               # Dummy aktuelle Temperatur
ist = str(Ist)         # Dummy dito als String
Minute = "00"          # Dummy 
Stunde = "00"          # Dummy
StMinute = "00"        # Dummy Startminute
StStunde = "00"        # Dummy Startstunde
Uhrzeit = "00:00:00"   # Dummy aktuelle Uhrzeit
StUhrzeit = StStunde + ":" + StMinute # Dummy Startuhrzeit
runmark = True         # Hilfsmarke geplant zum stoppen
Einschalten = False    # Startzeit != Uhrzeit
StarMark = False       # Start-Taste noch nicht gedrückt
stopMark = False       # Stop-Taste nicht gedrückt
hilfmk = False         # Uhrzeit noch nicht gesetzt
msg2_tst = False       # Test-Marker: Startzeit noch nicht klar
Rel_out = (31, 33, 35, 37) # GPIO-Pins (N, R, S, T)
#Def. Leistungs-Stufen
kw0 = (0, 0, 0, 0)
kw1 = (0, 0, 1, 1)
kw2 = (1, 0, 0, 1)
kw3 = (1, 0, 1, 1)
kw4 = (1, 1, 1, 1)
Leistungs_stufe = (kw0, kw1, kw2, kw3, kw4)
Stufen_merker = 0

#  auskommentiert, geht nur im raspi!
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
#for d in os.listdir("/sys/bus/w1/devices"):
#    if d.startswith("10") or d.startswith("28"):
#        deviceFile = "/sys/bus/w1/devices/" + d + "/w1_slave"

# alten Sollwert(Temperatur) aus Datei holen
# file = open("/home/josef/Desktop/solltemp.txt", "r") # MX
# #file = open("/home/pi/temp.txt", "r") # raspi
# # Pfad muß auf die Maschine angepasst werden!!
# Soll = file.read()
# file.close()


# gültige Soll-Temperatur für später sichern. 
def save_Soll():
    global Soll, soll
    Soll=(w.get())
    soll=str(Soll)
# Pfad muß auf die Maschine angepasst werden!!
    file = open("/home/josef/Desktop/solltemp.txt", "w") # MX
#    file = open("/home/pi/solltemp.txt", "w") # raspi
    file.write(soll)
    file.close()
    
# Stop-Taste gedrückt. Wirkung dieser Routine noch nicht getestet!!!
def ausschalten():
    global runmark, Einschalten, StarMark, hilfmk, msg2_tst, stopoMark
    stopMark = True
    runmark = True
    Einschalten = False 
    StarMark = False 
    hilfmk = False
    msg2_tst = False
    Ist_temp.config(bg="blue", fg="red")
    print("gestoppt")

# Start-Taste gedrückt!
def StarMarkSet():
    global StarMark, stopMark
    stopMark = False
    StarMark = True
    Ist_temp.config(bg="green", fg="red")

    
# nun gehts in die Hitze
def regeln():
    print("nun soll geregelt werden") #Ausgabe anstelle des Regelwerks!!
    # hier nun das "Regel-Werk"!


# erzeugen der 'Start-Uhrzeit'
def Uhr_string():
    global StStunde, StMinute, StUhrzeit
    if len(StStunde) == 1:
        StStunde = "0" + StStunde
    if len(StMinute) == 1:
        StMinute = "0" + StMinute
    StUhrzeit = StStunde + ":" + StMinute
    msg2.config(text=StUhrzeit)
    

# Startzeit festlegen
# Stunde   
def std_up():
    global StStunde, StMinute
    st = int(StStunde)
    if st < 23:
        st += 1
        StStunde = str(st)
        Uhr_string()
# auf 0 zurück setzen falls bei 23
    else:
        st=0
        StStunde = str(st)
        Uhr_string()
   
def std_down():
    global StStunde, StMinute
    st = int(StStunde)
    if st > 0:
        st -=1
        StStunde = str(st)
        Uhr_string()
# wenn '0', dann 23!
    else:
        st =23
        StStunde = str(st)
        Uhr_string()
    
    
def min_up():
    global StStunde, StMinute
    Min = int( StMinute)
    if Min < 59:
        Min += 1
        StMinute = str(Min)
        Uhr_string()
    else:
        Min = 0
        StMinute = str(Min)
        Uhr_string()
        
def min_down():
    global StMinute, StStunde
    Min = int(StMinute)
    if Min > 0:
        Min -= 1
        StMinute = str(Min)
        Uhr_string()
    else:
        Min = 59
        StMinute = str(Min)
        Uhr_string()


# Eigentliche Hauptroutine. Zeit abfragen und für diverse Zwecke aufbereiten
# Einschalten, Steuern u.s.w
def checkTime():
    global runmark, hilfmk, msg2_tst, Uhrzeit, StUhrzeit, StMinute, StStunde
    global StarMark, Einschalten, tempString, stopMark, deviceFile
    if stopMark == True:
        return()
    while runmark == True:
        #Uhrzeit einrichten
        t = localtime()
        Stunde = str(t.tm_hour)
        if len(Stunde) < 2:
            Stunde = "0" + Stunde
        Minute = str(t.tm_min)
        if len(Minute) < 2:
            Minute = "0" + Minute
        Sekunde = str(t.tm_sec)
        if len(Sekunde) < 2:
            Sekunde = "0" + Sekunde
        if stopMark == True:  # StUhrzeit auf akt. Zeit setzen
            StUhrzeit = Stunde + ":" + Minute
        hilfsuhr = Stunde + ":" + Minute
        Uhrzeit = hilfsuhr + ":" + Sekunde  # mit Sekunde
        msg1.config(text=Uhrzeit)           # -> in die Anzeige
        if msg2_tst == False:
            StMinute = Minute
            StStunde = Stunde
            StUhrzeit = Stunde + ":" + Minute # Std + Minute als Schaltzeit
            msg2.config(text=StUhrzeit)
            if StarMark == True:
                msg2_tst = True
        if StarMark == True and Einschalten == False:
            if StUhrzeit == hilfsuhr: # warten auf Schaltzeit                
                Einschalten = True      # dann einschalten
                print("einschalten") # für test OHNE Regelwerk!!
        if StarMark == True and Einschalten == True:                
            regeln()
        # Temperatur abragen (NUR im PI möglich)
        #ok = False
        #while not ok :
        #    f = open(deviceFile, "r")
        #    first, second = f.readlines()
        #    f.close
        #    if first.find("YES") != -1:
        #        ok = True
        #tempString = second.split("=")[1]
        #Ist = int(tempString)/1000
        #ist = str(int(Ist))
        #Ist_temp.config(text=ist)
        #print (ist) # für test OHNE Regelwerk!!
        
            
        sleep(5)   

fenster = Tk()
fenster.title("Sauna")
fenster.config (width=800, height=480)


# Sollwert-Schieberegler einrichten
w = Scale(fenster, from_=95, to=60, length=240, tickinterval=5)
# w.set(Soll)
w.place(x=650, y=20, width=160, height=330)
##w.grid(column=0, row=0, rowspan=3)
Soll_Button = Button(fenster, font=("arial",16),
      text='Soll-Temp', command = save_Soll)
Soll_Button.place(x=650, y=360)
##Soll_Button.grid(column=0, row=3)
      # bei Klick: neue Temperatur übernehmen    

# Ist-Temperatur-Fenster erzeugen
Ist_temp = Message(fenster, bg="blue", fg="red", font=("Arial",45),text=(ist))
#plazierung in anderer Zeile definieren, damit die Funktion nicht Grid aufruft
##Ist_temp.grid(column=1, row=0, rowspan=2, columnspan=2)
Ist_temp.place(x=50, y=50, width=150, heigh=150)

start_button = Button(fenster, font=("Arial",20), bg="green",
                      relief="sunken", text="Start", command = (StarMarkSet))
start_button.place(x=60, y=250, width=130, heigh=80)
##start_button.grid(column=1, row=2, columnspan=2)
stop_button = Button(fenster, font=("Arial",20), bg="red",
                     relief="sunken", text="Stop", command = (ausschalten))
stop_button.place(x=60, y=350, width=130, heigh=80)
##stop_button.grid(column=1, row=3, columnspan=2)


# Uhr-Fenster einrichten und Lokalzeit anzeigen
msg1 = Message(fenster, bd=50, font=("Arial",30), text=Uhrzeit)
msg1.place(x=240, y=50, width=160, heigh=150)
##msg1.grid(column=3, row=0, rowspan=2, columnspan=2)


# Schalt-Zeit-Fenster einrichten und Soll-Zeit anzeigen
msg2=Message(fenster, font=("Arial",30), text=StUhrzeit)
msg2.place(x=420, y=50, width=200, heigh=150)
##msg2.grid(column=5, row=0, rowspan=2, columnspan=2)
std_up_but = Button(fenster, font=("Arial",20), text="\u25b2", command = (std_up))
std_up_but.place(x=475, y=200, width=48, heigh=48)
##std_up_but.grid(column=5, row=2)
std_down_but = Button(fenster, font=("Arial",20), text="\u25bc", command = (std_down))
std_down_but.place(x=475, y=250, width=48, heigh=48)
##std_down_but.grid(column=5, row=3)
min_up_but = Button(fenster, font=("Arial",20), text="\u25b2", command = (min_up))
min_up_but.place(x=525, y=200, width=48, heigh=48)
##min_up_but.grid(column=6, row=2)
min_down_but = Button(fenster, font=("Arial",20), text="\u25bc", command = (min_down))
min_down_but.place(x=525, y=250, width=48, heigh=48)
##min_down_but.grid(column=6, row=3)


t = Thread(target=checkTime, args=())
t.daemon=True
t.start()
mainloop()
#fenster.destroy()
