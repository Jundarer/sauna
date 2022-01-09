from time import *
from RPi import GPIO

Heizein = 3 # erstes Anheizen mit +3° !
stufenMerker = 4 # volle Leistung

def Firstloop():
    while Heizein:
        sleep(10)
        if aktuelleTemp - sollTemp >= 3: # heizen bis 3° über Solltemperatur
            Heizein = 0


def setport(): # erwartet 'MERKER'
    for i in Rel_out:
        GPIO.output(i, (leistungsStufe(stufenMerker)))


def hoch():
    if stufenMerker < 4:  # bei '4' nix höher!
        stufenMerker = stufenMerker + 1
    setport()


def runter():
    if stufenMerker > 0:   # bei '0' nix tiefer
        stufenMerker = stufenMerker - 1
    setport()


def erhöhen():
    if (oldtemp < aktuelleTemp) and aktuelleTemp < sollTemp:
        hoch()           # fallend und (IST<SOLL)
    if oldtemp > aktuelleTemp and aktuelleTemp < (solltem - 3):
        hoch()           # steigend und IST<SOLL-3
    if  aktuelleTemp < (sollTemp - 1.5):
        runter()         # Diff. < -1,5°, steigend, dann einen runter


def vermindern():
    if oldtemp < aktuelleTemp:
        runter()         # steigend über SOLL
    if (oldtemp > aktuelleTemp) and (aktuelleTemp > (sollTemp + 1)):
        runter()         # fallend und IST>SOLL+1
    else:
        hoch()           # fallend und IST<SOLL+1
        
setport()


def regeln1():
    if Heizein:          # solange im ersten Lauf aktTmp-Solltmp < 3
        Firstloop()      # hier getestet

    if Heizein:
        regeln1()            # in sich selbst kreiseln!
    if aktuelleTemp - sollTemp >= 2:
        stufenMerker = 0     # bei mehr als 2° + sofort aus
        setport()
    if sollTemp - aktuelleTemp >= 5:
        stufenMerker = 4     # bei mehr als 5° - sofort volle Leistung
        setport()
    if aktuelleTemp < (sollTemp - 0.5):
        erhöhen()            # wenn IST < (SOLL -0,5°)

    if aktuelleTemp < (sollTemp + 0.5):
        vermindern()         # ähnlich oben
regeln1()

