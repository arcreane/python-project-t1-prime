import random
from .aircraft import Aircraft
from .airport import Airport


class SimulationEngine:
    def __init__(self):
        self.aircrafts = []
        self.airport = Airport("IPSA-Tower", 400, 300, 270)  # Aéroport au centre
        self.score = 0
        self.time_elapsed = 0

    def spawn_aircraft(self):
        """Génère un avion aléatoire (Gamification: difficulté croissante)"""
        # [cite: 33]
        callsign = f"AF{random.randint(100, 999)}"
        # Apparition sur les bords
        x = random.choice([0, 800])
        y = random.randint(0, 600)
        heading = random.randint(0, 360)

        new_plane = Aircraft(callsign, x, y, heading, speed=400, altitude=5000)
        self.aircrafts.append(new_plane)

    def update(self, dt: float):
        """Boucle principale de simulation"""
        self.time_elapsed += dt

        # Mise à jour des positions
        for plane in self.aircrafts:
            plane.update_position(dt)

            # Vérification atterrissage
            if plane.landing_requested and self.airport.can_land(plane):
                plane.active = False
                self.score += 100
                self.aircrafts.remove(plane)
                print(f"{plane.callsign} Atterrissage réussi !")

        # Vérification collisions [cite: 29]
        self.check_collisions()

        # Spawn aléatoire
        if random.random() < 0.01:  # 1% de chance par frame
            self.spawn_aircraft()

    def check_collisions(self):
        """Vérifie la distance entre tous les avions."""
        for i, p1 in enumerate(self.aircrafts):
            for p2 in self.aircrafts[i + 1:]:
                dist = ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
                # Si moins de 30 pixels et même altitude (à peu près)
                if dist < 30 and abs(p1.altitude - p2.altitude) < 300:
                    print(f"COLLISION DANGER: {p1.callsign} <-> {p2.callsign}")
                    # Ici on pourrait déduire des points ou arrêter le jeu