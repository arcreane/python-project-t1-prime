import random
from simulation.aircraft import Aircraft
from simulation.airport import Airport


class SimulationEngine:
    def __init__(self):
        self.aircrafts = []
        self.airport = Airport("IPSA-Tower", 400, 300, 270)
        self.score = 0
        self.time_elapsed = 0

        # Difficulté
        self.max_aircraft_limit = 20
        self.spawn_interval = 15

        # Spawn initial
        for _ in range(3):
            self.spawn_aircraft()

    def spawn_aircraft(self):
        """Génère un avion qui rentre DANS l'écran."""
        callsign = f"AF{random.randint(100, 999)}"
        side = random.randint(0, 3)

        if side == 0:  # Gauche
            x, y, heading = 0, random.randint(50, 550), random.randint(45, 135)
        elif side == 1:  # Droite
            x, y, heading = 800, random.randint(50, 550), random.randint(225, 315)
        elif side == 2:  # Haut
            x, y, heading = random.randint(50, 750), 0, random.randint(135, 225)
        else:  # Bas
            x, y, heading = random.randint(50, 750), 600, random.randint(315, 405)

        new_plane = Aircraft(callsign, x, y, heading, speed=280, altitude=5000)
        self.aircrafts.append(new_plane)
        print(f"SPAWN: {callsign} (Total: {len(self.aircrafts)})")

    def update(self, dt: float):
        """Boucle principale de simulation"""
        self.time_elapsed += dt

        # 1. Gestion du nombre d'avions
        allowed_planes = 3 + int(self.time_elapsed / self.spawn_interval)
        if allowed_planes > self.max_aircraft_limit: allowed_planes = self.max_aircraft_limit

        if len(self.aircrafts) < allowed_planes and random.random() < 0.02:
            self.spawn_aircraft()

        # 2. Mise à jour PHYSIQUE
        for plane in self.aircrafts[:]:

            # --- PILOTE AUTOMATIQUE ---
            if plane.landing_requested:
                plane.speed = 200

                dist_to_airport = ((self.airport.x - plane.x) ** 2 + (self.airport.y - plane.y) ** 2) ** 0.5
                diff_y = self.airport.y - plane.y
                diff_x = self.airport.x - plane.x

                # Approche initiale (non aligné)
                if abs(diff_y) > 5:
                    plane.heading = 180 if diff_y > 0 else 360

                # Phase finale (aligné)
                else:
                    plane.heading = 90 if diff_x > 0 else 270

                    # Plan de descente (Glide Slope)
                    target_altitude = dist_to_airport * 6.0
                    plane.altitude = min(plane.altitude, target_altitude)

                    # CORRECTION : Si on est très très proche (< 10px), on force 0 pour l'affichage
                    if dist_to_airport < 10:
                        plane.altitude = 0.0

            # Déplacement
            plane.update_position(dt)

            # 3. Vérification atterrissage
            dist_final = ((self.airport.x - plane.x) ** 2 + (self.airport.y - plane.y) ** 2) ** 0.5

            # CORRECTION : On réduit la tolérance de 20 à 5 pixels
            # L'avion doit être quasiment PILE sur la tour pour disparaître
            if plane.landing_requested and plane.altitude == 0 and dist_final < 5:
                plane.active = False
                self.score += 100
                self.aircrafts.remove(plane)
                print(f"{plane.callsign} ATTERRI ! Score: {self.score}")

            elif not plane.active:
                self.aircrafts.remove(plane)

        # 4. Collisions
        self.check_collisions()

    def check_collisions(self):
        """Gestion des alertes et crashs"""
        for p in self.aircrafts:
            p.warning = False

        crashes = []
        for i, p1 in enumerate(self.aircrafts):
            for p2 in self.aircrafts[i + 1:]:
                dist = ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
                alt_diff = abs(p1.altitude - p2.altitude)

                if dist < 80 and alt_diff < 400:
                    p1.warning = True
                    p2.warning = True
                    if dist < 20:
                        if p1 not in crashes: crashes.append(p1)
                        if p2 not in crashes: crashes.append(p2)

        for p in crashes:
            if p in self.aircrafts:
                p.active = False
                self.aircrafts.remove(p)
                self.score -= 500
                print(f"CRASH : {p.callsign}")