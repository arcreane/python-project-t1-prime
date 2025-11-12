from .aircraft import Aircraft

class SimulationEngine:
    def __init__(self):
        self.aircrafts = [] # La liste de tous les avions en vol
        self.airports = []

    def add_test_aircraft(self):
        # Ajoute un avion de test pour démarrer
        ac1 = Aircraft(id="AF123", x=-500, y=-200, altitude=10000, speed=450, heading=90)
        self.aircrafts.append(ac1)

    def update(self):
        """
        La fonction appelée à chaque "tick" de l'horloge (timer).
        Elle met à jour la position de tous les objets.
        """
        for aircraft in self.aircrafts:
            aircraft.move()