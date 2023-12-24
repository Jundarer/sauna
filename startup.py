#!/usr/bin/env python3
import os
try:
    from RPi import GPIO
except (ImportError, RuntimeError) as e:
    print("Could not find GPIO module. Exiting...")
    os.sleep(1)
    exit()
# GPIO Variablen
Rel_out = (31, 33, 35, 37)  # GPIO-Pins (N, R, S, T)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for i in Rel_out:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, True)  # Am Anfang alles auf Null!
                            # nun sind die out-pins konfiguriert!
                            # Ermitteln des Temperatur-Files (Seite 315) gilt NUR für den PI!
                            # und der Sensor MUSS angeschlossen sein!
os.system("modprobe wire")      # modprobe nicht nötig
os.system("modprobe w1-gpio")   # ist in boot-config festgelegt
os.system("modprobe w1-therm")