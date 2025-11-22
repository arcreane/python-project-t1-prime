import random
from simulation.aircraft import Aircraft
from simulation.airport import Airport


class SimulationEngine:
    def __init__(self):
        self.aircrafts = []
        self.airport = Airport("IPSA-Tower", 400, 300, 270)  # Aéroport au centre
        self.score = 0
        self.time_elapsed = 0

        # --- CORRECTION 1 : On fait apparaître des avions tout de suite ! ---
        self.spawn_aircraft()
        self.spawn_aircraft()
        self.spawn_aircraft()

    def spawn_aircraft(self):
        """Génère un avion qui rentre DANS l'écran (Logique corrigée)."""
        callsign = f"AF{random.randint(100, 999)}"

        # On choisit un côté au hasard : 0=Gauche, 1=Droite, 2=Haut, 3=Bas
        side = random.randint(0, 3)

        if side == 0:  # Gauche -> Doit voler vers la droite (Est)
            x = 0
            y = random.randint(50, 550)
            heading = random.randint(45, 135)  # Entre Nord-Est et Sud-Est

        elif side == 1:  # Droite -> Doit voler vers la gauche (Ouest)
            x = 800
            y = random.randint(50, 550)
            heading = random.randint(225, 315)  # Entre Sud-Ouest et Nord-Ouest

        elif side == 2:  # Haut -> Doit voler vers le bas (Sud)
            x = random.randint(50, 750)
            y = 0
            heading = random.randint(135, 225)  # Vers le Sud

        else:  # Bas -> Doit voler vers le haut (Nord)
            x = random.randint(50, 750)
            y = 600
            heading = random.randint(315, 405)  # Vers le Nord

        # Création de l'avion
        new_plane = Aircraft(callsign, x, y, heading, speed=280, altitude=5000)
        self.aircrafts.append(new_plane)
        print(f"SPAWN: {callsign} en ({x}, {y}) Cap {heading}°")

    def update(self, dt: float):
        """Boucle principale de simulation"""
        self.time_elapsed += dt

        # Mise à jour des positions (sur une COPIE de la liste pour éviter les bugs de suppression)
        for plane in self.aircrafts[:]:
            plane.update_position(dt)

            # Vérification atterrissage
            if plane.landing_requested and self.airport.can_land(plane):
                plane.active = False
                self.score += 100
                self.aircrafts.remove(plane)
                print(f"{plane.callsign} Atterrissage réussi !")

            # Suppression si l'avion n'est plus actif (crash ou sorti de map si besoin)
            elif not plane.active:
                self.aircrafts.remove(plane)

        # [cite_start]Vérification collisions [cite: 29]
        self.check_collisions()

        # --- CORRECTION 2 : Spawn aléatoire ---
        # On augmente un peu la chance : 0.01 -> 0.02 (2% par frame)
        # Mais surtout, on vérifie si la liste est vide pour en remettre un tout de suite
        if len(self.aircrafts) == 0:
            self.spawn_aircraft()
        elif random.random() < 0.02:
            self.spawn_aircraft()

    def check_collisions(self):
        """Vérifie la distance entre tous les avions."""
        for i, p1 in enumerate(self.aircrafts):
            for p2 in self.aircrafts[i + 1:]:
                dist = ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
                # Si moins de 30 pixels et même altitude (à peu près)
                if dist < 30 and abs(p1.altitude - p2.altitude) < 300:
                    print(f"COLLISION DANGER: {p1.callsign} <-> {p2.callsign}")