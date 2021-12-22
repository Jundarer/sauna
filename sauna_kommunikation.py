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
    
    def starten(self, aktuelleTemp, sollTemp):
        print("Sauna startet mit dem Ziel {} Grad".format(sollTemp))
    
    def stoppen(self):
        print("Sauna gestoppt!")