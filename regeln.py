from time import *
from RPi import GPIO

Heizein = 3 # erstes Anheizen mit +3° !
stufenMerker = 4 # volle Leistung

def Firstloop():
    while Heizein:
        sleep(10)
        if aktuelleTemp - sollTemp >= 3:
            Heizein = 0

def setport(): # erwartet 'MERKER'
    for i in Rel_out:
        GPIO.output(i, (leistungsStufe(stufenMerker)))

setport()
def regeln1():
    if Heizein:          # solange im ersten Lauf aktTmp-Solltmp < 3
        Firstloop() # hier getestet
if Heizein:
    regeln1()       # in sich selbst kreiseln!
if aktuelleTemp - sollTemp < 2:

    for i in Rel_out:
        GPIO.output(i, False)
    
